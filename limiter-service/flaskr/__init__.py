from flask import Flask, request, jsonify
import redis
from datetime import datetime
import os

app = Flask(__name__)



REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

@app.route("/check_limit", methods=["POST"])
def check_limit():
    data = request.json
    user_id = data.get("user_id")
    user_type = data.get("user_type")

    if not user_id or not user_type:
        return jsonify({"error": "Missing user_id or user_type"}), 400

    if user_type == "premium":
        return jsonify({"allowed": True})  # Premium users have no limits

    # Rate limiting for freemium users
    current_time = int(datetime.now().timestamp())
    window_start = current_time // 60  # Get the current minute window
    key = f"rate_limit:{user_id}:{window_start}"

    request_count = redis_client.get(key)
    if request_count is None:
        redis_client.set(key, 1, ex=60)  # Set expiry time of 1 minute
    elif int(request_count) < 5:
        redis_client.incr(key)
    else:
        # Fetch TTL for the current key
        ttl = redis_client.ttl(key)
        return jsonify({
            "allowed": False,
            "message": "Rate limit exceeded. Try again later.",
            "time_left": ttl
        }), 429

    return jsonify({"allowed": True})
