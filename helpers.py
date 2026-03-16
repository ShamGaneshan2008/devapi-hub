import re
import secrets
from functools import wraps
from datetime import datetime, timedelta
from flask import session, request, redirect, jsonify
from database import get_db, now

# ── Config ────────────────────────────────────────────────
RATE_LIMIT_REQUESTS = 30
RATE_LIMIT_WINDOW   = 60   # seconds
MAX_COMMENT_LEN     = 1000
MAX_API_NAME_LEN    = 80
MAX_DESCRIPTION_LEN = 500
MAX_ENDPOINT_LEN    = 300
VALID_CATEGORIES    = {"weather", "finance", "ai", "maps", "data", "other"}
BLOCKED_HOSTS       = ["localhost", "127.0.0.1", "0.0.0.0", "::1"]


# ── Input helpers ─────────────────────────────────────────
def sanitize(text, max_len=200): # check if the username is with in the given parameter
    if not text:
        return ""
    text = str(text).strip()
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    return text[:max_len]


def valid_url(url): # check if the url is real or not
    return url.startswith("http://") or url.startswith("https://")


def is_ssrf_safe(url): # Don't let hackers attack your own server
    lower = url.lower()
    for host in BLOCKED_HOSTS:
        if host in lower:
            return "/api/" in url   # only allow our own APIs
    return True


def generate_api_key():
    return "dah_" + secrets.token_hex(20)


# ── Rate limiting ─────────────────────────────────────────
def check_rate_limit(api_key): # this checks the limit of the API calls
    """Returns (allowed, remaining, reset_in_seconds)."""
    conn = get_db()
    row  = conn.execute(
        "SELECT * FROM rate_limits WHERE api_key=?", (api_key,)
    ).fetchone()

    if row:
        ws = datetime.strptime(row["window_start"], "%Y-%m-%d %H:%M:%S")
        if datetime.now() - ws < timedelta(seconds=RATE_LIMIT_WINDOW):
            if row["requests"] >= RATE_LIMIT_REQUESTS:
                reset_in = RATE_LIMIT_WINDOW - int((datetime.now() - ws).total_seconds())
                conn.close()
                return False, 0, reset_in
            conn.execute(
                "UPDATE rate_limits SET requests=requests+1 WHERE api_key=?", (api_key,)
            )
            remaining = RATE_LIMIT_REQUESTS - row["requests"] - 1
        else:
            conn.execute(
                "UPDATE rate_limits SET requests=1, window_start=? WHERE api_key=?",
                (now(), api_key)
            )
            remaining = RATE_LIMIT_REQUESTS - 1
    else:
        conn.execute(
            "INSERT INTO rate_limits(api_key, requests, window_start) VALUES (?,1,?)",
            (api_key, now())
        )
        remaining = RATE_LIMIT_REQUESTS - 1

    conn.commit()
    conn.close()
    return True, remaining, 0


def log_api_call(api_key, endpoint, status):
    try:
        conn = get_db()
        user = conn.execute(
            "SELECT id FROM users WHERE api_key=?", (api_key,)
        ).fetchone()
        conn.execute(
            "INSERT INTO api_logs(user_id, api_key, endpoint, status, ip, created_at) VALUES (?,?,?,?,?,?)",
            (user["id"] if user else None, api_key, endpoint,
             status, request.remote_addr, now())
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


# ── Decorators ────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            if request.is_json or request.path.startswith("/api/"):
                return jsonify({"error": "Authentication required"}), 401
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("is_admin"):
            if request.is_json:
                return jsonify({"error": "Admin access required"}), 403
            return redirect("/")
        return f(*args, **kwargs)
    return decorated


def api_key_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.args.get("key") or request.headers.get("X-API-Key")
        if not key:
            return jsonify({"error": "API key required", "hint": "Pass ?key=YOUR_KEY"}), 401

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE api_key=?", (key,)).fetchone()
        conn.close()

        if not user:
            log_api_call(key, request.path, 401)
            return jsonify({"error": "Invalid API key"}), 401

        allowed, remaining, reset_in = check_rate_limit(key)
        if not allowed:
            log_api_call(key, request.path, 429)
            resp = jsonify({
                "error": "Rate limit exceeded",
                "reset_in_seconds": reset_in,
                "limit": RATE_LIMIT_REQUESTS
            })
            resp.headers["X-RateLimit-Remaining"] = "0"
            resp.headers["X-RateLimit-Reset"]     = str(reset_in)
            return resp, 429

        request.api_user       = user
        request.rate_remaining = remaining
        log_api_call(key, request.path, 200)
        return f(*args, **kwargs)
    return decorated