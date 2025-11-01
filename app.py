import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, render_template
from flask_talisman import Talisman
from flask_wtf import CSRFProtect

csrf = CSRFProtect()

def create_app() -> Flask:
    load_dotenv()
    app = Flask(__name__, instance_relative_config=True)

    # Configure app with security-focused settings
    app.config.from_mapping(
        # SECRET_KEY — cryptographic key used to sign sessions and CSRF tokens.
        # Loaded from environment to avoid exposing secrets in source control.
        SECRET_KEY=os.environ.get("SECRET_KEY", "secret123"),
        DATABASE=os.environ.get(
            "DATABASE", str(Path(app.instance_path) / "secureleak.sqlite")
        ),
        # Disallows reading session cookies.
        # Protects against client-side script access if XSS ever occurs.
        SESSION_COOKIE_HTTPONLY=True,
        # Limits cookies being sent on cross-site requests.
        # Reduces risk of Cross-Site Request Forgery (CSRF) by defaulting to first-party context.
        SESSION_COOKIE_SAMESITE="Lax",
    )

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    # CSRFProtect: attaches per-session tokens to all forms to prevent Cross-Site Request Forgery (CSRF) attacks.
    # Talisman: enforces secure HTTP headers (CSP, HSTS, frame and content guards) to mitigate XSS and clickjacking.
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
