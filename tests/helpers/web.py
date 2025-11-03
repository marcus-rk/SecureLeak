import re

BASE_URL = "https://localhost"


def extract_csrf(html: str) -> str:
    m = re.search(r'name="csrf_token"\s+value="([^"]+)"', html)
    assert m, "CSRF token not found in form"
    return m.group(1)


def register_user(client, email: str, username: str, password: str = "secret1234") -> None:
    # GET token
    get_resp = client.get("/auth/register", base_url=BASE_URL)
    token = extract_csrf(get_resp.get_data(as_text=True))
    # POST register
    post_resp = client.post(
        "/auth/register",
        data={
            "username": username,
            "email": email,
            "password": password,
            "csrf_token": token,
        },
        base_url=BASE_URL,
        headers={"Referer": f"{BASE_URL}/auth/register"},
        follow_redirects=False,
    )
    assert post_resp.status_code in (302, 303)


def login_user(client, email: str, password: str = "secret1234") -> None:
    get_resp = client.get("/auth/login", base_url=BASE_URL)
    token = extract_csrf(get_resp.get_data(as_text=True))
    post_resp = client.post(
        "/auth/login",
        data={
            "email": email,
            "password": password,
            "csrf_token": token,
        },
        base_url=BASE_URL,
        headers={"Referer": f"{BASE_URL}/auth/login"},
        follow_redirects=False,
    )
    assert post_resp.status_code in (302, 303)
