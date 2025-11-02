from typing import Any, Dict, List, Optional

from database.connection import get_db


def create_report(title: str, status: str, severity: str, summary: str = "") -> int:
    db = get_db()
    cur = db.execute(
        "INSERT INTO reports (title, status, severity, summary) VALUES (?, ?, ?, ?)",
        (title, status, severity, summary),
    )
    db.commit()
    return cur.lastrowid


def get_report_by_id(report_id: int) -> Optional[Dict[str, Any]]:
    row = get_db().execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
    return dict(row) if row else None


def list_reports(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    rows = get_db().execute(
        "SELECT * FROM reports ORDER BY id LIMIT ? OFFSET ?", (limit, offset)
    ).fetchall()
    return [dict(r) for r in rows]


def update_report(report_id: int, **fields: Any) -> bool:
    if not fields:
        return False
    db = get_db()
    cols = ", ".join([f"{k} = ?" for k in fields.keys()])
    values = list(fields.values()) + [report_id]
    cur = db.execute(f"UPDATE reports SET {cols} WHERE id = ?", values)
    db.commit()
    return cur.rowcount > 0


def delete_report(report_id: int) -> bool:
    db = get_db()
    cur = db.execute("DELETE FROM reports WHERE id = ?", (report_id,))
    db.commit()
    return cur.rowcount > 0
