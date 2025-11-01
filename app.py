import os
from pathlib import Path

from flask import Flask, render_template
from flask_talisman import Talisman
from flask_wtf import CSRFProtect
from dotenv import load_dotenv

csrf = CSRFProtect()

def create_app() -> Flask:
    load_dotenv()
    app = Flask(__name__, instance_relative_config=True)

    # Configure app with security-focused settings
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "secret123"),
        DATABASE=os.environ.get(
            "DATABASE", str(Path(app.instance_path) / "secureleak.sqlite")
        ),
        SESSION_COOKIE_HTTPONLY=True, # Prevent JavaScript access to session cookies
        SESSION_COOKIE_SAMESITE="Lax", # Mitigate CSRF attacks by restricting cross-site requests
    )

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    # CSRFProtect ties each form submission to a session-only token, blocking cross-site form forgeries.
    # Talisman issues modern security headers (CSP, HSTS, frame guard) so browsers refuse unsafe content.
    csrf.init_app(app)
    Talisman(app, content_security_policy={"default-src": "'self'"})

    from routes.auth import auth_bp
    from routes.reports import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(reports_bp)

    @app.route("/")
    def index() -> str:
        return render_template("login.html")

    # Initialize and return the Flask application instance
    return app


app = create_app()
