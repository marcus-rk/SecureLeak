import re


def test_home_renders_login_with_csrf(client):
    # Why: Login page must include a CSRF token to mitigate CSRF attacks.
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "<h2>Login</h2>" in html
    assert 'name="csrf_token"' in html


def test_login_without_csrf_is_blocked(client):
    # Why: Missing CSRF token should be rejected (security control is active).
    resp = client.post("/auth/login", data={"email": "a@b.com", "password": "x"})
    assert resp.status_code in (400, 403)


def test_login_with_csrf_redirects_to_reports(client):
    # Why: With a valid token, login flow should succeed and redirect.
    get_resp = client.get("/auth/login")
    html = get_resp.get_data(as_text=True)
    m = re.search(r'name="csrf_token"\s+value="([^"]+)"', html)
    assert m, "CSRF token not found in login form"
    token = m.group(1)

    post_resp = client.post(
        "/auth/login",
        data={
            "email": "user@example.com",
            "password": "secret",
            "csrf_token": token,
        },
        follow_redirects=False,
    )
    assert post_resp.status_code in (302, 303)
    assert "/reports" in post_resp.headers.get("Location", "")
