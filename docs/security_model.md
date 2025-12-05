# Security Model (Threats & Defenses)

This document outlines the threat model for **SecureLeak** and the specific defenses implemented to mitigate them. It is mapped to the **OWASP Top 10:2025** to demonstrate comprehensive coverage.

---

## 1. Broken Access Control (A01:2025)

**Threat**: Users accessing resources or performing actions they are not authorized for (e.g., viewing another user's private report).

**Defenses**:
1.  **Role-Based Access Control (RBAC)**: Decorators enforce role checks (`@require_role('admin')`).
2.  **Object-Level Access Control (IDOR Prevention)**: Repository methods check ownership (e.g., `WHERE owner_id = ?`).
3.  **Information Hiding**: Unauthorized access to admin routes returns `404 Not Found` instead of `403 Forbidden` to prevent enumeration.

```python
# security/decorators.py
def require_role(role: str):
    required = (role or "").lower()

    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            # ...
            # Cheap session role check first
            sess_role = (session.get("role") or "").lower()
            if sess_role != required:
                abort(404)

            # Defense-in-depth: verify DB role for admins
            if required == "admin":
                # ... verify against DB ...
            
            return view(*args, **kwargs)
        return wrapped
    return decorator
```

---

## 2. Cryptographic Failures (A04:2025)

**Threat**: Sensitive data (passwords, sessions) being exposed or cracked.

**Defenses**:
1.  **Strong Hashing**: **Argon2id** (memory-hard) is used for passwords, resisting GPU cracking.
2.  **Secure Transmission**: `SESSION_COOKIE_SECURE=True` (in production) ensures cookies only travel over HTTPS.
3.  **Entropy**: Random tokens for CSRF and filenames use `secrets.token_hex()` (CSPRNG).

---

## 3. Injection (A05:2025)

**Threat**: Untrusted data being interpreted as code (SQLi, XSS).

**Defenses**:
1.  **SQL Injection**: Strictly using **Parameterized Queries** in `repository/`.
2.  **Cross-Site Scripting (XSS)**:
    *   **Auto-Escaping**: Jinja2 escapes HTML characters by default.
    *   **Content Security Policy (CSP)**: Blocks inline scripts and restricts sources.
    *   **HttpOnly Cookies**: Prevents JS from stealing sessions.

```python
# repository/reports_repo.py
cursor.execute(
    "INSERT INTO reports (owner_id, title, description, severity, status) VALUES (?, ?, ?, ?, ?)",
    (owner_id, title, description, severity, status)
)
```

---

## 4. Insecure Design (A06:2025)

**Threat**: Flaws in the logic or architecture that cannot be fixed by code alone.

**Defenses**:
1.  **Defense-in-Depth**: We don't rely on a single control (e.g., CSP backs up Auto-Escaping).
2.  **Secure Defaults**: The app is secure by default (e.g., all routes require auth unless exempted).
3.  **Rate Limiting**: Built-in protection against abuse, not added as an afterthought.

---

## 5. Security Misconfiguration (A02:2025)

**Threat**: Insecure default settings or incomplete configurations.

**Defenses**:
1.  **Hardened Headers**: `Flask-Talisman` sets HSTS, X-Frame-Options, and X-Content-Type-Options.
2.  **Cookie Security**: Explicitly setting `HttpOnly` and `SameSite=Lax`.
3.  **Error Handling**: Custom error pages (404, 500) prevent leaking stack traces (A10:2025).

```python
# app.py - CSP Configuration
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
```

---

## 6. Authentication Failures (A07:2025)

**Threat**: Attackers guessing passwords or hijacking sessions.

**Defenses**:
1.  **Rate Limiting**: Login is limited to 5 attempts/minute to stop brute-force.
2.  **Session Management**: `session.clear()` is called on login to prevent Session Fixation.
3.  **Generic Error Messages**: "Invalid email or password" prevents Account Enumeration.

---

## 7. Software and Data Integrity Failures (A08:2025)

**Threat**: Code or data being tampered with, or insecure deserialization.

**Defenses**:
1.  **File Upload Sanitization**: Images are re-encoded with **Pillow** to strip malicious metadata/payloads.
2.  **Signed Sessions**: Flask sessions are cryptographically signed to prevent client-side tampering.

---

## 8. Logging & Alerting Failures (A09:2025)

**Threat**: Security breaches going unnoticed or being impossible to investigate.
```python
# security/audit.py
def log_security_event(
    action: str,
    user_id: Optional[int] = None,
    target_id: Optional[str] = None,
    ip: Optional[str] = None,
) -> None:
    # ...
    try:
        _configure_logger()
        extra = {
            "ip": ip or "unknown",
            "user_id": str(user_id) if user_id else "anon",
            "target_id": str(target_id) if target_id else "-",
            "action": action,
        }
        # We pass the message as empty because all info is in the formatter/extra
        _audit_logger.info("", extra=extra)
    except Exception:
        pass
```     "user_id": str(user_id) if user_id else "anon",
        "action": action,
        "target_id": str(target_id) if target_id else "-",
    }
    _audit_logger.info("", extra=extra)
```

---

## 9. Cross-Site Request Forgery (CSRF)

*Note: While often merged into other categories, CSRF is a distinct threat we explicitly handle.*

**Defense**: **Synchronizer Token Pattern**. `Flask-WTF` generates a unique token for each session/form.

```html
<!-- templates/report_new.html -->
<form method="post">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
    <!-- ... -->
</form>
```

---

## 10. Denial of Service (DoS)

**Threat**: Resource exhaustion.

**Defenses**:
1.  **Rate Limiting**: Global and per-endpoint limits.
2.  **Resource Quotas**: `MAX_CONTENT_LENGTH` (3MB) limits upload sizes.
