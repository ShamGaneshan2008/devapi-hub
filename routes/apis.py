from flask import Blueprint, render_template, request, redirect, session
from database import get_db, now
from helpers import (login_required, sanitize, valid_url,
                     MAX_API_NAME_LEN, MAX_DESCRIPTION_LEN,
                     MAX_ENDPOINT_LEN, VALID_CATEGORIES)

apis_bp = Blueprint("apis", __name__)


@apis_bp.route("/api/<int:api_id>")
def api_details(api_id):
    conn = get_db()
    conn.execute("UPDATE apis SET views=views+1 WHERE id=?", (api_id,))
    conn.commit()

    api = conn.execute("SELECT * FROM apis WHERE id=?", (api_id,)).fetchone()
    if not api:
        conn.close()
        return redirect("/")

    comments       = conn.execute(
        "SELECT * FROM comments WHERE api_id=? ORDER BY id DESC", (api_id,)
    ).fetchall()
    owner          = conn.execute(
        "SELECT is_admin FROM users WHERE username=?", (api["owner"],)
    ).fetchone()
    related        = conn.execute(
        "SELECT * FROM apis WHERE category=? AND id!=? ORDER BY views DESC LIMIT 3",
        (api["category"], api_id)
    ).fetchall()
    conn.close()

    return render_template(
        "api_details.html",
        api=api,
        comments=comments,
        owner_is_admin=owner and owner["is_admin"] == 1,
        related=related
    )


@apis_bp.route("/add_api", methods=["GET", "POST"])
@login_required
def add_api():
    error = None
    if request.method == "POST":
        name        = sanitize(request.form.get("name", ""),        MAX_API_NAME_LEN)
        description = sanitize(request.form.get("description", ""), MAX_DESCRIPTION_LEN)
        endpoint    = sanitize(request.form.get("endpoint", ""),    MAX_ENDPOINT_LEN)
        category    = sanitize(request.form.get("category", "other"), 20)
        if category not in VALID_CATEGORIES:
            category = "other"

        if not all([name, description, endpoint]):
            error = "All fields are required."
        elif not valid_url(endpoint):
            error = "Endpoint must start with http:// or https://"
        else:
            conn = get_db()
            if conn.execute(
                "SELECT id FROM apis WHERE endpoint=? AND owner=?",
                (endpoint, session["user"])
            ).fetchone():
                error = "You already published an API with this endpoint."
                conn.close()
            else:
                conn.execute(
                    "INSERT INTO apis(name, description, endpoint, category, owner, created_at) VALUES (?,?,?,?,?,?)",
                    (name, description, endpoint, category, session["user"], now())
                )
                conn.commit()
                conn.close()
                return redirect("/dashboard")

    return render_template("add_api.html", error=error)


@apis_bp.route("/edit_api/<int:api_id>", methods=["GET", "POST"])
@login_required
def edit_api(api_id):
    conn = get_db()
    api  = conn.execute(
        "SELECT * FROM apis WHERE id=? AND owner=?", (api_id, session["user"])
    ).fetchone()
    if not api:
        conn.close()
        return redirect("/dashboard")

    error = None
    if request.method == "POST":
        name        = sanitize(request.form.get("name", ""),        MAX_API_NAME_LEN)
        description = sanitize(request.form.get("description", ""), MAX_DESCRIPTION_LEN)
        endpoint    = sanitize(request.form.get("endpoint", ""),    MAX_ENDPOINT_LEN)
        category    = sanitize(request.form.get("category", "other"), 20)
        if category not in VALID_CATEGORIES:
            category = "other"

        if not all([name, description, endpoint]):
            error = "All fields are required."
        elif not valid_url(endpoint):
            error = "Endpoint must start with http:// or https://"
        else:
            conn.execute(
                "UPDATE apis SET name=?, description=?, endpoint=?, category=? WHERE id=? AND owner=?",
                (name, description, endpoint, category, api_id, session["user"])
            )
            conn.commit()
            conn.close()
            return redirect("/dashboard")

    conn.close()
    return render_template("edit_api.html", api=api, error=error)


@apis_bp.route("/delete_api/<int:api_id>", methods=["POST"])
@login_required
def delete_api(api_id):
    conn = get_db()
    conn.execute("DELETE FROM apis WHERE id=? AND owner=?", (api_id, session["user"]))
    conn.commit()
    conn.close()
    return redirect("/dashboard")


@apis_bp.route("/rate/<int:api_id>", methods=["GET", "POST"])
@login_required
def rate_api(api_id):
    conn = get_db()
    api  = conn.execute("SELECT * FROM apis WHERE id=?", (api_id,)).fetchone()
    if not api:
        conn.close()
        return redirect("/")

    if request.method == "POST":
        try:
            rating = int(request.form["rating"])
        except (ValueError, KeyError):
            rating = 0

        if 1 <= rating <= 5:
            new_count  = api["rating_count"] + 1
            new_rating = ((api["rating"] * api["rating_count"]) + rating) / new_count
            conn.execute(
                "UPDATE apis SET rating=?, rating_count=? WHERE id=?",
                (round(new_rating, 1), new_count, api_id)
            )
            conn.commit()
        conn.close()
        return redirect(f"/api/{api_id}")

    conn.close()
    return render_template("rate_api.html", api=api)