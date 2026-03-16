import re
from flask import Blueprint, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db, now
from helpers import sanitize, generate_api_key

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        username = sanitize(request.form.get("username", ""), 40)
        password = request.form.get("password", "")

        if not username or not password:
            error = "Username and password are required."
        elif len(username) < 3:
            error = "Username must be at least 3 characters."
        elif not re.match(r'^[a-zA-Z0-9_]+$', username):
            error = "Username can only contain letters, numbers, and underscores."
        elif len(password) < 6:
            error = "Password must be at least 6 characters."
        else:
            conn = get_db()
            if conn.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone():
                error = "Username already taken."
                conn.close()
            else:
                user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
                conn.execute(
                    "INSERT INTO users(username, password, api_key, is_admin, created_at) VALUES (?,?,?,?,?)",
                    (username, generate_password_hash(password),
                     generate_api_key(), 1 if user_count == 0 else 0, now())
                )
                conn.commit()
                conn.close()
                return redirect("/login")

    return render_template("register.html", error=error)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = sanitize(request.form.get("username", ""), 40)
        password = request.form.get("password", "")

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()

        if user and check_password_hash(user["password"], password):
            conn.execute("UPDATE users SET last_login=? WHERE id=?", (now(), user["id"]))
            conn.commit()
            conn.close()
            session.update({
                "user":     user["username"],
                "user_id":  user["id"],
                "api_key":  user["api_key"],
                "is_admin": bool(user["is_admin"])
            })
            return redirect("/dashboard")

        conn.close()
        error = "Invalid username or password."

    return render_template("login.html", error=error)


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")