from tests.helpers.web import BASE_URL, extract_csrf, register_user


def _post_register(client, email: str, username: str, password: str = "secret1234"):
    # Direct POST: register_user asserts a redirect, conflict tests need the 409.
    get_resp = client.get("/auth/register", base_url=BASE_URL)
    token = extract_csrf(get_resp.get_data(as_text=True))
    return client.post(
        "/auth/register",
        data={"username": username, "email": email, "password": password, "csrf_token": token},
        base_url=BASE_URL,
        headers={"Referer": f"{BASE_URL}/auth/register"},
        follow_redirects=False,
    )


def test_register_taken_username_returns_409(client):
    # Why: a taken username must give a clear 409 on the form, not a 500 error page.
    register_user(client, email="alice@example.com", username="alice")

    resp = _post_register(client, email="other@example.com", username="alice")

    assert resp.status_code == 409
    assert "Username already taken." in resp.get_data(as_text=True)


def test_register_username_differing_only_in_case_is_rejected(client):
    # Why: usernames are unique case-insensitively, so "Alice" cannot impersonate "alice".
    register_user(client, email="alice@example.com", username="alice")

    resp = _post_register(client, email="other@example.com", username="Alice")

    assert resp.status_code == 409
    assert "Username already taken." in resp.get_data(as_text=True)
    # The rejected attempt created no account: its credentials do not sign in.
    login_page = client.get("/auth/login", base_url=BASE_URL)
    login = client.post(
        "/auth/login",
        data={
            "email": "other@example.com",
            "password": "secret1234",
            "csrf_token": extract_csrf(login_page.get_data(as_text=True)),
        },
        base_url=BASE_URL,
        headers={"Referer": f"{BASE_URL}/auth/login"},
    )
    assert login.status_code == 401


def test_register_taken_email_keeps_its_own_409_message(client):
    # Why: a taken email still answers 409 with its existing message, not the username one.
    register_user(client, email="alice@example.com", username="alice")

    resp = _post_register(client, email="alice@example.com", username="bob")

    assert resp.status_code == 409
    html = resp.get_data(as_text=True)
    assert "Email already registered." in html
    assert "Username already taken." not in html
