from flask import (
    Flask,
    request,
    redirect,
    session,
    abort,
    jsonify,
)
import uuid
from datetime import datetime
from flaskr.db import get_db
import os
import redis
from flask_session import Session

app = Flask(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
WEBAPP_HOST = os.getenv("WEBAPP_HOST", "http://localhost:3000")
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

@app.route("/register", methods=["POST"])
def register():
    user_email = request.json.get("email")
    user_type = request.json.get("type")

    if not user_email or not user_type:
        abort(400, description="Falta el email o el tipo de usuario")

    existing_user = get_db().users.find_one({"email": user_email})

    if(existing_user):
        abort(400, description="Ya existe un usuario con ese email")

    new_user =  {
            "oid": str(uuid.uuid4()),
            "email": user_email,
            "type": user_type,
            "createdAt": datetime.now().isoformat(),
        }
    
    get_db().users.insert_one(new_user)

    session['user'] = existing_user

    # return jsonify({"message": "Usuario registrado con éxito", "user": {"oid": new_user["oid"], "email": new_user["email"], "type": new_user["type"]}}), 201 
    return redirect(f"{WEBAPP_HOST}/")
    
@app.route("/login", methods=["POST"])
def login():
    user_email = request.json.get("email")

    if not user_email:
        abort(400, description="Falta el email o el tipo de usuario")


    existing_user = get_db().users.find_one({"email": user_email})

    if not existing_user:
        abort(400, description="No existe un usuario con ese email")

    # session_id = create_session()
    # redis_client.set(session_id, existing_user)
    session['user'] = existing_user
    
    # return jsonify({"message": "Inicio sesión con éxito", "user":  {"oid": existing_user["oid"], "email": existing_user["email"], "type": existing_user["type"]}}), 201 
    return redirect(f"{WEBAPP_HOST}/")
    
