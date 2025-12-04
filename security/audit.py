import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from flask import current_app

# Configure a specific logger for security audits
# We don't use the default app.logger to keep audit logs separate from debug logs
_audit_logger = logging.getLogger("security_audit")
_audit_logger.setLevel(logging.INFO)
_handler = None


def _configure_logger():
    """Lazy configuration of the file handler to ensure app context is available."""
    global _handler
    if _handler:
        return

    # Store audit logs in instance/audit.log
    log_path = Path(current_app.instance_path) / "audit.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    _handler = logging.FileHandler(log_path)
    # Format: [TIMESTAMP] [IP] User:ID Action:ACTION Target:ID
    formatter = logging.Formatter(
        "[%(asctime)s] [%(ip)s] User:%(user_id)s Action:%(action)s Target:%(target_id)s"
    )
    _handler.setFormatter(formatter)
    _audit_logger.addHandler(_handler)


def log_security_event(
    action: str,
    user_id: Optional[int] = None,
    target_id: Optional[str] = None,
    ip: Optional[str] = None,
) -> None:
    """Log a security-relevant event to the audit log.

    Args:
        action: The event name (e.g., 'LOGIN_SUCCESS', 'DELETE_REPORT').
        user_id: The ID of the user performing the action (or None if anonymous).
        target_id: The ID of the object being acted upon (e.g., report_id).
        ip: The IP address of the client.
    """
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
