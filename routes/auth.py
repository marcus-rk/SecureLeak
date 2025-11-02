from __future__ import annotations

import functools

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
from argon2 import PasswordHasher, exceptions as argon2_exceptions

from repository import users_repo

auth_bp = Blueprint("auth", __name__)

# Argon2 parameters: balanced for development and exam readability
# - time_cost=3: ~3 iterations; increases CPU work
# - memory_cost=65536: 64 MiB memory to resist GPU/ASIC cracking
# - parallelism=2: reasonable for typical dev machines
# - hash_len=32, salt_len=16: standard sizes
_hasher = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=2, hash_len=32, salt_len=16)


def _normalize_email(email: str) -> str:
    return (email or "").strip().lower()


def login_required(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please sign in.", "info")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped


# GET: Login form page
@auth_bp.route("/login", methods=["GET"])
def login() -> ResponseReturnValue:
    return render_template("login.html"), 200


# POST: Login Authentication
@auth_bp.route("/login", methods=["POST"])
def login_post() -> ResponseReturnValue:
    email = _normalize_email(request.form.get("email", ""))
    password = request.form.get("password", "")

    if not email or not password:
        flash("Email and password are required.", "error")
        return render_template("login.html"), 400

    user = users_repo.get_user_by_email(email)
    try:
        if not user or not _hasher.verify(user["password_hash"], password):
            raise argon2_exceptions.VerifyMismatchError
    except Exception:
        # Treat all failures as generic invalid credentials (no enumeration)
        flash("Invalid email or password.", "error")
        return render_template("login.html"), 401

    # Optional: upgrade hash transparently
    try:
        if _hasher.check_needs_rehash(user["password_hash"]):
            users_repo.update_user(user["id"], password_hash=_hasher.hash(password))
    except Exception:
        pass  # non-fatal

    # Prevent session fixation and set identity
    session.clear()
    session["user_id"] = user["id"]
    if "role" in user:
        session["role"] = user["role"]

    flash("Signed in.", "success")
    return redirect(url_for("reports.list_reports"))


# GET: Registration form page
@auth_bp.route("/register", methods=["GET"])
def register() -> ResponseReturnValue:
    return render_template("register.html"), 200


# POST: Create account
@auth_bp.route("/register", methods=["POST"])
def register_post() -> ResponseReturnValue:
    email = _normalize_email(request.form.get("email", ""))
    password = request.form.get("password", "")
    name = (request.form.get("name") or "").strip()
    # Security: ignore client-provided admin role in Phase 2; default to user
    role = "user"

    if not name or not email or not password:
        flash("Name, email and password are required.", "error")
        return render_template("register.html"), 400

    if users_repo.get_user_by_email(email):
        flash("Email already registered.", "error")
        return render_template("register.html"), 409

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
