import secrets
from flask import Flask, jsonify, render_template, request
from database import init_db

from routes.auth      import auth_bp
from routes.dashboard import dashboard_bp
from routes.apis      import apis_bp
from routes.comments  import comments_bp
from routes.admin     import admin_bp
from routes.protected import protected_bp
from routes.pages     import pages_bp

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# ── Register blueprints ───────────────────────────────────
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(apis_bp)
app.register_blueprint(comments_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(protected_bp)
app.register_blueprint(pages_bp)

# ── Init DB ───────────────────────────────────────────────
init_db() # this setup the tables in the database before anyone visits

# ── Error handlers ────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Endpoint not found"}), 404
    return render_template("404.html"), 404

@app.errorhandler(500)
def server_error(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Internal server error"}), 500
    return render_template("404.html", message="Something went wrong."), 500

# ── Run ───────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)