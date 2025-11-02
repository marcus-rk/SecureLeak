# Authentication, Sessions, and CSRF

Flow (happy path):

```
GET  /auth/login  → form with CSRF token
POST /auth/login  → verify (Argon2id), session.clear(); session['user_id']=…, redirect 303 → /reports
POST /auth/logout → session.clear(), redirect 303 → /auth/login
```

- Passwords: hashed with Argon2id (argon2‑cffi). Parameters are explicit for exam clarity (time, memory, parallelism). On login, hashes may be upgraded in place if parameters change.
- Email normalization: `strip().lower()` before lookups to avoid duplicates and logic bugs.
- Generic failures: the same 401 path for wrong email or password to limit user enumeration.

Sessions (why and how):

- Flask uses cookie‑based, signed sessions (HMAC with `SECRET_KEY`). The server rejects tampered cookies.
- Security flags set in `app.py`:
  - `HttpOnly` → blocks JS access to the cookie (XSS resilience)
  - `SameSite=Lax` → reduces cross‑site cookie sending (CSRF resilience)
  - Consider `Secure=True` in production so cookies travel only over HTTPS.
- On authentication boundaries we call `session.clear()` to prevent session fixation and start from a clean slate; then we set minimal identity (`user_id`, optional `role`).

CSRF (tokens and handling):

- `Flask‑WTF`’s `CSRFProtect` binds tokens to the session; templates call `{{ csrf_token() }}` in forms.
- Missing/invalid tokens raise `CSRFError` which we map to HTTP 400 and a friendly page.

Status codes and PRG:

- Form errors → 400; invalid credentials → 401; duplicate email on register → 409.
- Successful POSTs redirect with 303 See Other (PRG) to avoid resubmission on refresh and to convert the next request to GET.