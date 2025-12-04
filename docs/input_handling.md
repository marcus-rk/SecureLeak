# User Input Handling & Security Mitigations

This document details how **SecureLeak** handles untrusted user input throughout the application lifecycle. It specifically addresses how we prevent malicious characters (like `<`, `>`, `'`, `"`) from causing vulnerabilities such as Cross-Site Scripting (XSS) or SQL Injection.

---

## 🛡️ Core Philosophy: "Never Trust User Input"

Every piece of data coming from the client (forms, headers, cookies, files) is treated as untrusted. We rely on a multi-layered defense strategy (Defense-in-Depth) rather than a single check.

---

## 1. Input Validation (The First Line of Defense)

Before processing data, we validate that it meets expected formats.

- **Type Enforcement**: We cast inputs to their expected types immediately (e.g., `int(report_id)`).
- **Length Limits**: Inputs are checked for length to prevent database truncation issues or Denial of Service (DoS).
  - *Example*: Comments are limited to 2000 characters.
- **Allowlisting**: For critical fields like `severity` or `status`, we only accept values from a predefined set (`{'low', 'medium', 'high'}`).

---

## 2. SQL Injection Prevention (Database Layer)

**Threat**: Attackers input SQL commands (e.g., `' OR 1=1 --`) to manipulate database queries.

**Mitigation**: **Parameterized Queries**
We **never** concatenate user strings directly into SQL queries. Instead, we use the database driver's placeholder system (`?`).

**How it works**:
When a user inputs `admin' --`, the database treats it strictly as the *value* of a text field, not as executable SQL code.

```python
# ✅ Secure: Parameterized
db.execute("INSERT INTO reports (title) VALUES (?)", (user_input,))

# ❌ Insecure: String Concatenation (NEVER USED)
# db.execute(f"INSERT INTO reports (title) VALUES ('{user_input}')")
```

---

## 3. Cross-Site Scripting (XSS) Prevention (Output Layer)

**Threat**: Attackers input HTML/JavaScript (e.g., `<script>alert('hacked')</script>`) to execute code in other users' browsers.

**Mitigation A: Context-Aware Auto-Escaping (Jinja2)**
This is our **primary defense**. Flask's template engine (Jinja2) automatically converts special characters into their safe HTML entity equivalents before rendering.

| User Input | Rendered HTML Source | Browser Display | Result |
|:---|:---|:---|:---|
| `<` | `&lt;` | `<` | Safe Text |
| `>` | `&gt;` | `>` | Safe Text |
| `&` | `&amp;` | `&` | Safe Text |
| `"` | `&#34;` | `"` | Safe Text |
| `'` | `&#39;` | `'` | Safe Text |

*   **No `|safe` Filter**: We strictly avoid using the `|safe` filter on user-controlled data, which would bypass this protection.

**Mitigation B: Content Security Policy (CSP)**
This is our **safety net**. Even if an attacker bypasses auto-escaping, the browser is instructed to block unauthorized scripts.

Configured in `app.py` via `Flask-Talisman`:

```python
content_security_policy={
    # Only allow scripts from our own domain
    "script-src": "'self'",
    # Block all inline scripts (<script>...</script>) and event handlers (onclick=...)
    # (Implicitly blocked because 'unsafe-inline' is NOT present)
    "style-src": "'self'",
    # Block <object>, <embed>, <applet>
    "object-src": "'none'",
    # Prevent forms from submitting to external sites
    "form-action": "'self'",
    # Prevent <base> tag hijacking
    "base-uri": "'self'"
}
```

---

## 4. File Upload Handling

**Threat**: Uploading malicious files (e.g., PHP shells, SVGs with JS).

**Mitigations**:
1.  **Extension Allowlist**: Only `.png`, `.jpg`, `.jpeg`, `.gif`.
2.  **MIME Type Check**: Must start with `image/`.
3.  **Content Sanitization**: We use **Pillow** to re-encode images. This strips malicious metadata (EXIF) and ensures the file is truly an image.
4.  **Filename Sanitization**: Original filenames are discarded. We generate a random secure hash for storage.
5.  **Storage Location**: Uploads are stored outside the `static/` folder and served via a controlled route, preventing direct execution.

---

## Summary of Character Handling

| Character | Potential Attack | How it is Mitigated |
|:---|:---|:---|
| `<` `>` | XSS (HTML Injection) | **Jinja2 Auto-escaping** converts to `&lt;` `&gt;`. |
| `'` `"` | SQL Injection / XSS | **Parameterized Queries** (DB) & **Auto-escaping** (HTML). |
| `;` | SQL Injection | **Parameterized Queries**. |
| `/` `\` | Path Traversal | **secure_filename** & Random filenames for uploads. |
