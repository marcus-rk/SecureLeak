from typing import Any, Dict, Optional

from database.connection import get_db


def create_user(email: str, password_hash: str, name: Optional[str] = None) -> int:
    db = get_db()
    cur = db.execute(
        "INSERT INTO users (email, password_hash, name) VALUES (?, ?, ?)",
        (email, password_hash, name),
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
    if not fields:
        return False
    db = get_db()
    cols = ", ".join([f"{k} = ?" for k in fields.keys()])
    values = list(fields.values()) + [user_id]
    cur = db.execute(f"UPDATE users SET {cols} WHERE id = ?", values)
    db.commit()
    return cur.rowcount > 0


def delete_user(user_id: int) -> bool:
    db = get_db()
    cur = db.execute("DELETE FROM users WHERE id = ?", (user_id,))
    db.commit()
    return cur.rowcount > 0
