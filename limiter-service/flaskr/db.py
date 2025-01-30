import os
import pymongo
from flask import g

def get_db():
    if 'db' not in g:
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")  # Default to localhost if MONGO_URI is not set
        db_name = os.getenv("DB_NAME", "mydb")  # Optional: Get the database name from an environment variable
        
        db_client = pymongo.MongoClient(mongo_uri)
        db = db_client[db_name]
        g.db = db
    
    return g.db
