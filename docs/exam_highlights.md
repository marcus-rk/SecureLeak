# Exam Report Highlights & Codebase Reflections

This document is designed to assist in writing the final exam report. It highlights key security implementations in **SecureLeak**, maps them to OWASP vulnerabilities, and provides technical reflections suitable for academic discussion.

---

## 1. Injection Attacks (SQLi & XSS)

### 🛡️ SQL Injection (SQLi)
**Concept**: Preventing attackers from manipulating database queries via input fields.
**Implementation**: `repository/reports_repo.py`
**Key Snippet**:
```python
# repository/reports_repo.py
cur = db.execute(
    "INSERT INTO reports (owner_id, title, description, severity, status) VALUES (?, ?, ?, ?, ?)",
    (owner_id, title, description, severity, status),
)
```
**Reflection for Report**:
> "Instead of sanitizing input (which is error-prone), we use **Parameterized Queries**. This ensures the database engine treats user input strictly as data, never as executable code. This completely neutralizes classic SQLi attacks like `' OR 1=1 --`."

### 🛡️ Cross-Site Scripting (XSS)
**Concept**: Preventing malicious scripts from running in a victim's browser.
**Implementation**: `app.py` (CSP) & Jinja2 (Auto-escaping).
**Key Snippet**:
```python
# app.py - Content Security Policy (Defense-in-Depth)
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

## 2. Input Validation & Broken Access Control

### 🛡️ Input Validation (Allowlisting)
**Concept**: Only accepting known-good input.
**Implementation**: `routes/reports.py`
**Key Snippet**:
```python
# routes/reports.py
# Allowlisting valid values
if severity not in {"low", "medium", "high"}:
    return _report_bad_request("Invalid severity.")

# Type enforcement is handled by Flask routing:
# @reports_bp.route("/<int:report_id>", methods=["GET"])
```
**Reflection for Report**:
> "Input validation is the first line of defense. By using **Allowlisting** (only accepting known good values) rather than Blocklisting (trying to guess bad values), we significantly reduce the attack surface. If the data isn't 'low', 'medium', or 'high', it is rejected immediately."

### 🛡️ Broken Access Control (IDOR)
**Concept**: Preventing users from accessing resources they don't own.
**Implementation**: `security/reports_access.py`
**Key Snippet**:
```python
# security/reports_access.py
def is_report_viewable(report: dict, user_id: Optional[int], role: Optional[str] = None) -> bool:
    if not report:
        return False
    
    # Admin override (can see everything)
    if role == "admin":
        return True

    status = report.get("status")
    if status == "public":
        return True
    if status == "private":
        return user_id is not None and user_id == report.get("owner_id")
    # Unknown status: default deny
    return False
```
**Reflection for Report**:
> "We implement **Attribute-Based Access Control (ABAC)** logic at the data retrieval level. It is not enough to check if a user is logged in; we must check if *this* user owns *this* specific resource. This prevents IDOR attacks where valid IDs are guessed."

---

## 3. Cryptographic Failures

### 🛡️ Password Hashing (Argon2id)
**Concept**: Storing passwords so that a database leak does not reveal them.
**Implementation**: `security/auth_utils.py`
**Key Snippet**:
```python
# security/auth_utils.py
def build_hasher() -> PasswordHasher:
    return PasswordHasher(
        time_cost=3,
        memory_cost=65536,  # 64 MiB
        parallelism=2,
        hash_len=32,
        salt_len=16,
    )
```
**Reflection for Report**:
> "We chose **Argon2id** (the OWASP recommended algorithm) over bcrypt or PBKDF2. Argon2id is memory-hard, making it significantly more resistant to GPU/ASIC brute-force attacks. We explicitly configured parameters (64MB RAM cost) to balance security with server performance."

---

## 4. File Upload Vulnerabilities

### 🛡️ Malicious File Execution
**Concept**: Preventing users from uploading shells (`shell.php`) or XSS payloads in images.
**Implementation**: `security/uploads.py`
**Key Snippet**:
```python
# security/uploads.py
ext = get_ext(file.filename or "")
rnd = secrets.token_hex(16) + ext
dest_name = secure_filename(rnd)

# ...

with Image.open(file) as img:
    # Convert to RGB to handle PNGs with transparency if saving as JPEG,
    # but here we keep original format. Pillow saves without metadata by default.
    # We create a new image to ensure no hidden data is copied over.
    data = list(img.getdata())
    clean_img = Image.new(img.mode, img.size)
    clean_img.putdata(data)
    clean_img.save(str(dest_path))
```
**Reflection for Report**:
> "File uploads are dangerous. We mitigate this by: 1) **Allowlisting** extensions, 2) **Randomizing** filenames to prevent overwriting or directory traversal, and 3) **Re-encoding** the image using Pillow. This 'sanitization by reconstruction' ensures that even if a file *looks* like a JPG but contains hidden code, that code is stripped out during the save process."

---

## 5. Identification and Authentication Failures

### 🛡️ Session Fixation & Hijacking
**Concept**: Preventing attackers from stealing or setting a user's session ID.
**Implementation**: `routes/auth.py` & `app.py`
**Key Snippet**:
```python
# routes/auth.py
# Session fixation defense and identity establishment
_establish_session(user)

# routes/auth.py
def _establish_session(user: dict) -> None:
    session.clear()
    session["user_id"] = user["id"]

# app.py
app.config.from_mapping(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=not app.debug,
)
```
**Reflection for Report**:
> "To prevent **Session Fixation**, we regenerate the session ID (`session.clear()`) immediately upon login. To prevent **Session Hijacking** via XSS, we set the `HttpOnly` flag. We also use `SameSite=Lax` to provide a robust default defense against CSRF."

### 🛡️ Common Password Check (NIST Guideline)
**Concept**: Preventing users from choosing easily guessable passwords.
**Implementation**: `security/auth_utils.py`
**Key Snippet**:
```python
def is_common_password(password: str) -> bool:
    common_set = _load_common_passwords() # 10k most common
    return password in common_set
```
**Reflection for Report**:
> "Following NIST SP 800-63B guidelines, we check new passwords against a list of the 10,000 most common passwords. This is more effective than arbitrary complexity rules (like 'must contain a symbol'), which often lead to predictable patterns like 'Password1!'."

---

## 6. Security Misconfiguration & Outdated Components

### 🛡️ Security Headers
**Concept**: Instructing the browser to enforce security features.
**Implementation**: `app.py` (Flask-Talisman)
**Key Headers**:
*   `Strict-Transport-Security` (HSTS): Forces HTTPS.
*   `X-Content-Type-Options: nosniff`: Prevents MIME-sniffing attacks.
*   `Frame-Ancestors: 'none'`: Prevents Clickjacking (UI Redressing).

### 🛡️ Dependency Management
**Concept**: Ensuring third-party libraries are known and secure.
**Implementation**: `requirements.txt`, `requirements-dev.txt`, `.github/workflows/ci.yml`
**Reflection for Report**:
> "We pin every direct dependency to an exact version: runtime packages in `requirements.txt`, test and lint tools in `requirements-dev.txt`, and CI actions to full commit SHAs. Pinning prevents 'supply chain attacks' where a future update might introduce a vulnerability. We can audit these specific versions against CVE databases."

---

## 7. Security Logging & Monitoring (OWASP A09)

### 🛡️ Audit Logging
**Concept**: Recording critical actions for non-repudiation and incident response.
**Implementation**: `security/audit.py`
**Key Snippet**:
```python
formatter = logging.Formatter(
    "[%(asctime)s] [%(ip)s] User:%(user_id)s Action:%(action)s Target:%(target_id)s"
)
```
**Reflection for Report**:
> "We implemented a dedicated audit log separate from standard debug logs. It records WHO (User ID), DID WHAT (Action), TO WHAT (Target ID), and FROM WHERE (IP). This is crucial for forensics. Events such as logins, registrations and report creation are traceable to a user and IP. The log is a plain file (`instance/audit.log`), so it is append-only by convention, not tamper-proof, and admin status changes are not logged yet."

---

## 8. Server-Side Request Forgery (SSRF) & DoS

### 🛡️ Rate Limiting (DoS Protection)
**Concept**: Preventing brute-force attacks and resource exhaustion.
**Implementation**: `security/limiter.py`
**Key Snippet**:
```python
@limiter.limit("5 per minute")
def login_post(): ...
```
**Reflection for Report**:
> "We use **Flask-Limiter** to enforce strict quotas on sensitive endpoints. Login is limited to 5 attempts per minute to stop brute-force attacks. Report creation is limited to 10 per hour to prevent spam/DoS. This protects the application's availability."

---

## 9. Automated Security Testing (DevSecOps)

### 🛡️ CI/CD Pipeline (`.github/workflows/ci.yml`)
**Concept**: Shifting security left by automating checks on every commit.
**Implementation**: GitHub Actions workflow.
**Key Tools**:
*   **Bandit**: Static Application Security Testing (SAST) for Python. Scans for common flaws (e.g., hardcoded secrets, unsafe exec).
*   **pip-audit**: Checks installed dependencies against known CVE databases.
*   **Ruff**: Enforces code quality and linting standards.
**Reflection for Report**:
> "Security isn't a one-time check. We implemented a **DevSecOps** pipeline that runs **Bandit** (SAST) and **pip-audit** (SCA) on every push and pull request that changes Python files, `requirements.txt` or `requirements-dev.txt`. This helps ensure that no known vulnerabilities or insecure coding patterns (like `eval()`) are merged into the main branch. The pytest job in CI runs the full test suite."

### 🛡️ Security Unit Tests (`tests/security/`)
**Concept**: Verifying that security controls actually work.
**Implementation**: `tests/security/test_headers.py`
**Key Snippet**:
```python
def test_csp_header_is_restrictive_on_login(client):
    resp = client.get("/auth/login")
    csp = resp.headers.get("Content-Security-Policy", "")
    assert "default-src 'self'" in csp
```
**Reflection for Report**:
> "We don't just assume our headers are set; we test them. Our test suite asserts that the **Content-Security-Policy** is present and restrictive on critical endpoints. This prevents regression where a developer might accidentally disable security headers."

---

## 10. Advanced Access Control Patterns

### 🛡️ Custom Role Decorators (Defense-in-Depth)
**Concept**: Ensuring high-privilege actions are doubly verified.
**Implementation**: `security/decorators.py`
**Key Snippet**:
```python
# Defense-in-depth: verify DB role for admins
if required == "admin":
    user = get_user_by_id(int(uid))
    if user["role"] != "admin":
        abort(404)
```
**Reflection for Report**:
> "For standard users, we trust the session role for performance. But for **Admins**, we implement a 'paranoid' check: we fetch the user's role from the database on *every* admin request and on every report page, comment and image request. This ensures that if an admin's privileges are revoked, they lose access immediately, even if their session is still active."

---

## 11. CSRF Protection Details

### 🛡️ Synchronizer Token Pattern
**Concept**: Preventing attackers from forcing users to submit unwanted forms.
**Implementation**: `app.py` (Flask-WTF) & Templates.
**Key Snippet**:
```python
# app.py
csrf = CSRFProtect()
csrf.init_app(app)

# templates/login.html
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
```
**Reflection for Report**:
> "We use the **Synchronizer Token Pattern** via Flask-WTF. Every form includes a hidden, unique, per-session token. The server rejects any POST request that lacks this token. This makes it impossible for an attacker to forge a request from a malicious site, as they cannot read the user's token due to the Same-Origin Policy."

---

## 12. Error Handling & Information Leakage

### 🛡️ Generic Error Pages
**Concept**: Preventing stack traces from revealing internal logic.
**Implementation**: `app.py`
**Key Snippet**:
```python
@app.errorhandler(500)
def internal_error(_e):
    return render_template("errors/500.html"), 500
```
**Reflection for Report**:
> "We override the default Flask error handlers to show generic HTML pages. This prevents **Information Leakage** (like stack traces or database schemas) which could help an attacker map the system. Even 404s are standardized to avoid revealing which resources exist."

---

## 13. Case Study: Defense-in-Depth (The "Swiss Cheese" Model)

**Scenario**: A user uploads a screenshot of a vulnerability.
**Why this matters**: File uploads are a high-risk feature (RCE, XSS, DoS).
**The Layers of Defense**:
1.  **Network Layer**: Request is encrypted via **HTTPS/HSTS** (prevents interception).
2.  **Application Layer (DoS)**: **Rate Limiter** checks if user exceeded 10 uploads/hour.
3.  **Session Layer**: **CSRF Token** verified (prevents forced upload). **Auth Decorator** verifies login.
4.  **Input Layer**:
    *   **Extension Check**: Must be `.png`, `.jpg`, etc.
    *   **MIME Check**: Must be `image/*`.
    *   **Size Check**: Max 2MB (prevents disk exhaustion).
5.  **Processing Layer**: **Pillow Sanitization** re-encodes the image, stripping malicious metadata or polyglot code.
6.  **Storage Layer**: Filename is **Randomized** (prevents path traversal and overwrites).
7.  **Data Layer**: **Audit Log** records the upload action.
8.  **Presentation Layer**: Image served via `send_from_directory` with **CSP** headers (prevents XSS if sanitization failed).

**Reflection for Report**:
> "No single control is perfect. By stacking these 8 layers, we ensure that even if an attacker bypasses one (e.g., spoofs the MIME type), the next layer (Pillow sanitization) catches them. This illustrates the **Defense-in-Depth** principle in a practical, real-world feature."

---

## 14. Critical Reflection: Future Improvements

**Concept**: Acknowledging limitations is a sign of maturity.
**What is missing?**:
1.  **Multi-Factor Authentication (MFA)**: Currently, a stolen password equals a compromised account. TOTP (Google Authenticator) would mitigate this.
2.  **Database Scalability**: SQLite is excellent for development but locks the file during writes. For a high-traffic bug tracker, migrating to **PostgreSQL** would be necessary.
3.  **Email Verification**: We currently trust the email provided. A "Verify your email" loop would prevent fake accounts.

---

## 15. Architectural Reflections (The "Why")

### 💡 KISS Principle (Keep It Simple, Stupid)
> "Complexity is the worst enemy of security. By using **SQLite** and standard **Flask** patterns, we reduced the attack surface. A complex microservices architecture might have introduced more vulnerabilities (e.g., insecure inter-service communication) than it solved for this scale."

### 💡 Why Flask?
> "We chose Flask over Django for this educational project because Flask is 'explicit'. In Django, much of the security (CSRF, Auth) happens 'magically' in the background. In Flask, we had to manually configure `Talisman`, `CSRFProtect`, and a custom session-based `@login_required` decorator, which demonstrates a deeper understanding of *how* these mechanisms actually work."

### 💡 SSR (Server-Side Rendering) vs. CSR (Client-Side Rendering)
> "We deliberately chose **SSR** (Flask/Jinja2) over a CSR framework (React/Vue) for security reasons:
> 1.  **Reduced Data Exposure**: In CSR, APIs often over-fetch data (sending full user objects), relying on the frontend to hide it. In SSR, the server renders *only* what the user is allowed to see, preventing data leaks via network inspection.
> 2.  **Session Security**: CSR apps often store tokens in `localStorage` (vulnerable to XSS). We use `HttpOnly` cookies, which are invisible to JavaScript, neutralizing token theft even if XSS occurs.
> 3.  **Simpler Access Control**: With SSR, we don't need complex CORS configurations (a common source of misconfiguration). Everything is served from `'self'`, simplifying our Content Security Policy."

### 💡 Defense-in-Depth
> "We never rely on a single control. For example, XSS is blocked by **Auto-escaping** AND **CSP**. CSRF is blocked by **SameSite cookies** AND **CSRF Tokens**. Admin access is checked in the **Session** AND verified against the **Database** on every request. If one layer fails, the next catches the attack."

### 💡 Audit Logging
> "Security is not just prevention, but detection. We implemented `security/audit.py` to log critical events (`LOGIN_SUCCESS`, `LOGIN_FAILED`, `LOGOUT`, `REGISTER_USER`, `CREATE_REPORT`). This ensures **Non-repudiation**: users cannot deny actions they performed, and admins can investigate incidents."
