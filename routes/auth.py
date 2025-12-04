from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask.typing import ResponseReturnValue
from repository import users_repo
from security.auth_utils import (
    build_hasher,
    maybe_upgrade_hash,
    normalize_and_validate_email,
    verify_password,
    validate_password,
    normalize_email,
    is_common_password,
)
from security.decorators import login_required
from security.limiter import limiter
from security.audit import log_security_event

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

_hasher = build_hasher()


# GET: Login form page
@auth_bp.route("/login", methods=["GET"])
def login() -> ResponseReturnValue:
    return render_template("login.html"), 200

# POST: Login Authentication
@auth_bp.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login_post() -> ResponseReturnValue:
    email_raw = request.form.get("email", "")
    email_raw = request.form.get("email", "")
    email = normalize_email(email_raw)
    password = request.form.get("password", "")

    if not email or not password:
        return _login_bad_request("Email and password are required.")
    user = users_repo.get_user_by_email(email)
    if not user or not verify_password(_hasher, user["password_hash"], password):
        log_security_event("LOGIN_FAILED", ip=request.remote_addr, target_id=email)
        return _login_invalid()

    maybe_upgrade_hash(_hasher, user, password, users_repo.update_user)

    # Session fixation defense and identity establishment
    _establish_session(user)
    log_security_event("LOGIN_SUCCESS", user_id=user["id"], ip=request.remote_addr)

    flash("Signed in.", "success")
    flash("Signed in.", "success")
    return redirect(url_for("reports.list_reports"), 303)


# GET: Registration form page
@auth_bp.route("/register", methods=["GET"])
def register() -> ResponseReturnValue:
    return render_template("register.html"), 200

# POST: Create account
@auth_bp.route("/register", methods=["POST"])
@limiter.limit("3 per hour")
def register_post() -> ResponseReturnValue:
    email_raw = request.form.get("email", "")
    email_raw = request.form.get("email", "")
    email = normalize_and_validate_email(email_raw)
    password = request.form.get("password", "")
    username = (request.form.get("username") or "").strip()
    # Security: ignore client-provided admin role in Phase 2; default to user
    role = "user"

    if not username or not email or not password:
        return _register_bad_request("Username, email and password are required.")

    # Server-side validation: enforce minimum password length regardless of client-side HTML
    if not validate_password(password):
        return _register_bad_request("Password must be at least 10 characters.")

    if is_common_password(password):
        return _register_bad_request("Password is too common.")
    
    # Check for existing email or username to avoid duplicates
    if users_repo.get_user_by_email(email):
        return _register_conflict("Email already registered.")

    pwd_hash = _hasher.hash(password)
    # Fallback safety: ensure a non-empty username is stored
    uid = users_repo.create_user(email=email, password_hash=pwd_hash, username=username or email, role=role)
    log_security_event("REGISTER_USER", user_id=uid, ip=request.remote_addr)
    flash("Account created. Please sign in.", "success")
    return redirect(url_for("auth.login"), 303)

# POST: Logout
@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout() -> ResponseReturnValue:
    log_security_event("LOGOUT", user_id=session.get("user_id"), ip=request.remote_addr)
    session.clear()
    flash("Signed out.", "info")
    return redirect(url_for("auth.login"), 303)
    session.clear()
    flash("Signed out.", "info")
    return redirect(url_for("auth.login"), 303)


# --- Micro-helpers (keep routes small and readable) ---

def _render_with_flash(template: str, category: str, message: str, status: int) -> ResponseReturnValue:
    """Flash a message, then render the template with the given HTTP status."""
    flash(message, category)
    return render_template(template), status


def _login_bad_request(msg: str) -> ResponseReturnValue:
    """400 for missing/invalid login form fields."""
    return _render_with_flash("login.html", "error", msg, 400)


def _login_invalid() -> ResponseReturnValue:
    """401 for wrong credentials; single path to avoid user enumeration."""
    return _render_with_flash("login.html", "error", "Invalid email or password.", 401)


def _register_bad_request(msg: str) -> ResponseReturnValue:
    """400 for missing/invalid registration fields."""
    return _render_with_flash("register.html", "error", msg, 400)


def _register_conflict(msg: str) -> ResponseReturnValue:
    """409 when the email is already registered."""
    return _render_with_flash("register.html", "error", msg, 409)


def _establish_session(user: dict) -> None:
    """Reset session (fixation defense) and set minimal identity (user_id, role).
    Sessions are signed cookies; HttpOnly/SameSite flags are set in app.py.
    """
    # Drop any pre-auth or attacker-influenced keys before we set identity
    session.clear()
    # Minimal identity: who the user is and, optionally, their role
    session["user_id"] = user["id"]
    session["role"] = (user.get("role") or "user").lower()
