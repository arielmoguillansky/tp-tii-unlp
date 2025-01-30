from flask import (
    Flask,
    request,
    render_template,
    redirect,
    session,
    abort,
    jsonify,
)
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

@app.route("/login")
def login():
    return render_template('login.html')
    
@app.route("/register")
def register():
    return render_template('register.html')

@app.route("/")
def home():
    if not session['user']:
        return redirect('/login')
    return render_template('index.html')