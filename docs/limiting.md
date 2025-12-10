# Rate Limiting & DoS Protection

This document outlines the strategies implemented in SecureLeak to mitigate Denial of Service (DoS) attacks and abuse.

---

## 🛡️ Defense Strategy

We employ a multi-layered approach to protect application resources and ensure availability:

1.  **Application-Level Rate Limiting**: Restricts the frequency of requests from a single IP address.
2.  **Resource Quotas**: Enforces strict limits on data size to prevent resource exhaustion.

---

## 🚦 Rate Limiting Configuration

We use `Flask-Limiter` to track request rates per IP address.

### Global Limits
*   **200 requests per day**
*   **50 requests per hour**

These apply to all endpoints unless a specific override is defined.

### Specific Endpoint Limits

| Action | Route | Limit | Rationale |
| :--- | :--- | :--- | :--- |
| **Login** | `POST /auth/login` | **5 per minute** | Prevents brute-force password guessing attacks. |
| **Register** | `POST /auth/register` | **3 per hour** | Mitigates automated account creation (spam bots). |
| **Create Report** | `POST /reports/new` | **10 per hour** | Prevents content flooding and database bloat. |

### Implementation

```python
# security/limiter.py
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

# routes/auth.py
@auth_bp.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login_post() -> ResponseReturnValue:
    # ...
```

### User Experience
When a user exceeds a limit, the server responds with a **429 Too Many Requests** status code. A custom error page (`templates/errors/429.html`) is rendered to inform the user politely, maintaining the application's visual consistency.

---

## 📦 Resource Quotas

To prevent "Resource Exhaustion" attacks where an attacker sends massive payloads to crash the server:

*   **Max Request Body Size**: `MAX_CONTENT_LENGTH` is set to **3 MB**.
    *   This covers the file upload limit (2 MB) plus overhead for form fields and headers.
    *   Requests larger than this are rejected immediately by Flask with a 413 error.

```python
# app.py
app.config.from_mapping(
    # ...
    MAX_CONTENT_LENGTH=3 * 1024 * 1024,  # 3 MB
)
```

*   **File Uploads**:
    *   Strictly validated for file type (PNG, JPG, GIF) and MIME type.
    *   **Pixel Dimensions**: Images are limited to **2048x2048 pixels** to prevent "Decompression Bomb" attacks that exhaust server RAM.
    *   Files are renamed upon storage to prevent directory traversal or overwriting critical files.

---

## 🔮 Future Improvements (Production)

For a production environment, we would enhance this by:
*   Moving rate limit storage to **Redis** to support multiple worker processes.
*   Implementing **Nginx** rate limiting for faster rejection at the infrastructure level.
*   Using a **CDN** (like Cloudflare) for distributed DDoS protection.
