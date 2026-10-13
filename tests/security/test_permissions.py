from repository import comments_repo, reports_repo, users_repo
from security.auth_utils import build_hasher
from tests.helpers.web import BASE_URL, extract_csrf, login_user

PASSWORD = "secret1234"
MISSING_REPORT_ID = 9999


def test_non_owner_gets_404_on_private_report_same_as_missing(app, client):
    # Why: A private report is viewable only by its owner and admins, and must not reveal that it exists.
    owner_id = _create_user(app, "owner@example.com", "Owner1")
    _create_user(app, "other@example.com", "Other1")
    report_id = _create_report(app, owner_id, "private")

    login_user(client, "other@example.com", PASSWORD)
    # Consume the one-time "Signed in." flash so both 404 pages render the same way
    client.get("/reports/", base_url=BASE_URL)
    private_resp = client.get(f"/reports/{report_id}", base_url=BASE_URL)
    missing_resp = client.get(f"/reports/{MISSING_REPORT_ID}", base_url=BASE_URL)

    assert private_resp.status_code == 404
    assert private_resp.get_data() == missing_resp.get_data()


def test_non_owner_comment_on_private_report_gets_404_and_stores_nothing(app, client):
    # Why: Nobody may interact with a report they cannot view, and a refusal must not store the comment.
    owner_id = _create_user(app, "owner@example.com", "Owner1")
    _create_user(app, "other@example.com", "Other1")
    report_id = _create_report(app, owner_id, "private")

    login_user(client, "other@example.com", PASSWORD)
    resp = _post(client, f"/reports/{report_id}/comment", {"body": "Sneaky comment"})

    assert resp.status_code == 404
    with app.app_context():
        assert comments_repo.list_comments_for_report(report_id) == []


def test_regular_user_gets_404_on_admin_dashboard_and_status_change(app, client):
    # Why: Only an admin reaches the admin pages or changes a report's status.
    user_id = _create_user(app, "user@example.com", "User1")
    report_id = _create_report(app, user_id, "private")

    login_user(client, "user@example.com", PASSWORD)
    dashboard_resp = client.get("/admin/", base_url=BASE_URL)
    status_resp = _post(client, f"/admin/reports/{report_id}/status", {"status": "public"})

    assert dashboard_resp.status_code == 404
    assert status_resp.status_code == 404
    with app.app_context():
        assert reports_repo.get_report_by_id(report_id)["status"] == "private"


def test_demoted_admin_gets_404_on_admin_dashboard_despite_admin_session(app, client):
    # Why: Removing the admin role must take effect on the next request, not when the session ends.
    admin_id = _create_user(app, "admin@example.com", "Admin1", role="admin")
    login_user(client, "admin@example.com", PASSWORD)
    assert client.get("/admin/", base_url=BASE_URL).status_code == 200

    _demote(app, admin_id)

    assert client.get("/admin/", base_url=BASE_URL).status_code == 404


def test_demoted_admin_gets_404_on_private_report_page_comment_and_image(app, client, tmp_path):
    # Why: A demoted admin must lose the admin override on other users' private reports on the next request.
    app.config["UPLOADS_DIR"] = str(tmp_path / "uploads")
    owner_id = _create_user(app, "owner@example.com", "Owner1")
    admin_id = _create_user(app, "admin@example.com", "Admin1", role="admin")
    report_id = _create_report(app, owner_id, "private")
    image_url = _attach_image(app, tmp_path / "uploads", report_id)

    login_user(client, "admin@example.com", PASSWORD)
    assert client.get(f"/reports/{report_id}", base_url=BASE_URL).status_code == 200
    assert client.get(image_url, base_url=BASE_URL).status_code == 200

    _demote(app, admin_id)

    assert client.get(f"/reports/{report_id}", base_url=BASE_URL).status_code == 404
    assert _post(client, f"/reports/{report_id}/comment", {"body": "After demotion"}).status_code == 404
    assert client.get(image_url, base_url=BASE_URL).status_code == 404
    with app.app_context():
        assert comments_repo.list_comments_for_report(report_id) == []


def test_signed_out_visitor_is_redirected_to_login(app, client):
    # Why: Nothing behind sign-in is reachable without signing in.
    owner_id = _create_user(app, "owner@example.com", "Owner1")
    report_id = _create_report(app, owner_id, "public")

    for path in ("/reports/", f"/reports/{report_id}", "/admin/"):
        resp = client.get(path, base_url=BASE_URL)
        assert resp.status_code == 302, path
        assert resp.headers["Location"].endswith("/auth/login"), path


# --- helpers ---


def _create_user(app, email: str, username: str, role: str = "user") -> int:
    # Registration always creates role "user", so users (and admins) are created through the repository
    with app.app_context():
        return users_repo.create_user(email, build_hasher().hash(PASSWORD), username, role)


def _create_report(app, owner_id: int, status: str) -> int:
    with app.app_context():
        return reports_repo.create_report(owner_id, "Title", "Description", "medium", status)


def _attach_image(app, uploads_dir, report_id: int) -> str:
    """Store a file as the report's image and return the image URL."""
    name = "stored.png"
    (uploads_dir / str(report_id)).mkdir(parents=True)
    (uploads_dir / str(report_id) / name).write_bytes(b"image bytes")
    with app.app_context():
        reports_repo.update_report(report_id, {"image_name": name})
    return f"/reports/{report_id}/image/{name}"


def _demote(app, user_id: int) -> None:
    with app.app_context():
        assert users_repo.update_user(user_id, role="user")


def _post(client, path: str, data: dict):
    # The CSRF token is bound to the session, so any signed-in form page provides a valid one
    token = extract_csrf(client.get("/reports/new", base_url=BASE_URL).get_data(as_text=True))
    return client.post(
        path,
        data={**data, "csrf_token": token},
        base_url=BASE_URL,
        headers={"Referer": f"{BASE_URL}/reports/new"},
    )
