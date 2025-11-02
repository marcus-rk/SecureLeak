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
    normalize_email,
    verify_password,
)
from security.decorators import login_required

auth_bp = Blueprint("auth", __name__)

_hasher = build_hasher()


# --- Micro-helpers (keep routes small and readable) ---

def _render_with_flash(template: str, category: str, message: str, status: int) -> ResponseReturnValue:
    flash(message, category)
    return render_template(template), status


def _login_bad_request(msg: str) -> ResponseReturnValue:
    return _render_with_flash("login.html", "error", msg, 400)


def _login_invalid() -> ResponseReturnValue:
    # Single path for invalid creds (no enumeration)
    return _render_with_flash("login.html", "error", "Invalid email or password.", 401)


def _register_bad_request(msg: str) -> ResponseReturnValue:
    return _render_with_flash("register.html", "error", msg, 400)


def _register_conflict(msg: str) -> ResponseReturnValue:
    return _render_with_flash("register.html", "error", msg, 409)


def _establish_session(user: dict) -> None:
    session.clear()
    session["user_id"] = user["id"]
    if "role" in user:
        session["role"] = user["role"]


# GET: Login form page
@auth_bp.route("/login", methods=["GET"])
def login() -> ResponseReturnValue:
    return render_template("login.html"), 200


# POST: Login Authentication
@auth_bp.route("/login", methods=["POST"])
def login_post() -> ResponseReturnValue:
    email = normalize_email(request.form.get("email", ""))
    password = request.form.get("password", "")

    if not email or not password:
        return _login_bad_request("Email and password are required.")

    user = users_repo.get_user_by_email(email)
    if not user or not verify_password(_hasher, user["password_hash"], password):
        return _login_invalid()

    maybe_upgrade_hash(_hasher, user, password, users_repo.update_user)

    # Prevent session fixation and set identity
    _establish_session(user)

    flash("Signed in.", "success")
    return redirect(url_for("reports.list_reports"))


# GET: Registration form page
@auth_bp.route("/register", methods=["GET"])
def register() -> ResponseReturnValue:
    return render_template("register.html"), 200


# POST: Create account
@auth_bp.route("/register", methods=["POST"])
def register_post() -> ResponseReturnValue:
    email = normalize_email(request.form.get("email", ""))
    password = request.form.get("password", "")
    name = (request.form.get("name") or "").strip()
    # Security: ignore client-provided admin role in Phase 2; default to user
    role = "user"

    if not name or not email or not password:
        return _register_bad_request("Name, email and password are required.")

    if users_repo.get_user_by_email(email):
        return _register_conflict("Email already registered.")

    pwd_hash = _hasher.hash(password)
    # Fallback safety: ensure a non-empty name is stored
    users_repo.create_user(email=email, password_hash=pwd_hash, name=name or email, role=role)
    flash("Account created. Please sign in.", "success")
    return redirect(url_for("auth.login"))

# POST: Logout
@auth_bp.route("/logout", methods=["POST"])
def logout() -> ResponseReturnValue:
    session.clear()
    flash("Signed out.", "info")
    return redirect(url_for("auth.login"))
