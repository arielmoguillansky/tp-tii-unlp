from flask import (
    Flask,
    request,
    jsonify,
    session
)
import uuid
from datetime import datetime
from flaskr.db import get_db
import os
import redis
from flask_session import Session
import logging
import sys

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
app = Flask(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

@app.route("/login", methods=["POST"])
def login():
    user_email = request.json.get("email")

    if not user_email:
        return jsonify({"allowed": False, "message": "Falta email"}), 400     

    existing_user = get_db().users.find_one({"email": user_email})

    if not existing_user:
        return jsonify({"allowed": False, "message": "No existe un usuario con ese email"}), 401   
    
    logged_user = {
        "oid": existing_user["oid"],
        "email": existing_user["email"],
        "type": existing_user["type"],
        "logged": "True"
    }

    redis_client.hmset('user', mapping = logged_user)
    redis_client.expire('user', 3600)
    
    return jsonify({"allowed": True, "message": "Inicio sesión con éxito", "user": {"oid": existing_user["oid"], "email": existing_user["email"], "type": existing_user["type"]}}), 201     

@app.route("/register", methods=["POST"])
def register():
    user_email = request.json.get("email")
    user_type = request.json.get("type")

    if not user_email:
        return jsonify({"allowed": False, "message": "Falta email"}), 400     

    if not user_type:
        return jsonify({"allowed": False, "message": "Falta tipo de suscripción"}), 400     

    existing_user = get_db().users.find_one({"email": user_email})

    if(existing_user):
        return jsonify({"allowed": False, "message": "Ya existe un usuario con el mail proporcionado"}), 400     

    new_user =  {
            "oid": str(uuid.uuid4()),
            "email": user_email,
            "type": user_type,
            "createdAt": datetime.now().isoformat(),
        }

    redis_client.hmset('user', mapping = {**new_user, "logged": "True"})
    redis_client.expire('user', 3600)

    get_db().users.insert_one(new_user)

    response = jsonify({"allowed": True, "message": "Usuario registrado con éxito", "user": {"oid": new_user["oid"], "email": new_user["email"], "type": new_user["type"]}})

    return response, 201 

@app.route("/logout", methods=["POST"])
def logout():

    redis_client.delete("user")
    
    return jsonify({"allowed": True, "message": "Sesión cerrada"}), 200 
