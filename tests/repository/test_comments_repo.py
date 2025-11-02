from repository.comments_repo import (
    create_comment,
    delete_comment,
    list_comments_for_report,
)
from repository.reports_repo import create_report
from repository.users_repo import create_user


def test_create_and_list_comments_for_report(app):
    with app.app_context():
        uid = create_user("c@example.com", "hash999", name="Commenter")
        rid = create_report("SQLi test", "public", "medium", summary="Demo")
        cid = create_comment(rid, uid, "Looks exploitable")
        assert isinstance(cid, int) and cid > 0, "Comment ID should be a positive integer"
        comments = list_comments_for_report(rid)
        assert any(c["id"] == cid for c in comments), "Created comment should be in the list"


def test_delete_comment(app):
    with app.app_context():
        uid = create_user("d@example.com", "hash888", name="Commenter")
        rid = create_report("Auth test", "public", "low", summary="Demo")
        cid = create_comment(rid, uid, "Okay")
        assert delete_comment(cid) is True, "Comment deletion should return True"
        comments_after = list_comments_for_report(rid)
        assert not any(c["id"] == cid for c in comments_after), "Deleted comment should not be in the list"
