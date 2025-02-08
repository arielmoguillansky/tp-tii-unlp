from flask import (
    Flask,
    request,
    render_template,
    redirect,
    session,
    jsonify,
)
import os
import requests
import logging
import sys
import redis
from flask_session import Session
import json

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

app = Flask(__name__)

AUTH_HOST = os.getenv("AUTH_HOST", "http://localhost:5001")
PREDICTOR_HOST = os.getenv("PREDICTOR_HOST", "http://localhost:5000")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

@app.route("/healthcheck")
def healthcheck():
    return "Webapp Server healthy"

@app.route("/login",  methods=["GET", "POST"])
def login():
    logged_value = redis_client.hget("user","logged")
    if logged_value == "True":
        return redirect('/')
    
    if request.method == "POST":
        user_email = request.form.get("user_email")

        if not user_email: 
            return render_template('login.html', error="Campo email es obligatorio")

        try:
            auth_response = requests.post(f"{AUTH_HOST}/login", json={"email": user_email}, headers={"Content-Type": "application/json"})
            auth_data = auth_response.json()

            if auth_data.get("allowed"):
                return redirect('/')
            else:
                return render_template('login.html', error=auth_data.get("message"))
            
        except requests.exceptions.RequestException as e:
            return jsonify({"allowed": False, "error": f"Error contacting authentication service: {e}"})
    
    return render_template('login.html')
    
@app.route("/register",  methods=["GET", "POST"])
def register():
    logged_value = redis_client.hget("user","logged")
    
    if logged_value == "True":
        return redirect('/')
    
    if request.method == "POST":
        user_email = request.form.get("user_email")
        user_type = request.form.get("user_type")

        if not user_email: 
            return render_template('login.html', error="Campo email es obligatorio")

        if not user_type: 
            return render_template('login.html', error="Campo subscripción es obligatorio")

        try:
            auth_response = requests.post(f"{AUTH_HOST}/register", json={"email": user_email, "type": user_type}, headers={"Content-Type": "application/json"})
            auth_data = auth_response.json()

            if auth_data.get("allowed"):
                return redirect('/')
            else:
                return render_template('register.html', error=auth_data.get("message"))

        except requests.exceptions.RequestException as e:
            return jsonify({"allowed": False, "error": f"Error en el servicio de autenticación: {e}"}),500
    
    return render_template('register.html')
    
@app.route("/predict",  methods=["POST"])
def predict():
    logged_value = redis_client.hget("user","logged")
    
    if logged_value == "False":
        return redirect('/login')
    
    if request.method == "POST":
        predict_payload = request.json.get("payload")

        if len(predict_payload) == 0: 
            return jsonify({"allowed": False, "status":400, "error": "Debe proporcionar una URI o Id"}),400

        try:
            predictor_response = requests.post(f"{PREDICTOR_HOST}/predict", json={"entity_payload": predict_payload}, headers={"Content-Type": "application/json"})
            predictor_data = predictor_response.json()

            if predictor_data.get("allowed"):   
                return jsonify({"allowed": True, "response": predictor_data.get("response")}),200
            else:
                return jsonify({"allowed": False, "error": {"message": predictor_data.get("error"),"time_left": predictor_data.get("time_left")}}), 400

        except requests.exceptions.RequestException as e:
            return jsonify({"allowed": False, "error": f"Error en el servicio de predicción: {e}"}),500
    
    return render_template('index.html')

@app.route("/")
def home():
        logged_value = redis_client.hget("user","logged")
        if logged_value == "True": 
            return render_template("index.html", session={"user": redis_client.hgetall("user")})

        elif logged_value is None: 
            return redirect('/login')

        else:
            return redirect('/login')

@app.route("/logout")
def logout():
    try:
        auth_response = requests.post(f"{AUTH_HOST}/logout")
        auth_data = auth_response.json()
        
        if auth_data.get("allowed"):
            return redirect('/login')

    except requests.exceptions.RequestException as e:
        return jsonify({"allowed": False, "error": f"Error en el servicio de autenticación: {e}"}),500
    
    
@app.route('/logrequests')
def logrequests():
    logged_value = redis_client.hget("user","logged")
    
    if not logged_value or logged_value == "False":
        return redirect('/login')
    
    try:
        log_response = requests.get(f"{AUTH_HOST}/logrequests")
        log_data = log_response.json()
        
        if log_data.get("allowed"):
            return render_template("logrequests.html", response = log_data.get("response"), session = {"user": redis_client.hgetall("user")})


    except requests.exceptions.RequestException as e:
        return jsonify({"allowed": False, "error": f"Error en el servicio de autenticación: {e}"}),500
