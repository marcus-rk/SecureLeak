import re


def test_home_renders_login_with_csrf(client):
    # Why: Login page must include a CSRF token to mitigate CSRF attacks.
    # Use https base_url to avoid HTTPS redirect enforced by security middleware
    resp = client.get("/", base_url="https://localhost")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "<h2>Login</h2>" in html
    assert 'name="csrf_token"' in html


def test_login_without_csrf_is_blocked(client):
    # Why: Missing CSRF token should be rejected (security control is active).
    # Use https base_url to avoid HTTPS redirect for POST
    resp = client.post(
        "/auth/login",
        data={"email": "a@b.com", "password": "x"},
        base_url="https://localhost",
    )
    assert resp.status_code in (400, 403)


def test_login_with_csrf_redirects_to_reports(client):
    # Why: With a valid token, login flow should succeed and redirect.
    # Ensure there is a user to log in with by registering first.
    reg_get = client.get("/auth/register", base_url="https://localhost")
    reg_html = reg_get.get_data(as_text=True)
    reg_m = re.search(r'name="csrf_token"\s+value="([^"]+)"', reg_html)
    assert reg_m, "CSRF token not found in register form"
    reg_token = reg_m.group(1)

    password = "secret1234"  # meets server-side minimum length
    reg_post = client.post(
        "/auth/register",
        data={
            "username": "User1",
            "email": "user@example.com",
            "password": password,
            "csrf_token": reg_token,
        },
        base_url="https://localhost",
        headers={"Referer": "https://localhost/auth/register"},
        follow_redirects=False,
    )
    assert reg_post.status_code in (302, 303)
    assert "/auth/login" in reg_post.headers.get("Location", "")

    get_resp = client.get("/auth/login", base_url="https://localhost")
    html = get_resp.get_data(as_text=True)
    m = re.search(r'name="csrf_token"\s+value="([^"]+)"', html)
    assert m, "CSRF token not found in login form"
    token = m.group(1)

    post_resp = client.post(
        "/auth/login",
        data={
            "email": "user@example.com",
            "password": password,
            "csrf_token": token,
        },
        headers={"Referer": "https://localhost/auth/login"},
        base_url="https://localhost",
        follow_redirects=False,
    )
    assert post_resp.status_code in (302, 303)
    assert "/reports" in post_resp.headers.get("Location", "")
