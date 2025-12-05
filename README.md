# SecureLeak

> *A minimal, educational bug tracker built to study and prevent web vulnerabilities.*

![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0.3-black?logo=flask)
![SQLite](https://img.shields.io/badge/SQLite-3-07405E?logo=sqlite&logoColor=white)
![Argon2](https://img.shields.io/badge/Argon2_cffi-23.1.0-7952B3)
![FlaskWTF](https://img.shields.io/badge/Flask_WTF-1.2.1-green)
![FlaskTalisman](https://img.shields.io/badge/Flask_Talisman-1.0.0-orange)
![FlaskLimiter](https://img.shields.io/badge/Flask_Limiter-3.8.0-red)
![Pillow](https://img.shields.io/badge/Pillow-10.3.0-yellow)
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
- Roles & admin area: [docs/roles.md](docs/roles.md)
- Rate Limiting & DoS: [docs/limiting.md](docs/limiting.md)
- Audit Logging: [docs/audit_logging.md](docs/audit_logging.md)
- Image Sanitization: [docs/image_sanitization.md](docs/image_sanitization.md)
- Security.txt: [docs/security_txt.md](docs/security_txt.md)

---

## Core Security Focus

| Threat | Mitigation |
|:--------|:------------|
| SQL Injection | Parameterized queries |
| XSS | Auto-escaped templates, CSP, HttpOnly cookies |
| CSRF | Flask-WTF CSRF tokens, SameSite=Lax |
| DoS / Abuse | Rate Limiting (Flask-Limiter), Resource Quotas |
| File Upload Abuse | Pillow Sanitization (strips metadata), MIME validation, random names |
| Non-repudiation | Audit Logging (who, what, when) |
| Brute Force | Rate limiting (5/min), Argon2id hashing, Common password check |
| Session Hijacking | HttpOnly + SameSite cookies, Session regeneration |
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
## 📂 Project Structure

```
SecureLeak/
├─ app.py                  # App factory: config, CSRF, security headers, blueprints, error handlers
├─ requirements.txt        # Python dependencies
├─ pytest.ini              # pytest configuration
├─ README.md               # Project guide + documentation links
├─ docs/                   # Detailed documentation (Architecture, Security, Auth, etc.)
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
│  ├─ auth.py              # Login, register, logout (Argon2id, CSRF, PRG, Audit)
│  ├─ reports.py           # List/view/new reports (Audit, Sanitization)
│  └─ admin.py             # Admin dashboard
│
├─ security/               # Security helpers and selfmade decorators
│  ├─ 10k-common-passwords # List of common passwords for checks
│  ├─ audit.py             # Audit logging logic (writes to instance/audit.log)
│  ├─ auth_utils.py        # Argon2id hasher, email normalize, common password check
│  ├─ decorators.py        # login_required, role checks
│  ├─ limiter.py           # Rate limiting configuration (Flask-Limiter)
│  ├─ reports_access.py    # Shared report visibility checks
│  ├─ security.txt         # Vulnerability disclosure content
│  └─ uploads.py           # Upload validation, Pillow sanitization, storage logic
│
├─ templates/              # Jinja2 templates (auto-escaped)
│  ├─ layout.html          # Base layout + nav + flash messages
│  ├─ ...                  # Feature templates
│  └─ errors/              
│     ├─ 400.html          # Bad request (e.g., CSRF)
│     ├─ 404.html          # Not found
│     ├─ 429.html          # Too Many Requests (Rate Limit)
│     └─ 500.html          # Server error
│
├─ static/                 # Front-end assets (CSS, JS, Icons)
│
├─ tests/                  # Pytest test-suite
│  ├─ conftest.py          # App fixture (temp DB per run)
│  ├─ auth/                # Auth tests
│  ├─ security/            # Security tests (Headers, CSP)
│  └─ repository/          # Repository CRUD tests
│
├─ uploads/                # Uploaded files (kept outside /static)
└─ instance/               # Runtime data (DB, logs)
  ├─ secureleak.sqlite     # SQLite database
  └─ audit.log             # Security audit log
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

## 🧭 Development Roadmap

The project was built in phases to ensure security was integrated at every step, not added as an afterthought.

| Phase | Feature Focus | Security Implementation |
|:---|:---|:---|
| **1. Setup** | Skeleton, DB, Routes | **Secure Headers** (CSP, HSTS), **CSRF** protection (Flask-WTF), Secrets management (.env) |
| **2. Auth** | Register, Login, Sessions | **Argon2id** hashing, **Common Password** check, HttpOnly/SameSite cookies |
| **3. Reports** | CRUD, Visibility | **Parameterized Queries** (SQLi), **Access Control** (Private/Public logic), Auto-escaping (XSS) |
| **4. Uploads** | File attachments | **Pillow Sanitization** (Metadata stripping), Random filenames, Non-public storage |
| **5. Comments** | Discussion threads | **Input Trimming**, Strict CSP for inline scripts, PRG pattern |
| **6. Admin** | Dashboard, Status management | **Role-Based Access Control** (RBAC), Admin-only routes |
| **7. Hardening** | Production readiness | **Rate Limiting** (DoS protection), **Audit Logging**, Security.txt |

---

## How to Run

### Prerequisites
- Python 3.12+
- pip

### Installation

1. **Clone and Setup**
   ```bash
   git clone https://github.com/marcus-rk/SecureLeak.git
   cd SecureLeak
   python3 -m venv venv
   source venv/bin/activate  
   pip install -r requirements.txt
   pip install --upgrade pip
   ```

2. **Initialize Database**
   The database is automatically initialized on the first run.
   Optionally, you can seed it with demo data:
   ```bash
   python -m seed.seed_runner
   ```
   *Note: Seeded users have password `password123`.*

3. **Run the Application**
   ```bash
   flask --app app run --debug
   ```
   Access at: `http://localhost:5000`

### Running with HTTPS (Local)
To test secure cookies and headers properly:
```bash
# Install mkcert
brew install mkcert nss
mkcert -install
mkcert localhost 127.0.0.1

# Run with certs
flask --app app run --cert=localhost+1.pem --key=localhost+1-key.pem
```
Access at: `https://127.0.0.1:5000`

---

## 🧪 Testing

The project includes a comprehensive test suite using `pytest`.

```bash
# Run all tests
pytest

# Run specific category
pytest tests/security/
pytest tests/auth/
```

**Test Coverage:**
- **Auth**: Login, Register, Logout, Session management.
- **Security**: CSP headers, HSTS, Rate Limiting, Password hashing.
- **Repository**: Database CRUD operations.
- **Uploads**: File type validation, sanitization.

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
| `GET` | `/reports/<id>/image/<name>` | Serve uploaded file (auth checked) |
| `GET` | `/admin` | Admin dashboard (list all reports) |
| `POST` | `/admin/reports/<id>/status` | Change status to public/private/closed |
| `GET` | `/.well-known/security.txt` | Security policy & disclosure |

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
