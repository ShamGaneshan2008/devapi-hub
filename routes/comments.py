from flask import Blueprint, redirect, request, session
from database import get_db, now
from helpers import login_required, admin_required, sanitize, MAX_COMMENT_LEN

comments_bp = Blueprint("comments", __name__)


@comments_bp.route("/comment/<int:api_id>", methods=["POST"])
@login_required
def add_comment(api_id):
    body = sanitize(request.form.get("body", ""), MAX_COMMENT_LEN)
    if body:
        conn = get_db()
        if conn.execute("SELECT id FROM apis WHERE id=?", (api_id,)).fetchone():
            conn.execute(
                "INSERT INTO comments(api_id, username, body, created_at) VALUES (?,?,?,?)",
                (api_id, session["user"], body, now())
            )
            conn.commit()
        conn.close()
    return redirect(f"/api/{api_id}")


@comments_bp.route("/delete_comment/<int:comment_id>", methods=["POST"])
@login_required
@admin_required
def delete_comment(comment_id):
    conn    = get_db()
    comment = conn.execute("SELECT api_id FROM comments WHERE id=?", (comment_id,)).fetchone()
    api_id  = comment["api_id"] if comment else None
    conn.execute("DELETE FROM comments WHERE id=?", (comment_id,))
    conn.commit()
    conn.close()
    return redirect(f"/api/{api_id}" if api_id else "/")