from pykeen.pipeline import pipeline
from pykeen.triples import TriplesFactory
import pandas as pd
import torch
import numpy as np

def is_valid_entity(entity):
    return "pronto.owl#space_site" in entity and len(entity.split("#")[1].split("_")) == 3

model = torch.load("trained_model.pkl", weights_only=False, map_location=torch.device('cpu'))
triples_file = "dataset_train.tsv.gz"
triples_factory = TriplesFactory.from_path(triples_file, create_inverse_triples=True)

triples_factory.relation_to_id["http://www.w3.org/2002/07/owl#sameAs"]

df = pd.read_csv(triples_file, sep="\t", header=None, names=["head", "relation", "tail"])

# heads = df[list(map(lambda x: True if ("pronto.owl#space_site" in x) and (len(x.split("#")[1].split("_")) == 3) else False, df["head"].values))]["head"].values

entity_urls = ["https://raw.githubusercontent.com/jwackito/csv2pronto/main/ontology/pronto.owl#space_site2_A1579031724", "https://raw.githubusercontent.com/jwackito/csv2pronto/main/ontology/pronto.owl#space_site1_12582408",100000]

heads = []

for entity in entity_urls:
  if isinstance(entity, int):
    if not entity in df["head"].index:
        raise Exception(f"Entity {entity} not valid.")
    entity_url = df["head"][entity]
    if not is_valid_entity(entity_url):
      raise Exception(f"Entity {entity} not valid.")
    heads.append(entity_url)

  if isinstance(entity, str): 
    head_exists = entity in df["head"].values
    if not head_exists or not is_valid_entity(entity):
      raise Exception(f"Entity {entity} not valid.")
    heads.append(entity)

relations = ['http://www.w3.org/2002/07/owl#sameAs'] * len(heads)

heads_idx = [triples_factory.entity_to_id[head] for head in heads]
relations_idx = [triples_factory.relation_to_id[relation] for relation in relations]

hr_batch = torch.tensor(list(zip(heads_idx, relations_idx)))
# print(hr_batch.shape)

sample = hr_batch[:len(heads)]
# print(sample)

torch.cuda.empty_cache()
scores = model.score_t(sample)

scores= torch.topk(scores, 10, largest=False)

print(scores)