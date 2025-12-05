# Audit Logging

This document explains the audit logging system implemented in SecureLeak to ensure accountability and non-repudiation.

---

## 🎯 Purpose

Audit logs provide a chronological record of security-relevant activities. They answer "who did what, when, and from where," which is critical for:
1.  **Forensics**: Investigating security incidents (e.g., unauthorized access).
2.  **Compliance**: Meeting standards that require tracking user actions.
3.  **Monitoring**: Detecting suspicious patterns (e.g., repeated login failures).

---

## ⚙️ Implementation

The logging logic is encapsulated in `security/audit.py`. We use a dedicated logger separate from the main application debug logs.

### Log Format
We use a structured text format for simplicity and readability:
```text
[TIMESTAMP] [IP] User:USER_ID Action:ACTION_NAME Target:TARGET_ID
```

### Code Snippet

```python
# security/audit.py
def log_security_event(
    action: str,
    user_id: Optional[int] = None,
    target_id: Optional[str] = None,
    ip: Optional[str] = None,
) -> None:
    """Log a security-relevant event to the audit log."""
    try:
        _configure_logger()
        extra = {
            "ip": ip or "unknown",
            "user_id": str(user_id) if user_id else "anon",
            "target_id": str(target_id) if target_id else "-",
            "action": action,
        }
        # We pass the message as empty because all info is in the formatter/extra
        _audit_logger.info("", extra=extra)
    except Exception:
        # Fail safe: never crash the app because logging failed
        pass
```

### Logged Events

| Event | Trigger | Context Logged |
| :--- | :--- | :--- |
| `LOGIN_SUCCESS` | Successful user authentication | User ID, IP |
| `LOGIN_FAILED` | Invalid credentials | Target Email (as ID), IP |
| `LOGOUT` | User session termination | User ID, IP |
| `REGISTER_USER` | New account creation | New User ID, IP |
| `CREATE_REPORT` | New report submission | User ID, Report ID, IP |

### Storage
Logs are stored in `instance/audit.log`. This keeps them separate from the application code and database, ensuring they persist even if the database is reset during development.

---

## 🔮 Reflections & Future Improvements

*   **Centralization**: In a distributed production environment, local files are insufficient. We would ship these logs to a centralized SIEM (Security Information and Event Management) system like ELK Stack or Splunk.
*   **Integrity**: Currently, a root attacker could modify the log file. In high-security contexts, we would write to a write-only medium or use cryptographic chaining (blockchain-style) to prevent tampering.
