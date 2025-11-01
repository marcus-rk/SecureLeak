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

---

## Project Overview

**SecureLeak** is a simplified bug tracker where developers (users) can submit **vulnerability reports** to admins.  
Admins review, comment on, close, or delete reports (e.g., spam).  
Reports can be **public** (for learning) or **private** (internal).  
Optional **file uploads** allow screenshots or proof-of-concepts.  

It’s intentionally **meta** — a secure app *about* vulnerabilities, protected against the same threats it demonstrates.

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

## 📂-Structure

```
secureleak/
├─ app.py               # Flask setup, routes, CSRF, headers
├─ db.py                # DB connection & helper functions
├─ .env                 # SECRET_KEY, DB path, etc.
├─ requirements.txt
├─ /routes/             # Blueprints: auth.py, reports.py, admin.py
├─ /templates/          # Jinja2 templates (SSR)
├─ /static/             # css/, js/
└─ /uploads/            # stored files (not publicly served)
```

---

## Development Outline

### Phase 1 – Setup
- Flask app, Talisman (security headers), CSRFProtect.
- Base templates and static assets.

### Phase 2 – Authentication
- Register/login/logout.
- Argon2 password hashing.
- Session cookies: `HttpOnly`, `SameSite=Lax`.

### Phase 3 – Reporting
- CRUD reports with parameterized queries.
- Output escaping and visibility rules.

### Phase 4 – Uploads
- Safe upload handling.
- Serve files through access-controlled route.

### Phase 5 – Comments
- Add comment threads.
- Escape content + enforce CSRF.

### Phase 6 – Admin Tools
- Role enforcement, triage, close, delete, import (XXE-safe).

### Phase 7 – Final Hardening
- Review headers, CSP, HTTPS setup.

---

## Endpoints

| Method | Path | Purpose |
|:--------|:------|:---------|
| `GET` | `/` | Home page |
| `GET/POST` | `/register`, `/login` | User auth |
| `POST` | `/logout` | End session |
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
python -m venv venv
source venv/bin/activate
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
