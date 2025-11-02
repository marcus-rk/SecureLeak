import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any, Iterable

from flask import current_app, g


def get_db() -> sqlite3.Connection:
    """Return a SQLite connection stored on Flask's `g` context.

    Ensures the database file and parent directory exist and configures rows
    to be dict-like via `sqlite3.Row`.
    """
    if "db" not in g:
        db_path = Path(current_app.config["DATABASE"])
        db_path.parent.mkdir(parents=True, exist_ok=True)
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(_: Any = None) -> None:
    """Close the connection stored on `g`, if any."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(schema_sql: Iterable[str]) -> None:
    """Initialize the database by executing the provided SQL statements.

    Intended for one-off setup or migrations in simple apps.
    """
    db = get_db()
    with closing(db.cursor()) as cur:
        for statement in schema_sql:
            cur.execute(statement)
    db.commit()
