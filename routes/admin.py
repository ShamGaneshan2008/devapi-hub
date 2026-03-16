from flask import Blueprint, render_template, redirect, session
from database import get_db
from helpers import login_required, admin_required

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin")
@login_required
@admin_required
def admin_panel():
    conn  = get_db()
    users = conn.execute("SELECT * FROM users ORDER BY id").fetchall()
    apis  = conn.execute("SELECT * FROM apis ORDER BY views DESC").fetchall()
    logs  = conn.execute("SELECT * FROM api_logs ORDER BY id DESC LIMIT 50").fetchall()
    conn.close()
    return render_template("admin.html", users=users, apis=apis, logs=logs)


@admin_bp.route("/admin/delete_user/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def delete_user(user_id):
    if user_id == session["user_id"]:
        return redirect("/admin")
    conn = get_db()
    conn.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    return redirect("/admin")


@admin_bp.route("/admin/delete_api/<int:api_id>", methods=["POST"])
@login_required
@admin_required
def delete_api(api_id):
    conn = get_db()
    conn.execute("DELETE FROM apis WHERE id=?", (api_id,))
    conn.commit()
    conn.close()
    return redirect("/admin")