import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, render_template
from flask_talisman import Talisman
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf, CSRFError

from database.connection import close_db

csrf = CSRFProtect()


def create_app() -> Flask:
    load_dotenv()
    app = Flask(__name__, instance_relative_config=True)

    # Configure app with security-focused settings
    app.config.from_mapping(
        # SECRET_KEY — cryptographic key used to sign sessions and CSRF tokens.
        # Loaded from environment to avoid exposing secrets in source control.
        SECRET_KEY=os.environ.get("SECRET_KEY", "5f4dcc3b5aa765d61d8327deb882cf99"), # Bad practice!
        DATABASE=os.environ.get("DATABASE", str(Path(app.instance_path) / "secureleak.sqlite")),
        # Disallows reading session cookies.
        # Protects against client-side script access if XSS ever occurs.
        SESSION_COOKIE_HTTPONLY=True,
        # Limits cookies being sent on cross-site requests.
        # Reduces risk of Cross-Site Request Forgery (CSRF) by defaulting to first-party context.
        SESSION_COOKIE_SAMESITE="Lax",
    )

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    # Auto-initialize the SQLite DB on first run.
    db_file = Path(app.config["DATABASE"])
    if not db_file.exists():
        from database.initialize import apply as init_db_from_sql
        with app.app_context():
            init_db_from_sql()
            app.logger.info(f"Initialized new database at {db_file}")
    else:
        app.logger.info(f"Using existing database at {db_file}")

    # CSRFProtect: attaches per-session tokens to all forms to prevent Cross-Site Request Forgery (CSRF) attacks.
    # Talisman: enforces secure HTTP headers (CSP, HSTS, frame and content guards) to mitigate XSS and clickjacking.
    csrf.init_app(app)
    Talisman(app,content_security_policy={
            "default-src": "'self'",
            "script-src": "'self'",
        })

    from routes.auth import auth_bp
    from routes.reports import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(reports_bp)

    # Make csrf_token() available in all templates without requiring WTForms
    @app.context_processor
    def inject_csrf_token():
        return {"csrf_token": generate_csrf}

    # --- Error handlers: consistent user-friendly pages ---
    # 404: Not Found – show a simple page instead of the default Werkzeug response
    @app.errorhandler(404)
    def not_found(_e):
        return render_template("errors/404.html"), 404

    # 500: Internal Server Error – generic message; avoid leaking stack traces
    @app.errorhandler(500)
    def internal_error(_e):
        return render_template("errors/500.html"), 500

    # 400 (CSRF): Invalid/missing CSRF tokens map to a clear, non-technical message
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e: CSRFError):
        reason = getattr(e, "description", "Invalid or missing CSRF token")
        return render_template("errors/400.html", reason=reason), 400

    @app.route("/")
    def index() -> str:
        return render_template("login.html")

    # Ensure DB connections are closed after each request/app context
    app.teardown_appcontext(close_db)

    # Initialize and return the Flask application instance
    return app


app = create_app()
