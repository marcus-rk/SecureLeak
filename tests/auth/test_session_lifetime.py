from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

import pytest
from itsdangerous.timed import TimestampSigner

from tests.helpers.web import BASE_URL, extract_csrf, register_user


@pytest.fixture()
def server_clock(monkeypatch):
    """Control the clock Flask uses to sign session cookies and check their age.

    Only the server's view of time moves; the test client keeps real time, as a
    copied cookie would, so these tests show what the server itself enforces.
    """
    clock = {"now": int(datetime.now(timezone.utc).timestamp())}
    monkeypatch.setattr(TimestampSigner, "get_timestamp", lambda _self: clock["now"])

    def advance(minutes: int) -> None:
        clock["now"] += minutes * 60

    return advance


def _login(client, email: str, password: str = "secret1234"):
    # Direct POST: the test needs the login response's Set-Cookie header.
    get_resp = client.get("/auth/login", base_url=BASE_URL)
    token = extract_csrf(get_resp.get_data(as_text=True))
    return client.post(
        "/auth/login",
        data={"email": email, "password": password, "csrf_token": token},
        base_url=BASE_URL,
        headers={"Referer": f"{BASE_URL}/auth/login"},
        follow_redirects=False,
    )


def _session_cookie_expires(resp):
    for header in resp.headers.getlist("Set-Cookie"):
        if header.startswith("session="):
            for part in header.split(";"):
                name, _, value = part.strip().partition("=")
                if name.lower() == "expires":
                    return parsedate_to_datetime(value)
            return None
    raise AssertionError("No session cookie in response")


def test_login_sets_session_cookie_expiring_in_30_minutes(client):
    # Why: the browser must drop the session cookie after the configured lifetime.
    register_user(client, email="alice@example.com", username="alice")

    resp = _login(client, "alice@example.com")

    assert resp.status_code == 303
    expires = _session_cookie_expires(resp)
    assert expires is not None, "session cookie has no Expires, so it lives until the browser closes"
    expected = datetime.now(timezone.utc) + timedelta(minutes=30)
    assert abs(expires - expected) < timedelta(seconds=10)


def test_activity_keeps_session_alive_beyond_lifetime(client, server_clock):
    # Why: the lifetime is an idle timeout, so a user who keeps working stays signed in.
    register_user(client, email="alice@example.com", username="alice")
    _login(client, "alice@example.com")
    assert client.get("/reports/", base_url=BASE_URL).status_code == 200

    server_clock(20)
    assert client.get("/reports/", base_url=BASE_URL).status_code == 200
    server_clock(20)
    resp = client.get("/reports/", base_url=BASE_URL)

    assert resp.status_code == 200


def test_server_rejects_session_idle_longer_than_lifetime(client, server_clock):
    # Why: the server, not only the browser, must refuse a session cookie idle past 30 minutes.
    register_user(client, email="alice@example.com", username="alice")
    _login(client, "alice@example.com")
    assert client.get("/reports/", base_url=BASE_URL).status_code == 200

    server_clock(31)
    resp = client.get("/reports/", base_url=BASE_URL, follow_redirects=True)

    assert resp.request.path == "/auth/login"
    assert "Please sign in." in resp.get_data(as_text=True)
