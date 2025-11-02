from pathlib import Path

from database.connection import get_db


def apply(sql_path: str | Path | None = None) -> None:
    """Apply the migration SQL to the configured SQLite database.

    KISS: read the file and run it with executescript().
    """
    if sql_path is None:
        sql_path = Path(__file__).with_name("migrations") / "init.sql"
    sql_text = Path(sql_path).read_text(encoding="utf-8")

    db = get_db()
    db.executescript(sql_text)
    db.commit()


if __name__ == "__main__":
    # Usage: python -m database.initialize
    from app import create_app

    app = create_app()
    with app.app_context():
        apply()
        print("Database initialized from database/migrations/init.sql")
