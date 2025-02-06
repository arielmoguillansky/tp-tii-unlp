from flask import Flask, request, jsonify
import redis
from datetime import datetime
import os
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

@app.route("/healthcheck")
def healthcheck():
    return "Limiter Server healthy"

@app.route("/check_limit")
def check_limit():
    # if request.method == "POST":
        user_id = redis_client.hget("user","oid")
        user_type = redis_client.hget("user","type")
        # data = request.json
        # user_id = data.get("user_id")
        # user_type = data.get("user_type")

        if not user_id or not user_type:
            return jsonify({"error": "Error en los datos del usuario"}), 400

        if user_type == "premium":
            return jsonify({"allowed": True})

        current_time = int(datetime.now().timestamp())
        window_start = current_time // 60 
        key = f"rate_limit:{user_id}:{window_start}"

        request_count = redis_client.get(key)
        if request_count is None:
            redis_client.set(key, 1, ex=60)
        elif int(request_count) < 3:
            redis_client.incr(key)
        else:
            ttl = redis_client.ttl(key)
            return jsonify({
                "allowed": False,
                "error": "Límite de peticiones alcanzado. Inténtalo de nuevo más tarde, o cambia a una cuenta premium.",
                "time_left": ttl
            }), 429

        return jsonify({"allowed": True})
