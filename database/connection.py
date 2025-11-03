import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any, Iterable

from flask import current_app, g


def get_db() -> sqlite3.Connection:
    """Return a SQLite connection stored on Flask's `g` context. 
    (g context = Flask's application context global storage)

    Ensures the database file and parent directory exist and configures rows
    to be dict-like via `sqlite3.Row`.
    """
    if "db" not in g:
        db_path = Path(current_app.config["DATABASE"])
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(db_path)
        # Enforce relational integrity on SQLite (off by default per-connection)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row
        g.db = conn
    return g.db


def close_db(_: Any = None) -> None:
    """Close the connection stored on `g`, if any."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(schema_sql: Iterable[str]) -> None:
    """Initialize the database by executing the provided SQL statements."""
    db = get_db()
    with closing(db.cursor()) as cur:
        for statement in schema_sql:
            cur.execute(statement)
    db.commit()
