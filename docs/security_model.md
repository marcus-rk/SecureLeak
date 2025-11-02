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
- XSS (cross‑site scripting)
  - Why it matters
    - Attacker‑controlled HTML/JS runs in the victim’s browser and can steal sessions, perform actions, or deface pages.
  - How we prevent it here
    - Auto‑escaping by Jinja2: values rendered with `{{ ... }}` are HTML‑escaped (`<`, `>`, `&`, `"`, `'`) so untrusted content shows as text, not code. Flask enables this by default for `.html` templates.
    - Avoid `|safe` on untrusted data: `|safe` disables escaping and can reintroduce XSS. Only use it on trusted, pre‑sanitized HTML.
    - Safe JS embedding with `|tojson`: when passing data into scripts, use `const data = {{ obj|tojson }};` to avoid breaking out of strings and to escape HTML‑significant chars correctly.
    - No inline JS or event handlers: keep JS in `static/js/main.js` and use `data-*` attributes. Our CSP blocks inline scripts and reduces XSS impact if a template slips.
    - Attribute/URL safety: keep attributes quoted and let Jinja escape: `<a href="{{ url }}">`, `<img alt="{{ name }}">`. If URLs come from users, whitelist schemes (e.g., `https`) to avoid `javascript:` links.
  - Defense‑in‑depth
    - Strict CSP via Talisman: `default-src 'self'; script-src 'self'` prevents third‑party and inline scripts, limiting exploitability.
    - HttpOnly session cookies: JS cannot read the cookie, reducing impact if any reflected XSS occurs.
  - Limits
    - Auto‑escape doesn’t sanitize rich HTML or URLs. If you must render HTML, sanitize server‑side first (e.g., Bleach) and only then mark safe. Use proper helpers (`tojson`, `url_for`) for JS/JSON/URLs.
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