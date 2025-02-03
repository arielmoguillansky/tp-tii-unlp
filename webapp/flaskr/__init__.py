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

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Set the desired logging level
handler = logging.StreamHandler(sys.stdout)  # Use sys.stdout
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
app = Flask(__name__)

AUTH_HOST = os.getenv("AUTH_HOST", "http://localhost:5001")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
app.secret_key = os.getenv('REDIS_KEY', default='123') # Same as auth service!

redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_REDIS'] = redis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}")
server_session = Session(app)

@app.route("/healthcheck")
def healthcheck():
    return "Webapp Server healthy"

@app.route("/login",  methods=["GET", "POST"])
def login():
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
            return jsonify({"allowed": False, "error": f"Error contacting authentication service: {e}"})
        
    return render_template('register.html')

@app.route("/")
def home():
    try:
        logger.debug(f"~~~~~~~~~~ RESPONSE LOGIN V2: {list(session.keys())}")
        if not session.get("user"):
            return redirect('/login')

    except requests.exceptions.RequestException as e:
        return jsonify({"allowed": False, "error": f"Error contacting authentication service: {e}"})
    
    return render_template("index.html", session={"user": session.get("user"), "logged_in": True})


@app.route("/logout",  methods=["POST"])
def logout():
    user_email = request.form.get("user_email")
    try:
        auth_response = requests.post(f"{AUTH_HOST}/logout", json={"email": user_email}, headers={"Content-Type": "application/json"})
        auth_data = auth_response.json()
        
        if auth_data.get("allowed"):
            return redirect('/login')

    except requests.exceptions.RequestException as e:
        return jsonify({"allowed": False, "error": f"Error contacting authentication service: {e}"})