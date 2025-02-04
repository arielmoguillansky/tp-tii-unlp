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
import jwt

SECRET_KEY_JWT = os.getenv("SECRET_KEY_JWT", "your_jwt_secret_key")

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
app = Flask(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
app.secret_key = os.getenv('REDIS_KEY', default='123')

redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_REDIS'] = redis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}")
server_session = Session(app)

@app.route("/healthcheck")
def healthcheck():
    return "Auth Server healthy"

    
@app.route("/login", methods=["POST"])
def login():
    user_email = request.json.get("email")

    if not user_email:
        return jsonify({"allowed": False, "message": "Falta email"}), 400     

    existing_user = get_db().users.find_one({"email": user_email})

    if not existing_user:
        return jsonify({"allowed": False, "message": "No existe un usuario con ese email"}), 401   

    session["user"] = {
        "oid": existing_user["oid"],
        "email": existing_user["email"],
        "type": existing_user["type"],
    }
    session["logged_in"] = True  
    
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
    
    get_db().users.insert_one(new_user)

    token = jwt.encode(new_user, SECRET_KEY_JWT, algorithm="HS256")
    
    response = jsonify({"allowed": True, "message": "Usuario registrado con éxito", "user": {"oid": new_user["oid"], "email": new_user["email"], "type": new_user["type"]}})
    response.set_cookie('access_token', token, httponly=True, samesite='Strict')

    return response, 201 

# @app.route("/logout", methods=["POST"])
# def logout():

#     session.clear()

#     return jsonify({"allowed": True, "message": "Sesión cerrada"}), 200 
