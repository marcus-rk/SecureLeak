from typing import Any, Dict, Optional

from database.connection import get_db


def create_user(email: str, password_hash: str, name: Optional[str] = None, role: str = "user") -> int:
    db = get_db()
    cur = db.execute(
        "INSERT INTO users (email, password_hash, name, role) VALUES (?, ?, ?, ?)",
        (email, password_hash, name, role),
    )
    db.commit()
    return cur.lastrowid


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    row = get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return dict(row) if row else None


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    row = get_db().execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    return dict(row) if row else None


def update_user(user_id: int, **fields: Any) -> bool:
    """Update allowed user columns using a whitelist to avoid SQL injection.

    Allowed fields: email, password_hash, name, role.
    Returns True if a row was updated.
    """
    allowed = {"email", "password_hash", "name", "role"}
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        return False
    db = get_db()
    cols = ", ".join([f"{k} = ?" for k in updates.keys()])
    values = list(updates.values()) + [user_id]
    sql = "UPDATE users SET " + cols + " WHERE id = ?"  # columns validated via whitelist
    cur = db.execute(sql, values)
    db.commit()
    return cur.rowcount > 0


def delete_user(user_id: int) -> bool:
    db = get_db()
    cur = db.execute("DELETE FROM users WHERE id = ?", (user_id,))
    db.commit()
    return cur.rowcount > 0
