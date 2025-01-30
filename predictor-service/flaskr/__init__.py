from flask import (
    Flask,
    request,
    Response,
    abort,
    jsonify,
)
from flaskr.db import get_db
from datetime import datetime
from pykeen.triples import TriplesFactory
import pandas as pd
import torch
from bson.json_util import dumps

model = torch.load("trained_model.pkl", weights_only=False, map_location=torch.device('cpu'))
triples_file = "dataset_train.tsv.gz"
triples_factory = TriplesFactory.from_path(triples_file, create_inverse_triples=True)

triples_factory.relation_to_id["http://www.w3.org/2002/07/owl#sameAs"]

df = pd.read_csv(triples_file, sep="\t", header=None, names=["head", "relation", "tail"])

def is_valid_entity(entity):
    return "pronto.owl#space_site" in entity and len(entity.split("#")[1].split("_")) == 3


def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=True)

    @app.route("/healthcheck")
    def healthcheck():
        return "Server healthy"

    @app.route("/predict", methods=["POST"])
    def predict():
        user_id = request.headers.get("X-User-ID")
        user_type = request.headers.get("X-User-Type")

        if not user_id or not user_type:
            abort(400, description="Missing user ID or user type")

        limiter_response = requests.post("http://localhost:6000/check_limit", json={"user_id": user_id, "user_type": user_type})

        if limiter_response.status_code == 429:
            abort(429, description="Rate limit exceeded. Try again later.")

        if limiter_response.status_code != 200:
            abort(500, description="Rate limiter service error.")

        heads = []
        error = None
        entity_urls = request.json.get("entity_urls")

        if not entity_urls:
            abort(404, description="Debe proporcionar urls o ids de entidades válidas.")

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
            abort(404, description=error)

        relations = ['http://www.w3.org/2002/07/owl#sameAs'] * len(heads)

        heads_idx = [triples_factory.entity_to_id[head] for head in heads]
        relations_idx = [triples_factory.relation_to_id[relation] for relation in relations]

        hr_batch = torch.tensor(list(zip(heads_idx, relations_idx)))

        sample = hr_batch[:len(heads)]

        torch.cuda.empty_cache()
        scores = model.score_t(sample)

        top_scores, top_indices= torch.topk(scores, 10, largest=False)
        result = {"scores":top_scores.tolist(), "indexes":top_indices.tolist()}
        get_db().request_log.insert_one( 
            {
                "timestamp": datetime.now().isoformat(),
                "params": entity_urls,
                "response": result
            }
        )
        return jsonify(result)
        
    @app.route('/requests',methods=['GET', 'POST'])
    def requests():
        result=get_db().request_log.find()
        # se convierte el cursor a una lista
        list_cur = list(result)         
        # se serializan los objetos
        json_data = dumps(list_cur, indent = 2)  
        #retornamos la lista con los metadatos adecuados
        return Response(json_data,mimetype='application/json')

    return app
