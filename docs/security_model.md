# Security Model (Threats & Defenses)

Threats considered:

- CSRF (cross‑site request forgery)
- XSS (cross‑site scripting)
- SQL injection
- Session fixation / hijacking
- Clickjacking and weak browser defaults
- File upload abuse (not enabled yet; approach documented below)

Defenses in this codebase:

- CSRF
  - `CSRFProtect`: per‑session tokens; templates render `{{ csrf_token() }}`.
  - Errors mapped to HTTP 400 with a friendly explanation.
- XSS
  - Jinja auto‑escaping by default; no unsafe `|safe` in user content.
  - Strict CSP via Talisman: `default-src 'self'; script-src 'self'` keeps third‑party and inline scripts out.
- SQL Injection
  - Repository layer uses parameterized queries (`?` placeholders) only.
  - Whitelisting column names in dynamic updates.
- Sessions
  - Cookie sessions are signed; `HttpOnly` and `SameSite=Lax` configured.
  - `session.clear()` at auth boundaries (fixation defense), then store minimal identity.
- Headers / Browser guards
  - Flask‑Talisman sets secure headers (CSP, HSTS, X‑Frame‑Options, Referrer‑Policy, X‑Content‑Type‑Options).
  - In production, enable `SESSION_COOKIE_SECURE=True` and HTTPS so cookies are never sent over HTTP.

Uploads (when added):

- Validate MIME type (`image/*`), bound size, and content sniffing; reject executables.
- Sanitize and randomize filenames (`secure_filename`, `secrets.token_hex()`); never execute or inline return content.
- Store files outside `/static` and serve via `send_file()` with authorization checks.

Limits & trade‑offs:

- SQLite is perfect for prototyping; for concurrency and migrations at scale, use Postgres.
- CSP can be strict; keep JS external (no inline) to avoid `unsafe-inline`.
- Cookie sessions are simple; keep payloads minimal since they’re client‑held (though signed).