import pytest

import app as app_module
from app import create_app


@pytest.fixture()
def isolated_env(monkeypatch, tmp_path):
    # Why: conftest.py sets SECRET_KEY for the whole process, and load_dotenv()
    # finds a .env next to app.py regardless of cwd. Neutralise both so only
    # the variables set in each test decide the outcome.
    monkeypatch.setattr(app_module, "load_dotenv", lambda *args, **kwargs: False)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("DATABASE", str(tmp_path / "test.sqlite"))
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.delenv("FLASK_DEBUG", raising=False)
    return monkeypatch


def test_missing_secret_key_outside_debug_refuses_to_start(isolated_env):
    # Why: a publicly known fallback key lets anyone forge sessions and CSRF tokens.
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        create_app()


def test_empty_secret_key_outside_debug_refuses_to_start(isolated_env):
    # Why: a blank SECRET_KEY= line in .env must not count as configured.
    isolated_env.setenv("SECRET_KEY", "")
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        create_app()


def test_missing_secret_key_in_debug_starts_with_dev_key(isolated_env):
    # Why: local `flask --app app run --debug` must keep working with zero setup.
    isolated_env.setenv("FLASK_DEBUG", "1")
    app = create_app()
    assert app.debug is True
    assert app.config["SECRET_KEY"] == "dev-insecure-key"


@pytest.mark.parametrize("flask_debug", ["0", "1"])
def test_explicit_secret_key_is_used_as_is(isolated_env, flask_debug):
    isolated_env.setenv("FLASK_DEBUG", flask_debug)
    isolated_env.setenv("SECRET_KEY", "explicit-test-key")
    app = create_app()
    assert app.config["SECRET_KEY"] == "explicit-test-key"
