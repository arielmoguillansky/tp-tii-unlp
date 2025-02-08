from flask import (
    Flask,
    request,
    Response,
    abort,
    jsonify,
)
import requests
from flaskr.db import get_db
from datetime import datetime
from pykeen.triples import TriplesFactory
import pandas as pd
import torch
import logging
import sys
import os
import redis
import time

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

LIMITER_URL = os.getenv("LIMITER_URL", "http://localhost:6000")

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

app = Flask(__name__)


model = torch.load("trained_model.pkl", weights_only=False, map_location=torch.device('cpu'))
triples_file = "dataset_train.tsv.gz"
triples_factory = TriplesFactory.from_path(triples_file, create_inverse_triples=True)

triples_factory.relation_to_id["http://www.w3.org/2002/07/owl#sameAs"]

df = pd.read_csv(triples_file, sep="\t", header=None, names=["head", "relation", "tail"])

def is_valid_entity(entity):
    return "pronto.owl#space_site" in entity and len(entity.split("#")[1].split("_")) == 3


@app.route("/healthcheck")
def healthcheck():
    return "Predictor Server healthy"

@app.route("/predict", methods=["POST"])
def predict():
    if request.method == "POST":
        start_time = time.time()
        try:
            limiter_response = requests.get(f"{LIMITER_URL}/check_limit")
            limiter_data = limiter_response.json()

            if not limiter_data.get("allowed"):
                return jsonify(limiter_data), 429
        
        except requests.exceptions.RequestException as e:
            return jsonify({"allowed": False, "error": f"Error contacting limiter service: {e}"})
        
        heads = []
        error = None
        entity_urls = request.json.get("entity_payload")

        if not entity_urls:
            return jsonify({"allowed": False, "error": "Debe proporcionar urls o ids de entidades válidas."}), 500

        for entity in entity_urls:
            if isinstance(entity, int):
                if not entity in df["head"].index:
                    error = (f"Entidad {entity} inválida.")
                entity_url = df["head"][entity]
                if not is_valid_entity(entity_url):
                    error = (f"Entidad {entity} inválida.")
                heads.append(entity_url)

            if isinstance(entity, str): 
                head_exists = entity in df["head"].values
                if not head_exists or not is_valid_entity(entity):
                    raise Exception(f"Entity {entity} not valid.")
                heads.append(entity)

        if error:
            return jsonify({"allowed": False, "error": error}), 500

        relations = ['http://www.w3.org/2002/07/owl#sameAs'] * len(heads)

        heads_idx = [triples_factory.entity_to_id[head] for head in heads]
        relations_idx = [triples_factory.relation_to_id[relation] for relation in relations]

        hr_batch = torch.tensor(list(zip(heads_idx, relations_idx)))

        sample = hr_batch[:len(heads)]

        torch.cuda.empty_cache()
        scores = model.score_t(sample)

        end_time = time.time()
        execution_time = end_time - start_time

        top_scores, top_indices = torch.topk(scores, 10, largest=False)
        result = {"scores":top_scores.tolist(), "indexes":top_indices.tolist()}
        get_db().request_log.insert_one({"user_id": redis_client.hget("user","oid"), "timestamp": datetime.now().isoformat(), "params": entity_urls, "response": result, "execution_time": execution_time})  
        return jsonify({"allowed": True, "response": result}), 200
