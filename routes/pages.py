import json
import time
import requests as http_requests
from flask import Blueprint, render_template, request, redirect, session, jsonify
from database import get_db, now
from helpers import (login_required, sanitize, valid_url, is_ssrf_safe,
                     MAX_ENDPOINT_LEN)

pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/")
def home():
    sort   = request.args.get("sort", "views")
    cat    = request.args.get("cat", "all")
    query  = request.args.get("q", "").strip()
    if sort not in {"views", "rating", "created_at", "rating_count"}:
        sort = "views"

    conn   = get_db()
    sql    = "SELECT * FROM apis WHERE 1=1"
    params = []

    if cat and cat != "all":
        sql += " AND category=?"
        params.append(cat)
    if query:
        q = f"%{query}%"
        sql += " AND (name LIKE ? OR description LIKE ? OR owner LIKE ?)"
        params.extend([q, q, q])

    sql   += f" ORDER BY {sort} DESC"
    apis   = conn.execute(sql, params).fetchall()
    total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    conn.close()

    return render_template("index.html", apis=apis, sort=sort, cat=cat,
                           query=query, total_users=total_users)


@pages_bp.route("/about")
def about():
    conn = get_db()
    total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    total_apis  = conn.execute("SELECT COUNT(*) FROM apis").fetchone()[0]
    total_views = conn.execute("SELECT SUM(views) FROM apis").fetchone()[0] or 0
    conn.close()
    return render_template("about.html", total_users=total_users,
                           total_apis=total_apis, total_views=total_views)


@pages_bp.route("/developer/<username>")
def developer(username):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    if not user:
        conn.close()
        return redirect("/")
    apis = conn.execute(
        "SELECT * FROM apis WHERE owner=? ORDER BY views DESC", (username,)
    ).fetchall()
    conn.close()
    return render_template("developer.html",
        name=username,
        apis=apis,
        is_admin=user["is_admin"] == 1,
        total_views=sum(a["views"] for a in apis),
        joined=user["created_at"][:10] if user["created_at"] else "Unknown"
    )


@pages_bp.route("/api_key")
@login_required
def api_key_page():
    return render_template("api_key.html", key=session["api_key"])


@pages_bp.route("/api_test", methods=["GET", "POST"])
@login_required
def api_test():
    result = error = endpoint = status = elapsed = headers = None
    endpoint = ""

    if request.method == "POST":
        endpoint = sanitize(request.form.get("endpoint", ""), MAX_ENDPOINT_LEN)
        if not endpoint:
            error = "Please enter an endpoint URL."
        elif not valid_url(endpoint):
            error = "URL must start with http:// or https://"
        elif not is_ssrf_safe(endpoint):
            error = "Requests to internal addresses are not allowed."
        else:
            try:
                start   = time.time()
                resp    = http_requests.get(endpoint, timeout=8,
                                            headers={"User-Agent": "DevAPIHub/1.0"})
                elapsed = round((time.time() - start) * 1000)
                status  = resp.status_code
                try:
                    result = json.dumps(resp.json(), indent=2)
                except Exception:
                    result = resp.text[:4000]
                headers = {k: v for k, v in resp.headers.items()
                           if k.lower() in ["content-type", "x-ratelimit-limit",
                                            "x-ratelimit-remaining", "cache-control", "server"]}
            except http_requests.exceptions.Timeout:
                error = "Request timed out after 8 seconds."
            except http_requests.exceptions.ConnectionError:
                error = "Could not connect — is the server running?"
            except Exception as e:
                error = f"Request failed: {str(e)}"

    return render_template("api_test.html", result=result, error=error,
                           endpoint=endpoint, status=status,
                           elapsed=elapsed, headers=headers)


@pages_bp.route("/search")
def search():
    q    = sanitize(request.args.get("q", ""), 100)
    cat  = sanitize(request.args.get("cat", ""), 20)
    page = max(1, int(request.args.get("page", 1)))
    per  = 10

    conn   = get_db()
    sql    = "SELECT * FROM apis WHERE 1=1"
    params = []
    if q:
        qp = f"%{q}%"
        sql += " AND (name LIKE ? OR description LIKE ? OR owner LIKE ?)"
        params.extend([qp, qp, qp])
    if cat and cat != "all":
        sql += " AND category=?"
        params.append(cat)

    total = conn.execute(sql.replace("SELECT *", "SELECT COUNT(*)"), params).fetchone()[0]
    sql  += f" ORDER BY views DESC LIMIT {per} OFFSET {(page-1)*per}"
    apis  = conn.execute(sql, params).fetchall()
    conn.close()

    return jsonify({
        "results": [dict(a) for a in apis],
        "total": total, "page": page,
        "pages": (total + per - 1) // per
    })


@pages_bp.route("/health")
def health():
    try:
        conn  = get_db()
        users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        apis  = conn.execute("SELECT COUNT(*) FROM apis").fetchone()[0]
        conn.close()
        return jsonify({"status": "ok", "timestamp": now(),
                        "db": "connected", "users": users, "apis": apis})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500