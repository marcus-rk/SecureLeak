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
        assert isinstance(rid, int) and rid > 0
        r = get_report_by_id(rid)
        assert r is not None
        assert r["title"] == "XSS found"
        assert r["status"] == "public"
        assert r["severity"] == "high"
        assert r["summary"]


def test_list_reports(app):
    with app.app_context():
        rid = create_report("SQLi", "public", "medium", summary="Demo")
        reports = list_reports()
        assert any(item["id"] == rid for item in reports)


def test_update_report(app):
    with app.app_context():
        rid = create_report("CSRF", "public", "low", summary="Demo")
        assert update_report(rid, status="private") is True
        r = get_report_by_id(rid)
        assert r["status"] == "private"


def test_delete_report(app):
    with app.app_context():
        rid = create_report("Headers", "public", "low", summary="Demo")
        assert delete_report(rid) is True
        assert get_report_by_id(rid) is None
