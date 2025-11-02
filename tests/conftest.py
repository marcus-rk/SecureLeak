# ruff: noqa: E402
import os
import sys
from pathlib import Path

import pytest

# Ensure project root is on sys.path so "from app import create_app" works
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import create_app  # noqa: E402
from database.initialize import apply as apply_migration  # noqa: E402


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
