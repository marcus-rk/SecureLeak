"""Simple auth decorators for this app (KISS).

Provides:
- @login_required → redirects unauthenticated users to /auth/login
- @require_role(role) → requires a specific role; for 'admin' also verifies in DB
- require_owner_or_admin(owner_id) → helper for per-object access
"""

from functools import wraps
from flask import abort, flash, redirect, session, url_for
from repository.users_repo import get_user_by_id

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
    """Require `role` for a route (404 on mismatch; no info leak).

    - Unauthenticated → redirect to login (consistent with @login_required)
    - Mismatch → abort(404)
    - For 'admin' → confirm role in DB each request (defense-in-depth)
    """
    required = (role or "").lower()

    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            uid = session.get("user_id")
            if not uid:
                flash("Please sign in.", "info")
                return redirect(url_for("auth.login"))

            # Cheap session role check first
            sess_role = (session.get("role") or "").lower()
            if sess_role != required:
                abort(404)

            # Defense-in-depth: verify DB role for admins
            if required == "admin":
                try:
                    user = get_user_by_id(int(uid))
                except Exception:
                    user = None
                db_role = ((user or {}).get("role") or "").lower()
                if db_role != "admin":
                    abort(404)

            return view(*args, **kwargs)
        return wrapped
    return decorator
