from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for
from flask.typing import ResponseReturnValue
from repository import reports_repo
from security.decorators import login_required

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")

# DB-backed reports: sample data removed


@reports_bp.route("/", methods=["GET"])
@login_required
def list_reports() -> ResponseReturnValue:
    user_id = session.get("user_id")
    reports = reports_repo.list_public_and_own(user_id)
    return render_template("reports_list.html", reports=reports), 200


@reports_bp.route("/new", methods=["GET"])
@login_required
def new_report() -> ResponseReturnValue:
    return render_template("report_new.html"), 200


@reports_bp.route("/new", methods=["POST"])
@login_required
def new_report_post() -> ResponseReturnValue:
    title = (request.form.get("title") or "").strip()
    description = (request.form.get("description") or "").strip()
    severity = (request.form.get("severity") or "").strip().lower()
    status = (request.form.get("status") or "").strip().lower()

    if not title or not description:
        return _report_bad_request("Title and description are required.")

    if severity not in {"low", "medium", "high"}:
        return _report_bad_request("Invalid severity.")

    # Creation policy: only allow public/private at creation time
    if status not in {"public", "private"}:
        return _report_bad_request("Invalid status. Choose public or private.")

    owner_id = session.get("user_id")
    reports_repo.create_report(owner_id, title, description, severity, status)
    flash("Report created.", "success")
    return redirect(url_for("reports.list_reports"), 303)


@reports_bp.route("/<int:report_id>", methods=["GET"])
def view_report(report_id: int) -> ResponseReturnValue:
    report = reports_repo.get_report_by_id(report_id)
    if not report:
        abort(404)

    # Authorization: private reports visible only to owner; return 404 to avoid info leakage
    if report.get("status") == "private":
        uid = session.get("user_id")
        if not uid or uid != report.get("owner_id"):
            abort(404)
    return render_template("report_detail.html", report=report), 200


# --- helpers ---

def _report_bad_request(msg: str) -> ResponseReturnValue:
    flash(msg, "error")
    return render_template("report_new.html"), 400
