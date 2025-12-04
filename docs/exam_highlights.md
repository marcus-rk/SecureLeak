# Exam Report Highlights & Codebase Reflections

This document is designed to assist in writing the final exam report. It highlights key security implementations in **SecureLeak**, maps them to OWASP vulnerabilities, and provides technical reflections suitable for academic discussion.

---

## 1. Injection Attacks (SQLi & XSS)

### 🛡️ SQL Injection (SQLi)
**Concept**: Preventing attackers from manipulating database queries via input fields.
**Implementation**: `repository/reports_repo.py`
**Key Snippet**:
```python
# ✅ Parameterized Query (The "Question Mark" Style)
cur = db.execute(
    "INSERT INTO reports (title, ...) VALUES (?, ...)",
    (title, ...)
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
content_security_policy={ 
    "default-src": "'self'", 
    "script-src": "'self'",  # No inline scripts allowed!
    "object-src": "'none'", 
    "base-uri": "'self'"
}
```
**Reflection for Report**:
> "We employ a dual-layer defense. **Layer 1** is Jinja2's context-aware auto-escaping, which converts `<script>` to `&lt;script&gt;`. **Layer 2** is a strict **Content Security Policy (CSP)** that forbids inline JavaScript (`unsafe-inline`). Even if an attacker bypasses the auto-escaping, the browser will refuse to execute the injected script."

### 🛡️ Input Validation (Pre-Defense)
**Concept**: Rejecting malformed data before it reaches the database or logic.
**Implementation**: `routes/reports.py`
**Key Snippet**:
```python
# Allowlisting valid values
if severity not in {"low", "medium", "high"}:
    return _report_bad_request("Invalid severity.")

# Type enforcement
report_id = int(request.view_args['report_id'])
```
**Reflection for Report**:
> "Input validation is the first line of defense. By using **Allowlisting** (only accepting known good values) rather than Blocklisting (trying to guess bad values), we significantly reduce the attack surface. If the data isn't 'low', 'medium', or 'high', it is rejected immediately."

---

## 2. Broken Access Control (IDOR & RBAC)

### 🛡️ Insecure Direct Object References (IDOR)
**Concept**: Preventing User A from viewing User B's private data by changing an ID in the URL (`/reports/123`).
**Implementation**: `security/reports_access.py`
**Key Snippet**:
```python
def is_report_viewable(report, user_id):
    if report['status'] == 'public':
        return True
    # Private: only owner or admin can see
    return user_id and (report['owner_id'] == user_id or session.get('role') == 'admin')
```
**Reflection for Report**:
> "We implement **Attribute-Based Access Control (ABAC)** logic at the data retrieval level. It is not enough to check if a user is logged in; we must check if *this* user owns *this* specific resource. This prevents IDOR attacks where valid IDs are guessed."

---

## 3. Cryptographic Failures (Password Storage)

### 🛡️ Hashing Strategy
**Concept**: Storing passwords securely to resist cracking if the DB is leaked.
**Implementation**: `security/auth_utils.py`
**Key Snippet**:
```python
PasswordHasher(
    time_cost=3,        # Iterations
    memory_cost=65536,  # 64 MiB RAM usage
    parallelism=2,      # Threads
    hash_len=32,
    salt_len=16
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
# 1. Randomize Filename (Prevents path traversal & overwrites)
dest_name = secure_filename(secrets.token_hex(16) + ext)

# 2. Content Sanitization (Pillow)
with Image.open(file) as img:
    # Re-writing the image strips EXIF metadata and malicious payloads
    clean_img = Image.new(img.mode, img.size)
    clean_img.putdata(list(img.getdata()))
    clean_img.save(dest_path)
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
session.clear()  # Destroy old session (Fixation defense)
session["user_id"] = user["id"]

# app.py
SESSION_COOKIE_HTTPONLY = True  # JS cannot read cookie
SESSION_COOKIE_SAMESITE = "Lax" # CSRF protection
SESSION_COOKIE_SECURE = True    # HTTPS only
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
**Implementation**: `requirements.txt`
**Reflection for Report**:
> "We pin all dependencies to specific versions in `requirements.txt`. This prevents 'supply chain attacks' where a future update might introduce a vulnerability. We can audit these specific versions against CVE databases."

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
> "We implemented a dedicated audit log separate from standard debug logs. It records WHO (User ID), DID WHAT (Action), TO WHAT (Target ID), and FROM WHERE (IP). This is crucial for forensics. If a malicious admin deletes a report, we have an immutable record of that action."

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

## 10. Automated Security Testing (DevSecOps)

### 🛡️ CI/CD Pipeline (`.github/workflows/ci.yml`)
**Concept**: Shifting security left by automating checks on every commit.
**Implementation**: GitHub Actions workflow.
**Key Tools**:
*   **Bandit**: Static Application Security Testing (SAST) for Python. Scans for common flaws (e.g., hardcoded secrets, unsafe exec).
*   **pip-audit**: Checks installed dependencies against known CVE databases.
*   **Ruff**: Enforces code quality and linting standards.
**Reflection for Report**:
> "Security isn't a one-time check. We implemented a **DevSecOps** pipeline that runs **Bandit** (SAST) and **pip-audit** (SCA) on every pull request. This ensures that no known vulnerabilities or insecure coding patterns (like `eval()`) are merged into the main branch."

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

## 11. Advanced Access Control Patterns

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
> "For standard users, we trust the session role for performance. But for **Admins**, we implement a 'paranoid' check: we fetch the user's role from the database on *every* request. This ensures that if an admin's privileges are revoked, they lose access immediately, even if their session is still active."

---

## 12. CSRF Protection Details

### 🛡️ Synchronizer Token Pattern
**Concept**: Preventing attackers from forcing users to submit unwanted forms.
**Implementation**: `app.py` (Flask-WTF) & Templates.
**Key Snippet**:
```python
# app.py
csrf = CSRFProtect(app)

# templates/login.html
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
```
**Reflection for Report**:
> "We use the **Synchronizer Token Pattern** via Flask-WTF. Every form includes a hidden, unique, per-session token. The server rejects any POST request that lacks this token. This makes it impossible for an attacker to forge a request from a malicious site, as they cannot read the user's token due to the Same-Origin Policy."

---

## 13. Error Handling & Information Leakage

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

## 14. Architectural Reflections (The "Why")

### 💡 KISS Principle (Keep It Simple, Stupid)
> "Complexity is the worst enemy of security. By using **SQLite** and standard **Flask** patterns, we reduced the attack surface. A complex microservices architecture might have introduced more vulnerabilities (e.g., insecure inter-service communication) than it solved for this scale."

### 💡 Defense-in-Depth
> "We never rely on a single control. For example, XSS is blocked by **Auto-escaping** AND **CSP**. CSRF is blocked by **SameSite cookies** AND **CSRF Tokens**. Admin access is checked in the **Session** AND verified against the **Database** on every request. If one layer fails, the next catches the attack."

### 💡 Audit Logging
> "Security is not just prevention, but detection. We implemented `security/audit.py` to log critical events (Login, Register, Report Access). This ensures **Non-repudiation**—users cannot deny actions they performed, and admins can investigate incidents."
