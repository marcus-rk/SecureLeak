from typing import Any, Dict, List

from database.connection import get_db


def create_comment(report_id: int, user_id: int, content: str) -> int:
    db = get_db()
    cur = db.execute(
        "INSERT INTO comments (report_id, user_id, content) VALUES (?, ?, ?)",
        (report_id, user_id, content),
    )
    db.commit()
    return cur.lastrowid


def list_comments_for_report(report_id: int) -> List[Dict[str, Any]]:
    rows = get_db().execute(
        "SELECT * FROM comments WHERE report_id = ? ORDER BY id", (report_id,)
    ).fetchall()
    return [dict(r) for r in rows]


def delete_comment(comment_id: int) -> bool:
    db = get_db()
    cur = db.execute("DELETE FROM comments WHERE id = ?", (comment_id,))
    db.commit()
    return cur.rowcount > 0
