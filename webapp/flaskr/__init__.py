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
import jwt

SECRET_KEY_JWT = os.getenv("SECRET_KEY_JWT", "your_jwt_secret_key")

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
app = Flask(__name__)

AUTH_HOST = os.getenv("AUTH_HOST", "http://localhost:5001")
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

            logger.debug(f"~~~~~~~~~~ RESPONSE LOGIN V2: {list(session.keys())}")

            if auth_data.get("allowed"):
                return redirect('/')
            else:
                return render_template('register.html', error=auth_data.get("message"))

        except requests.exceptions.RequestException as e:
            return jsonify({"allowed": False, "error": f"Error contacting authentication service: {e}"})
        
    return render_template('register.html')

@app.route("/")
def home():
        token = request.cookies.get('access_token')
        logger.debug(f"~~~~~~~~~~ RESPONSE LOGIN V2: {list(session.keys())}")
        if not token:
            return redirect('/login')
        try:
            payload = jwt.decode(token, SECRET_KEY_JWT, algorithms=["HS256"])
            # Now you have the user info from the payload
            session["user"] = payload # Store user in session, but only after JWT verification
            return render_template("index.html", session={"user": session.get("user"), "logged_in": True})

        except jwt.ExpiredSignatureError:
            return redirect('/login')  # Token expired
        except jwt.InvalidTokenError:
            return redirect('/login')  # Invalid token

# @app.route("/logout",  methods=["GET"])
# def logout():
#     try:
#         auth_response = requests.post(f"{AUTH_HOST}/logout")
#         auth_data = auth_response.json()
        
#         if auth_data.get("allowed"):
#             return redirect('/login')

#     except requests.exceptions.RequestException as e:
#         return jsonify({"allowed": False, "error": f"Error contacting authentication service: {e}"})