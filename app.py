from datetime import timedelta
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, render_template
from flask_talisman import Talisman
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf, CSRFError

from database.connection import close_db
from security.limiter import limiter

csrf = CSRFProtect()


def create_app() -> Flask:
    load_dotenv()
    app = Flask(__name__, instance_relative_config=True)

    # --- Application Configuration ---
    # Security settings are grouped here for clarity.
    # 1. SECRET_KEY: Signs sessions and CSRF tokens. (Production: set this in .env!)
    # 2. SESSION_COOKIE_HTTPONLY: Prevents JavaScript from reading the session cookie (XSS protection).
    # 3. SESSION_COOKIE_SAMESITE: 'Lax' restricts cookies on cross-site requests (CSRF protection).
    # 4. SESSION_COOKIE_SECURE: Sends cookies only over HTTPS (active when debug=False).
    # 5. MAX_CONTENT_LENGTH: Limits request body to 3MB to prevent DoS attacks.
    
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-insecure-key"),
        DATABASE=os.environ.get("DATABASE", str(Path(app.instance_path) / "secureleak.sqlite")),
        UPLOADS_DIR=os.environ.get("UPLOADS_DIR", "uploads"),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        PERMANENT_SESSION_LIFETIME=timedelta(minutes=30),
        SESSION_COOKIE_SECURE=not app.debug,
        MAX_CONTENT_LENGTH=3 * 1024 * 1024,
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
    # Limiter: rate limiting to prevent brute-force and DoS attacks.
    csrf.init_app(app)
    limiter.init_app(app)
    Talisman(
        app,
        content_security_policy={ 
            "default-src": "'self'", 
            "script-src": "'self'", 
            "style-src": "'self'", 
            "object-src": "'none'", 
            "frame-ancestors": "'none'",
            "form-action": "'self'",
            "base-uri": "'self'"
        },
        force_https=not app.debug,
        strict_transport_security=True
    )

    from routes.auth import auth_bp
    from routes.reports import reports_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(admin_bp)

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

    # 429: Too Many Requests - Rate limiting
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return render_template("errors/429.html"), 429

    @app.route("/")
    def index() -> str:
        return render_template("login.html")

    @app.route("/.well-known/security.txt")
    def security_txt() -> str:
        """Serve the security.txt file for vulnerability disclosure."""
        content = Path("security/security.txt").read_text(encoding="utf-8")
        return content, 200, {"Content-Type": "text/plain; charset=utf-8"}

    # Ensure DB connections are closed after each request/app context
    app.teardown_appcontext(close_db)

    # Initialize and return the Flask application instance
    return app


app = create_app()
