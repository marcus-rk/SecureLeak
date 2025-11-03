"""Simple selfmade Flask auth decorators
instead of using Flask-Login or similar packages.
Provides @login_required and @require_role(role) decorators.
"""

from functools import wraps
from flask import abort, flash, redirect, session, url_for

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
            if not session.get("user_id"):
                flash("Please sign in.", "info")
                return redirect(url_for("auth.login"))
            if session.get("role") != role:
                abort(404)
            return view(*args, **kwargs)

        return wrapped

    return decorator
