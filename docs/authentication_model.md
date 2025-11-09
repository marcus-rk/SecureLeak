# Authentication & Authorization Model

This project uses **session-based authentication** with lightweight, role-aware authorization.
It follows the “Keep It Simple, Secure, and Explainable” principle suitable for a small Flask web app.

---

## Authentication

When a user logs in, Flask verifies their password (hashed with Argon2id) and stores their `user_id`
and `role` in a **signed session cookie**. The cookie is:

- **Signed** using `SECRET_KEY`, preventing tampering.
- **HttpOnly** and **SameSite=Lax**, protecting against XSS and CSRF.
- **Validated automatically** by Flask on every request.

This approach is called **session-based authentication**.  
It is *stateful*: the server issues and verifies the cookie each request.

> **Why not JWT or Basic Auth?**
> - JWT and Bearer tokens are designed for stateless APIs or distributed services.
> - This app is a traditional server-rendered site with forms and CSRF protection.
> - Flask’s session cookies are simpler, safer, and easier to explain in a security-focused exam.

---

## Authorization

Two custom decorators enforce access control:
- `@login_required` – blocks unauthenticated users, redirects to login.
- `@require_role("admin")` – checks both session and database to confirm the role before allowing access.

Additionally, per-object rules (e.g., report owners) use helper checks like:

```
require_owner_or_admin(owner_id)
```
