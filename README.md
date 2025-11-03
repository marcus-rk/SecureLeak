# SecureLeak

> *A minimal, educational bug tracker built to study and prevent web vulnerabilities.*

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-2.x-black?logo=flask)
![SQLite](https://img.shields.io/badge/SQLite-07405E?logo=sqlite&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6-F7DF1E?logo=javascript&logoColor=black)
![Argon2](https://img.shields.io/badge/Password-Argon2-7952B3)
![FlaskWTF](https://img.shields.io/badge/Forms-CSRF_Protected-green)
![FlaskTalisman](https://img.shields.io/badge/Headers-CSP%2FHSTS-orange)
![Werkzeug](https://img.shields.io/badge/Uploads-Safe-yellow)
![Gunicorn](https://img.shields.io/badge/WSGI-Gunicorn-499848?logo=gunicorn&logoColor=white)
![Nginx](https://img.shields.io/badge/Reverse_Proxy-Nginx-009639?logo=nginx&logoColor=white)
![Security](https://img.shields.io/badge/Focus-Web_Security-critical)
[![CI - Lint and Security](https://github.com/marcus-rk/SecureLeak/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/marcus-rk/SecureLeak/actions/workflows/ci.yml)

---

## Project Overview

**SecureLeak** is a simplified bug tracker where developers (users) can submit **vulnerability reports** to admins. 
 
Admins review, comment on, close, or delete reports (e.g., spam).  
Reports can be **public** (for learning) or **private** (internal).  
Optional **file uploads** allow screenshots or proof-of-concepts.  

It’s intentionally **meta** — a secure app *about* vulnerabilities, protected against the same threats it demonstrates.

---

## Documentation

- Project overview: [docs/project_overview.md](docs/project_overview.md)
- Authentication & sessions: [docs/auth.md](docs/auth.md)
- Security model (threats/defenses): [docs/security_model.md](docs/security_model.md)
 - Reports & uploads: [docs/reports.md](docs/reports.md)

---

## Core Security Focus

| Threat | Mitigation |
|:--------|:------------|
| SQL Injection | Parameterized queries |
| XSS | Auto-escaped templates, CSP |
| CSRF | Flask-WTF CSRF tokens |
| File Upload Abuse | MIME validation, random names, non-public storage |
| XXE / Deserialization | Secure XML parser, entities & DTD disabled |
| Session Hijacking | HttpOnly + SameSite cookies |
| Client-Side Manipulation | All checks enforced server-side |

---

## 👥 Roles & Permissions

| Action | Developer (User) | Admin |
|:--------|:-----------------|:------|
| Register / Login | ✅ | ✅ |
| Create report | ✅ | ✅ |
| Upload image / PoC | ✅ | ✅ |
| View **public** reports | ✅ | ✅ |
| View **private** reports | ⚠️ (only their own) | ✅ |
| Comment on reports | ⚠️ (own/public) | ✅ |
| Change report status (Public / Private / Closed) | ⚠️ (only their own) | ✅ |
| Delete report | ⚠️ (only their own) | ✅ |

---

## Key Features

- Registration & login system (Argon2)
- Role-based access (Admin / Developer)
- Create & view vulnerability reports
- Public / private report visibility
- Comments for discussions
- Secure file uploads (screenshots / PoCs)
- Admin dashboard (moderate, close, delete)
- Optional XML/JSON import (XXE-safe)
- Security headers (CSP, HSTS, X-Frame-Options, etc.)

---

## 📂 Project Structure

```
SecureLeak/
├─ app.py                  # App factory: config, CSRF, security headers, blueprints, error handlers
├─ requirements.txt        # Python dependencies
├─ pytest.ini              # pytest configuration
├─ README.md               # Project guide + documentation links
├─ docs/                   
│  ├─ project_overview.md  # Layers, dependencies, trade-offs
│  ├─ auth.md              # Auth flow, sessions, CSRF, PRG
│  └─ security_model.md    # Threat model and defenses
│
├─ database/               
│  ├─ connection.py        # get_db()/close_db(); SQLite connection used by repositories
│  ├─ initialize.py        # Applies migrations on first run
│  └─ migrations/
│     └─ init.sql          # Schema: tables and indexes
│
├─ repository/             # Data-access layer (parameterized SQL only)
│  ├─ users_repo.py        
│  ├─ reports_repo.py      
│  └─ comments_repo.py     
│
├─ routes/                 # Feature routes (Flask blueprints)
│  ├─ auth.py              # Login, register, logout (Argon2id, CSRF, PRG)
│  └─ reports.py           # List/view/new reports
│
├─ security/               # Security helpers and selfmade decorators
│  ├─ auth_utils.py        # Argon2id hasher, email normalize, verify/rehash
│  └─ decorators.py        # login_required, role checks (KISS)
│
├─ templates/              # Jinja2 templates (auto-escaped)
│  ├─ layout.html          # Base layout + nav + flash messages
│  ├─ login.html           # Auth form with CSRF token
│  ├─ register.html        # Registration form with CSRF token
│  ├─ reports_list.html    # Reports table
│  ├─ report_detail.html   # Single report view
│  ├─ report_new.html      # Create report form
│  └─ errors/              
│     ├─ 400.html          # Bad request (e.g., CSRF)
│     ├─ 404.html          # Not found
│     └─ 500.html          # Server error
│
├─ static/                 # Front-end assets
│  ├─ css/
│  │  └─ style.css         
│  ├─ js/
│  │  └─ main.js           
│  └─ icons/               
│
├─ tests/                  # Pytest test-suite
│  ├─ conftest.py          # App fixture (temp DB per run)
│  ├─ auth/
│  │  └─ test_login.py     # CSRF + login redirect checks
│  ├─ security/
│  │  ├─ test_headers.py   # CSP header checks
│  │  └─ test_csp_headers.py
│  └─ repository/          # Repository CRUD tests
│     ├─ test_users_repo.py
│     ├─ test_reports_repo.py
│     └─ test_comments_repo.py
│
├─ uploads/                # Uploaded files (kept outside /static)
└─ instance/               # Runtime data (DB, logs)
  └─ logs/
```

**How it works:**
- `app.py` creates the Flask app, enables CSRF and security headers, registers blueprints, and auto-initializes the SQLite DB on first run.  
- `database/` holds the SQLite connection helpers and the migration SQL.  
- `repository/` contains small CRUD helpers that use `database.connection.get_db()`.  
- `routes/` defines the URL endpoints per feature (auth, reports).  
- `templates/` contains the rendered HTML pages, and `static/` serves CSS/JS/icons.  
- `instance/` holds the SQLite database and other writable runtime files.  
- `uploads/` stores user-uploaded files outside the static path for safety.

---

# 🧭 SecureLeak – Development Outline

A simple, phased roadmap with both **Feature (how)** and **Security (what/why/how)** focus.  
Each phase builds naturally on the previous one — simple, readable, and exam-friendly.

---

## **Phase 1 – Setup (Skeleton)**

**Feature (how):**
- Create base files: `app.py`, `.env`, `requirements.txt`, `.gitignore`
- Add folders: `database/` (with `migrations/`), `repository/`, `routes/`, `templates/`, `static/{css,js}`, `instance/`
- Add base templates: `layout.html`
- Static assets: `style.css`, `main.js`
- Create a test route `/` in `app.py` or a tiny blueprint

**Security (what/why/how):**
- CSRF protection: enable `Flask-WTF` → `CSRFProtect(app)`
- HTTP headers: `Flask-Talisman` with a minimal CSP (`default-src 'self'`)
- Secret management: store `SECRET_KEY` in `.env`

**Done when:**
- The home page renders via Jinja2
- A dummy POST without a CSRF token returns 400/403
- App runs at `http://localhost:5000`

---

## **Phase 2 – Authentication (Register/Login/Logout)**

**Feature (how):**
- DB table: `users(id, email unique, username, password_hash, role)`
- Templates: `login.html`, `register.html`
- Routes (`routes/auth.py`):  
  - `GET/POST /register` (form → create user)  
  - `GET/POST /login` (form → session cookie)  
  - `POST /logout`
- Minimal CSS for forms

**Security (what/why/how):**
- Password hashing: `argon2-cffi`  
- Sessions: Flask cookie `HttpOnly`, `SameSite='Lax'`
- CSRF tokens in all auth forms  
- Validation: trim inputs, require password length

**Done when:**
- Can register, log in, and log out
- Wrong password fails safely
- Cookies have `HttpOnly` and `SameSite=Lax`

---

## **Phase 3 – Reporting (Create/List/View)**

**Feature (how):**
- DB table: `reports(id, owner_id, title, description, severity, status)`  
  - `status`: `'public' | 'private' | 'closed'`
- Templates: `reports_list.html`, `report_new.html`
- Routes (`routes/reports.py`):  
  - `GET /reports` (list public + own private)  
  - `GET/POST /reports/new` (create new report)
- Basic table layout in CSS

**Security (what/why/how):**
- SQL injection: **parameterized queries only**
- XSS: auto-escape Jinja (`{{ title }}` not `|safe`)
- CSRF token in create form
- Authorization: limit visibility (no foreign private reports)

**Done when:**
- Users can create, list, and view their own reports
- Private reports stay private
- Random SQL input doesn’t break queries

---

## **Phase 4 – Uploads (Screenshots/Proofs)**

**Feature (how):**
- Add `/uploads/` directory (outside `/static/`)
- Form: `<input type="file" accept="image/*">` in `report_new.html`
- Routes:  
  - `POST /reports/new` handles uploads  
  - `GET /reports/file/<name>` serves via `send_file()`
- CSS: small thumbnail styling

**Security (what/why/how):**
- File validation: allow only `image/*` MIME types
- Filename: sanitize + randomize with `secure_filename` + `secrets.token_hex()`
- Access control: private report files accessible only to owner/admin
- Prevent direct public serving of `/uploads/`

**Done when:**
- Non-images or large files are rejected
- Private file URL blocked for other users

---

## **Phase 5 – Comments (Discussion)**

**Feature (how):**
- DB: `comments(id, report_id, author_id, body, created_at)`
- Template: add comment section in `report_detail.html`
- Route: `POST /reports/<id>/comment` (insert → redirect)

**Security (what/why/how):**
- XSS: auto-escape comment text
- CSRF token in comment form
- Authorization: only authenticated users; only owners/admins for private reports

**Done when:**
- Comments display correctly
- `<script>` tags render as text, not run
- Missing CSRF token blocks submission

---

## **Phase 6 – Admin Tools (Publish/Close/Delete)**

**Feature (how):**
- Admin role: add `role='admin'` in DB
- Admin page: `admin_dashboard.html` with status buttons  
  - Publish → `status='public'`  
  - Make Private → `status='private'`  
  - Close → `status='closed'`
- Routes (`routes/admin.py`):  
  - `GET /admin` (dashboard)  
  - `POST /admin/report/<id>/<action>` (publish, close, etc.)

**Security (what/why/how):**
- Authorization: `@require_admin` on all admin routes
- CSRF: tokens on all admin forms
- Input sanitization: validate `id` and `action`
- Optional import demo: if added, disable XML external entities

**Done when:**
- Admin can see all reports
- Buttons change status correctly
- Non-admin access denied to `/admin` routes

---

## **Phase 7 – Final Hardening (Headers, HTTPS, Review)**

**Feature (how):**
- Remove all inline JS → move to `static/js/main.js`
- Configure final CSP:  
  `default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:`
- Test under Gunicorn/Nginx + HTTPS

**Security (what/why/how):**
- Headers via `Flask-Talisman`: HSTS, Referrer-Policy, X-Frame-Options, X-Content-Type-Options
- Cookies: set `Secure=True` (production)
- Manual review: test XSS, CSRF, SQLi, file upload safety

**Done when:**
- No inline JS breaks under CSP
- HTTPS works, cookies marked Secure
- Manual “attack” tests all fail safely

---

## ✅ **Checklist Summary**

| Area | What You Verify |
|:------|:----------------|
| Templates | Proper escaping, no inline JS |
| Auth | Passwords hashed, cookies protected |
| Reports | SQLi prevented, visibility correct |
| Uploads | No file exposure, validated types |
| Comments | XSS & CSRF safe |
| Admin | Role restrictions enforced |
| Config | CSP/HSTS headers, secrets in `.env` |

---

## Endpoints

| Method | Path | Purpose |
|:--------|:------|:---------|
| `GET` | `/` | Home page |
| `GET/POST` | `/auth/register`, `/auth/login` | User auth |
| `POST` | `/auth/logout` | End session |
| `GET/POST` | `/reports/new` | Submit new report |
| `GET` | `/reports` | List reports |
| `GET` | `/reports/<id>` | View single report |
| `POST` | `/reports/<id>/comment` | Add comment |
| `GET` | `/reports/file/<name>` | Serve uploaded file (auth checked) |
| `GET/POST` | `/admin` | Admin dashboard |
| `POST` | `/admin/import` | Import XML/JSON report data |

---

## Quick Start

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
flask --app app run --debug
```

App runs on **http://localhost:5000**

---

## 📜 License & Purpose

This project is part of an academic course on **Security in Web Development**.  
The goal is to build a functional web system that demonstrates awareness of:
- Common web vulnerabilities (OWASP Top 10)
- Secure design patterns
- Proper authentication, authorization, and input handling

SecureLeak is not a product — it’s a **controlled learning environment** for demonstrating practical security principles.

MIT License — for educational and academic use.

---

## 👤 Author
**SecureLeak** — student project by [@marcus-rk](https://github.com/marcus-rk)  
*IT Architecture, 5th Semester*  
Security in Web Development, 2025
