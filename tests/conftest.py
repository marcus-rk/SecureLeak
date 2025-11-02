import os
import pytest

from app import create_app


@pytest.fixture()
def app():
    """Create and configure a Flask app instance for tests.

    Using the name `app` follows common pytest/flask conventions and keeps
    fixtures interoperable with extensions and helpers.
    """
    # Ensure a deterministic secret for CSRF/session during tests
    os.environ.setdefault("SECRET_KEY", "test-secret-key")
    app = create_app()
    app.config.update(
        TESTING=True,
    )
    yield app


@pytest.fixture()
def client(app):
    """A test client bound to the application fixture."""
    return app.test_client()
