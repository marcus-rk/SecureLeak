from repository.reports_repo import (
    create_report,
    delete_report,
    get_report_by_id,
    list_public_and_own,
    update_report,
)
from repository.users_repo import create_user


def test_create_report_and_get_by_id(app):
    with app.app_context():
        owner_id = create_user("reporter@example.com", "hash123", username="Reporter")
        rid = create_report(owner_id, "XSS found", "Proof of XSS", "high", "public")
        assert isinstance(rid, int) and rid > 0, "Report ID should be a positive integer"
        r = get_report_by_id(rid)
        assert r is not None, "Report should be retrievable by ID"
        assert r["title"] == "XSS found", "Report title should match"
        assert r["status"] == "public", "Report status should match"
        assert r["severity"] == "high", "Report severity should match"
        assert r["description"] == "Proof of XSS", "Report description should match"


def test_list_reports(app):
    with app.app_context():
        owner_id = create_user("owner@example.com", "hash456", username="Owner")
        rid = create_report(owner_id, "SQLi", "Demo", "medium", "public")
        reports = list_public_and_own(owner_id)
        assert any(item["id"] == rid for item in reports), "Created report should be in the list"


def test_update_report(app):
    with app.app_context():
        owner_id = create_user("editor@example.com", "hash789", username="Editor")
        rid = create_report(owner_id, "CSRF", "Demo", "low", "public")
        assert update_report(rid, {"status": "private"}) is True, "Report update should return True"
        r = get_report_by_id(rid)
        assert r["status"] == "private", "Report status should be updated to private"


def test_delete_report(app):
    with app.app_context():
        owner_id = create_user("deleter@example.com", "hash000", username="Deleter")
        rid = create_report(owner_id, "Headers", "Demo", "low", "public")
        assert delete_report(rid) is True, "Report deletion should return True"
        assert get_report_by_id(rid) is None, "Deleted report should not be retrievable"
