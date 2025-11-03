import os
from pathlib import Path
from typing import Optional

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from flask.typing import ResponseReturnValue
from repository import reports_repo
from security.decorators import login_required
from security.reports_access import is_report_viewable
from security.uploads import (
    get_ext,
    is_allowed_ext,
    is_allowed_mimetype,
    max_upload_bytes,
    store_report_image,
    uploads_base_dir,
)

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


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
    file = request.files.get("image")

    if not title or not description:
        return _report_bad_request("Title and description are required.")

    if severity not in {"low", "medium", "high"}:
        return _report_bad_request("Invalid severity.")

    # Creation policy: only allow public/private at creation time
    if status not in {"public", "private"}:
        return _report_bad_request("Invalid status. Choose public or private.")

    # Validate optional upload (KISS): small checks before creating report
    if file and file.filename:
        ext = get_ext(file.filename)
        if not is_allowed_ext(ext):
            return _report_bad_request("Invalid file type. Allowed: PNG, JPG, GIF.")
        if not is_allowed_mimetype(file.mimetype):
            return _report_bad_request("Invalid file mimetype.")
        max_bytes = max_upload_bytes()
        if request.content_length and request.content_length > max_bytes:
            return _report_bad_request("File too large. Max size is 2 MiB.")

    owner_id = session.get("user_id")
    report_id = reports_repo.create_report(owner_id, title, description, severity, status)

    # Save file after report exists; on failure, continue without image (KISS)
    if file and file.filename:
        try:
            dest_name = store_report_image(file, report_id, uploads_base_dir())
            # one-file-per-report: update stored name
            reports_repo.update_report(report_id, {"image_name": dest_name})
        except Exception:
            flash("Report created but image could not be saved.", "warning")
    flash("Report created.", "success")
    return redirect(url_for("reports.list_reports"), 303)


@reports_bp.route("/<int:report_id>", methods=["GET"])
@login_required
def view_report(report_id: int) -> ResponseReturnValue:
    report = reports_repo.get_report_by_id(report_id)
    if not report:
        abort(404)

    # Authorization: private reports visible only to owner; return 404 to avoid info leakage
    uid = session.get("user_id")
    if not is_report_viewable(report, uid):
        abort(404)
    return render_template("report_detail.html", report=report), 200


@reports_bp.route("/<int:report_id>/image/<path:name>", methods=["GET"])  # New, clearer path
@reports_bp.route("/file/<int:report_id>/<path:name>", methods=["GET"])   # Back-compat alias
@login_required
def report_file(report_id: int, name: str) -> ResponseReturnValue:
    report = reports_repo.get_report_by_id(report_id)
    if not report:
        abort(404)
    # Visibility: same rule as detail
    uid = session.get("user_id")
    if not is_report_viewable(report, uid):
        abort(404)
    # Path safety: only serve the exact stored image_name
    if not report.get("image_name") or name != report.get("image_name"):
        abort(404)
    base_dir = uploads_base_dir()
    directory = os.path.join(base_dir, str(report_id))
    return send_from_directory(directory, name, as_attachment=False)


# --- helpers ---

def _report_bad_request(msg: str) -> ResponseReturnValue:
    flash(msg, "error")
    return render_template("report_new.html"), 400
