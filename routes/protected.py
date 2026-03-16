import random
from flask import Blueprint, jsonify, request
from database import get_db, now
from helpers import api_key_required

protected_bp = Blueprint("protected", __name__)

JOKES = [
    {"setup": "Why do programmers prefer dark mode?",             "punchline": "Because light attracts bugs!"},
    {"setup": "How many programmers to change a light bulb?",     "punchline": "None — that's a hardware problem."},
    {"setup": "Why did the developer go broke?",                   "punchline": "They used up all their cache."},
    {"setup": "What's a computer's favourite snack?",              "punchline": "Microchips!"},
    {"setup": "Why do Java developers wear glasses?",              "punchline": "Because they don't C#."},
]


@protected_bp.route("/api/weather")
@api_key_required
def weather_api():
    resp = jsonify({
        "city": "London", "temperature": "18°C", "feels_like": "16°C",
        "status": "Cloudy", "humidity": "72%", "wind": "14 km/h",
        "uv_index": 3, "timestamp": now()
    })
    resp.headers["X-RateLimit-Remaining"] = str(request.rate_remaining) #Adds a header to the response
    return resp


@protected_bp.route("/api/joke")
@api_key_required
def joke_api():
    resp = jsonify({**random.choice(JOKES), "timestamp": now()})
    resp.headers["X-RateLimit-Remaining"] = str(request.rate_remaining)
    return resp


@protected_bp.route("/api/status")
@api_key_required
def status_api():
    from helpers import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW
    conn      = get_db()
    log_count = conn.execute(
        "SELECT COUNT(*) FROM api_logs WHERE user_id=?",
        (request.api_user["id"],)
    ).fetchone()[0]
    conn.close()
    resp = jsonify({
        "username":    request.api_user["username"],
        "total_calls": log_count,
        "rate_limit":  RATE_LIMIT_REQUESTS,
        "remaining":   request.rate_remaining,
        "window_secs": RATE_LIMIT_WINDOW,
        "timestamp":   now()
    })
    resp.headers["X-RateLimit-Remaining"] = str(request.rate_remaining)
    return resp