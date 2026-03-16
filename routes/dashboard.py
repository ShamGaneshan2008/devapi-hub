from flask import Blueprint, render_template, redirect, session
from database import get_db, now
from helpers import login_required, generate_api_key

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    conn    = get_db()
    my_apis = conn.execute(
        "SELECT * FROM apis WHERE owner=? ORDER BY created_at DESC",
        (session["user"],)
    ).fetchall()
    recent_logs = conn.execute(
        "SELECT * FROM api_logs WHERE user_id=? ORDER BY id DESC LIMIT 10",
        (session["user_id"],)
    ).fetchall()
    conn.close()

    return render_template(
        "dashboard.html",
        username=session["user"],
        api_key=session["api_key"],
        my_apis=my_apis,
        total_views=sum(a["views"] for a in my_apis),
        total_ratings=sum(a["rating_count"] for a in my_apis),
        recent_logs=recent_logs,
        is_admin=session.get("is_admin")
    )


@dashboard_bp.route("/regenerate_key", methods=["POST"])
@login_required
def regenerate_key():
    new_key = generate_api_key()
    conn    = get_db()
    conn.execute("UPDATE users SET api_key=? WHERE id=?", (new_key, session["user_id"]))
    conn.commit()
    conn.close()
    session["api_key"] = new_key
    return redirect("/dashboard")