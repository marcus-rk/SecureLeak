from repository.reports_repo import (
    create_report,
    get_report_by_id,
    list_reports,
    update_report,
    delete_report,
)


def test_create_report_and_get_by_id(app):
    with app.app_context():
        rid = create_report("XSS found", "public", "high", summary="Proof of XSS")
        assert isinstance(rid, int) and rid > 0, "Report ID should be a positive integer"
        r = get_report_by_id(rid)
        assert r is not None, "Report should be retrievable by ID"
        assert r["title"] == "XSS found", "Report title should match"
        assert r["status"] == "public", "Report status should match"
        assert r["severity"] == "high", "Report severity should match"
        assert r["summary"] == "Proof of XSS", "Report summary should match"


def test_list_reports(app):
    with app.app_context():
        rid = create_report("SQLi", "public", "medium", summary="Demo")
        reports = list_reports()
        assert any(item["id"] == rid for item in reports), "Created report should be in the list"


def test_update_report(app):
    with app.app_context():
        rid = create_report("CSRF", "public", "low", summary="Demo")
        assert update_report(rid, status="private") is True, "Report update should return True"
        r = get_report_by_id(rid)
        assert r["status"] == "private", "Report status should be updated to private"


def test_delete_report(app):
    with app.app_context():
        rid = create_report("Headers", "public", "low", summary="Demo")
        assert delete_report(rid) is True, "Report deletion should return True"
        assert get_report_by_id(rid) is None, "Deleted report should not be retrievable"
