# Deployment (KISS)

**Goal:** TLS at the proxy (Nginx), app security headers/cookies in Flask.

- The Flask app runs on `127.0.0.1:8000` (Gunicorn).
- Nginx terminates HTTPS, redirects HTTP→HTTPS, and sets HSTS.
- Nginx passes `X-Forwarded-Proto: https` so Flask/Talisman treats requests as secure.
- The app sets CSP and secure cookies (HttpOnly, SameSite, Secure) in code.

### Files in this repo
- `deploy/nginx.conf` — minimal HTTPS reverse proxy (with comments).

### Dev vs Prod
- **Dev**: run `flask --app app run` (HTTP) or `flask --app app run --cert=adhoc` (self-signed HTTPS).
- **Prod**: run Gunicorn (`127.0.0.1:8000`), put Nginx in front using `deploy/nginx.conf`.

### Why this split
- TLS and redirects are proxy concerns (Nginx).
- CSRF, CSP, and cookie flags are app concerns (Flask).
