import io

import pytest

from repository import reports_repo, users_repo
from tests.helpers.web import BASE_URL, extract_csrf, register_user, login_user


def _create_report_with_image(client, title: str, status: str, filename: str, content_type: str,
                               image_bytes: bytes = b"\x89PNG\r\n\x1a\n") -> None:
    # GET new report page for CSRF
    get_resp = client.get("/reports/new", base_url=BASE_URL)
    token = extract_csrf(get_resp.get_data(as_text=True))
    data = {
        "title": title,
        "description": "Example",
        "severity": "medium",
        "status": status,
        "csrf_token": token,
        "image": (io.BytesIO(image_bytes), filename, content_type),
    }
    resp = client.post(
        "/reports/new",
        data=data,
        base_url=BASE_URL,
        headers={"Referer": f"{BASE_URL}/reports/new"},
        follow_redirects=False,
    )
    return resp


@pytest.mark.usefixtures("client")
def test_upload_public_and_private_access(app, client, tmp_path):
    # Use a temp uploads dir for isolation
    app.config["UPLOADS_DIR"] = str(tmp_path / "uploads")

    # Register two users and login as owner
    register_user(client, "owner@example.com", "Owner1")
    register_user(client, "other@example.com", "Other1")
    login_user(client, "owner@example.com")

    # Create public report with a tiny PNG
    resp = _create_report_with_image(client, "Public A", "public", "a.png", "image/png")
    assert resp.status_code in (302, 303)

    # Discover report id and image name from DB
    with app.app_context():
        owner = users_repo.get_user_by_email("owner@example.com")
        assert owner and owner["id"]
        reports = reports_repo.list_public_and_own(owner["id"])  # public + own private
        assert reports, "Report should exist"
        r = next((x for x in reports if x.get("title") == "Public A"), reports[0])
        rid = r["id"]
        image_name = r.get("image_name")
        assert image_name, "Image name should be stored on report"

    # Owner can fetch file
    file_resp = client.get(
        f"/reports/file/{rid}/{image_name}",
        base_url=BASE_URL,
    )
    assert file_resp.status_code == 200

    # Another user can fetch public file
    login_user(client, "other@example.com")
    file_resp2 = client.get(
        f"/reports/file/{rid}/{image_name}",
        base_url=BASE_URL,
    )
    assert file_resp2.status_code == 200

    # Create private report with image as owner
    login_user(client, "owner@example.com")
    resp2 = _create_report_with_image(client, "Private B", "private", "b.jpg", "image/jpeg")
    assert resp2.status_code in (302, 303)

    with app.app_context():
        reports2 = reports_repo.list_public_and_own(owner["id"])  # public + own private
        r2 = next((x for x in reports2 if x.get("title") == "Private B"), reports2[0])
        rid2 = r2["id"]
        image_name2 = r2.get("image_name")
        assert image_name2

    # Non-owner cannot fetch private file
    login_user(client, "other@example.com")
    not_allowed = client.get(
        f"/reports/file/{rid2}/{image_name2}",
        base_url=BASE_URL,
    )
    assert not_allowed.status_code == 404

    # Owner can fetch private file
    login_user(client, "owner@example.com")
    allowed = client.get(
        f"/reports/file/{rid2}/{image_name2}",
        base_url=BASE_URL,
    )
    assert allowed.status_code == 200


@pytest.mark.usefixtures("client")
def test_upload_disallowed_extension_returns_400(app, client, tmp_path):
    app.config["UPLOADS_DIR"] = str(tmp_path / "uploads")

    register_user(client, "owner2@example.com", "Owner2")
    login_user(client, "owner2@example.com")

    resp = _create_report_with_image(
        client,
        title="Bad File",
        status="public",
        filename="bad.txt",
        content_type="text/plain",
        image_bytes=b"hello",
    )
    assert resp.status_code == 400
