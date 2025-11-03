from typing import Any, Dict, List, Optional

from database.connection import get_db


def create_report(owner_id: int, title: str, description: str, severity: str, status: str) -> int:
    db = get_db()
    cur = db.execute(
        "INSERT INTO reports (owner_id, title, description, severity, status) VALUES (?, ?, ?, ?, ?)",
        (owner_id, title, description, severity, status),
    )
    db.commit()
    return cur.lastrowid


def get_report_by_id(report_id: int) -> Optional[Dict[str, Any]]:
    row = get_db().execute(
        """
        SELECT r.*, u.username AS owner_username
        FROM reports AS r
        LEFT JOIN users AS u ON u.id = r.owner_id
        WHERE r.id = ?
        """,
        (report_id,),
    ).fetchone()
    return dict(row) if row else None


def list_public_and_own(user_id: int, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    rows = get_db().execute(
        """
        SELECT *
        FROM reports
        WHERE status = 'public' OR owner_id = ?
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
        """,
        (user_id, limit, offset),
    ).fetchall()
    return [dict(r) for r in rows]


def update_report(report_id: int, updates: Dict[str, Any]) -> bool:
    """Update allowed report columns using a whitelist to avoid SQL injection.

    Allowed fields: title, description, severity, status, image_name.
    """
    allowed = {"title", "description", "severity", "status", "image_name"}
    sanitized = {k: v for k, v in updates.items() if k in allowed}
    if not sanitized:
        return False
    db = get_db()
    cols = ", ".join([f"{k} = ?" for k in sanitized.keys()])
    values = list(sanitized.values()) + [report_id]
    sql = "UPDATE reports SET " + cols + " WHERE id = ?"  # columns validated via whitelist
    cur = db.execute(sql, values)
    db.commit()
    return cur.rowcount > 0


def delete_report(report_id: int) -> bool:
    db = get_db()
    cur = db.execute("DELETE FROM reports WHERE id = ?", (report_id,))
    db.commit()
    return cur.rowcount > 0
