# Project Overview

A tiny, layered Flask app designed for clarity and exam-friendliness. The goal is to show a secure baseline with simple, readable code and explicit trade‑offs.

Architecture (high level):

```
Browser → Routes (Blueprints) → Repository (SQL) → SQLite
         ↘ Templates (Jinja)  ↘ Security (CSRF, headers)
```

- App composition
  - `app.py` uses the app factory pattern, registers Blueprints (`auth`, `reports`), enables CSRF, and sets security headers via Talisman (strict CSP).
  - Cookie sessions: signed with `SECRET_KEY`; `HttpOnly` and `SameSite=Lax` configured.
  - Error handlers: 400 (CSRF), 404, 500 render friendly pages.

- Layers
  - Routes (`routes/`): minimal HTTP handlers per feature. POSTs use PRG (303 See Other → GET).
  - Repository (`repository/`): parameterized SQL only (prepared‑statement style) to prevent SQLi.
  - Database (`database/`): connection helpers and migrations (`migrations/init.sql`).
  - Security (`security/`): pure helpers (Argon2id, email normalize), simple decorators.
  - Templates (`templates/`): Jinja views; a base `layout.html` renders flash messages and nav.

- Dependencies (core)
  - Flask, Jinja2
  - Flask‑WTF (CSRFProtect, `generate_csrf`)
  - Flask‑Talisman (CSP, sane security headers)
  - argon2‑cffi (Argon2id password hashing)
  - sqlite3 (via Python stdlib)

Why these choices:

- Keep security controls visible and default‑secure (CSRF, CSP, cookies).
- Prefer small helpers over heavy frameworks to stay KISS and explainable in an exam.
- PRG eliminates double‑submit on refresh and avoids resubmitting credentials.
- Argon2id is the recommended modern password hash with memory hardness.

Trade‑offs:

- Cookie sessions are simple and signed, but still client‑held—store minimal identity only.
- SQLite keeps setup trivial; not suited for high write concurrency.
- CSP is restrictive by default; inline scripts are avoided to keep it green.