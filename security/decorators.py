"""Simple selfmade Flask auth decorators
instead of using Flask-Login or similar packages.
Provides @login_required and @require_role(role) decorators.

Additionally provides a small helper `require_owner_or_admin(owner_id)`
for use inside routes to gate per-object access.
"""

from functools import wraps
from flask import abort, flash, redirect, session, url_for

# Lazy import in functions to avoid circulars during app startup
try:
    from repository.users_repo import get_user_by_id  # type: ignore
except Exception:  # pragma: no cover - import safety during docs/build
    get_user_by_id = None  # type: ignore

# Decorator to require user login for a view.
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please sign in.", "info")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped

# Decorator to require a specific user role for a view.
def require_role(role: str):
    """Require a specific role.

    Behavior:
    - If unauthenticated, redirect to login (keeps UX consistent with @login_required).
    - If authenticated but role mismatch, return 404 to avoid leaking role/authorization info.
    """

    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            uid = session.get("user_id")
            if not uid:
                flash("Please sign in.", "info")
                return redirect(url_for("auth.login"))
            required = (role or "").lower()

            # Session role check first (cheap and avoids timing leaks)
            sess_role = (session.get("role") or "").lower()
            if sess_role != required:
                # Hide whether user exists or not
                abort(404)

            # Defense-in-depth for privileged routes: confirm with DB
            if required == "admin":
                # Only check DB if repository import is available
                user = None
                if callable(get_user_by_id):  # type: ignore
                    try:
                        user = get_user_by_id(int(uid))  # type: ignore[arg-type]
                    except Exception:
                        user = None
                # If user missing or DB role isn't admin → hide with 404
                db_role = ((user or {}).get("role") or "").lower() if user else ""
                if db_role != "admin":
                    abort(404)
            return view(*args, **kwargs)

        return wrapped

    return decorator


def require_owner_or_admin(owner_id: int) -> bool:
    """Return True if the current session user owns the object or is an admin.

    Use inside route handlers for per-object access gates, e.g.:

        if not require_owner_or_admin(report["user_id"]):
            abort(404)

    We return False (not raise) so routes can choose appropriate behavior.
    """

    uid = session.get("user_id")
    if not uid:
        return False

    # Owner check (coerce to int defensively)
    try:
        if int(uid) == int(owner_id):
            return True
    except Exception:
        # If session uid is malformed, treat as not owner
        pass

    # Admin check via DB (authoritative)
    if callable(get_user_by_id):  # type: ignore
        try:
            user = get_user_by_id(int(uid))  # type: ignore[arg-type]
        except Exception:
            user = None
        role = ((user or {}).get("role") or "").lower() if user else ""
        return role == "admin"

    # Fallback to session role only if repo not importable
    return (session.get("role") or "").lower() == "admin"
