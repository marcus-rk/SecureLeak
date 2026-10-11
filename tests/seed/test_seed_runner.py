import pytest

import app as app_module
from app import create_app
from repository import users_repo
from security.auth_utils import build_hasher, verify_password
from seed import seed_runner

FAKE_VALID_PASSWORD = "fake-seed-pass-for-tests-7Q"


@pytest.fixture()
def seed_env(monkeypatch, tmp_path):
    # Why: load_dotenv() finds a .env next to the calling module regardless of
    # cwd, so a developer's local .env could leak in. Neutralise it so only the
    # variables set in each test decide the outcome.
    monkeypatch.setattr(app_module, "load_dotenv", lambda *args, **kwargs: False)
    monkeypatch.setattr(seed_runner, "load_dotenv", lambda *args, **kwargs: False)
    monkeypatch.chdir(tmp_path)
    db_path = tmp_path / "seed.sqlite"
    uploads_dir = tmp_path / "uploads"
    monkeypatch.setenv("DATABASE", str(db_path))
    monkeypatch.setenv("UPLOADS_DIR", str(uploads_dir))
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")
    monkeypatch.delenv("FLASK_DEBUG", raising=False)
    monkeypatch.delenv("SEED_PASSWORD", raising=False)
    return db_path, uploads_dir


def _make_existing_data(db_path, uploads_dir):
    db_path.write_bytes(b"existing database")
    uploads_dir.mkdir()
    (uploads_dir / "keep.png").write_bytes(b"existing upload")


def test_missing_seed_password_refuses_and_keeps_existing_data(seed_env, capsys):
    # Why: a missing variable must never cost the developer their data.
    db_path, uploads_dir = seed_env
    _make_existing_data(db_path, uploads_dir)

    with pytest.raises(SystemExit) as excinfo:
        seed_runner.main()

    assert excinfo.value.code == 1
    assert "SEED_PASSWORD" in capsys.readouterr().err
    assert db_path.read_bytes() == b"existing database"
    assert (uploads_dir / "keep.png").read_bytes() == b"existing upload"


@pytest.mark.parametrize(
    "weak_password",
    [
        pytest.param("qwertyuiop", id="common"),
        pytest.param("Short7x", id="too-short"),
    ],
)
def test_weak_seed_password_refuses_and_keeps_existing_data(seed_env, monkeypatch, capsys, weak_password):
    # Why: seeded accounts must meet the same password rules as registration.
    db_path, uploads_dir = seed_env
    _make_existing_data(db_path, uploads_dir)
    monkeypatch.setenv("SEED_PASSWORD", weak_password)

    with pytest.raises(SystemExit) as excinfo:
        seed_runner.main()

    assert excinfo.value.code == 1
    err = capsys.readouterr().err
    assert "SEED_PASSWORD" in err
    assert weak_password not in err
    assert db_path.read_bytes() == b"existing database"
    assert (uploads_dir / "keep.png").read_bytes() == b"existing upload"


def test_valid_seed_password_seeds_admin_that_can_authenticate(seed_env, monkeypatch, capsys):
    # Why: the demo must keep working, with the password the developer chose.
    monkeypatch.setenv("SEED_PASSWORD", FAKE_VALID_PASSWORD)

    seed_runner.main()

    out = capsys.readouterr().out
    assert "Seed complete:" in out
    assert FAKE_VALID_PASSWORD not in out
    with create_app().app_context():
        admin = users_repo.get_user_by_email("admin1@mail.com")
        assert admin is not None and admin["role"] == "admin"
        hasher = build_hasher()
        assert verify_password(hasher, admin["password_hash"], FAKE_VALID_PASSWORD)
        assert not verify_password(hasher, admin["password_hash"], "password123")
