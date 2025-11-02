import os
import pytest
from pathlib import Path

from app import create_app
from database.initialize import apply as apply_migration


@pytest.fixture()
def app(tmp_path):
    """Create and configure a Flask app instance for tests.

    Uses a temporary SQLite database per test run to keep tests isolated and simple.
    """
    os.environ.setdefault("SECRET_KEY", "test-secret-key")
    app = create_app()
    # Use a temp DB path and initialize schema
    db_path = tmp_path / "test.sqlite"
    app.config.update(TESTING=True, DATABASE=str(db_path))
    with app.app_context():
        apply_migration()
    yield app


@pytest.fixture()
def client(app):
    """A test client bound to the application fixture."""
    return app.test_client()
