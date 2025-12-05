# Roles, Authorization, and Admin Area

This document details the Role-Based Access Control (RBAC) system and the Admin dashboard.

---

## 🎭 Roles

The application supports two roles:

1.  **User**: Standard user. Can create reports and view public reports.
2.  **Admin**: Superuser. Can view all reports and change their status.

**Storage**:
*   **Database**: `users.role` column.
*   **Session**: `session['role']` (cached for performance, verified for critical actions).

---

## 🔐 Authorization Decorators

We use custom decorators to enforce access control. This keeps the route logic clean and the security logic centralized.

### 1. `@login_required`
Ensures the user is authenticated. Redirects to login if not.

### 2. `@require_role('admin')`
Ensures the user has the 'admin' role.

**Defense-in-Depth**:
For admin actions, we don't just trust the session cookie. We re-verify the role against the database to ensure a demoted admin loses access immediately.

**Information Hiding**:
If a non-admin tries to access an admin route, we return **404 Not Found** instead of 403 Forbidden. This prevents attackers from mapping out the admin interface.

```python
# security/decorators.py
def require_role(role: str):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            # ... auth check ...
            
            # 1. Session Check (Fast)
            if session.get("role") != role:
                abort(404) # Hide existence

            # 2. Database Check (Secure - for admins)
            if role == "admin":
                user = get_user_by_id(session["user_id"])
                if not user or user["role"] != "admin":
                    session.clear()
                    abort(404)
            
            return view(*args, **kwargs)
    return decorator
```

---

## 🎛️ Admin Dashboard

The admin dashboard (`/admin`) allows managing report statuses.

**Security Features**:
*   **Route Protection**: All routes are protected by `@require_role('admin')`.
*   **CSRF Protection**: All state-changing actions (POST) require a CSRF token.
*   **Input Validation**: Status updates are whitelisted (`public`, `private`, `closed`).

---

## 📊 Authorization Matrix

| Resource | User | Admin | Unauthenticated |
|:---|:---|:---|:---|
| **View Public Reports** | ✅ | ✅ | ❌ (Redirect) |
| **Create Report** | ✅ | ✅ | ❌ (Redirect) |
| **View Own Private Report** | ✅ | ✅ | ❌ (Redirect) |
| **View Others' Private Report** | ❌ (404) | ✅ | ❌ (Redirect) |
| **Admin Dashboard** | ❌ (404) | ✅ | ❌ (Redirect) |
| **Change Report Status** | ❌ (404) | ✅ | ❌ (Redirect) |

---

## 🧪 Testing Strategy

*   **Role Enforcement**: Test that a normal user gets a 404 when accessing `/admin`.
*   **Privilege Escalation**: Test that modifying the session cookie (if possible) doesn't grant admin access without DB validation.
*   **Status Changes**: Verify that only admins can change a report's status.
