from flask import Blueprint, flash, redirect, render_template, request, url_for

from repository import reports_repo
from security.decorators import require_role

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/", methods=["GET"])
@require_role("admin")
def dashboard():
    # Keep it simple: list the most recent reports for quick actions
    reports = reports_repo.list_all(limit=200, offset=0)
    return render_template("admin_dashboard.html", reports=reports), 200


@admin_bp.route("/reports/<int:report_id>/status", methods=["POST"])
@require_role("admin")
def update_report_status(report_id: int):
    status = (request.form.get("status") or "").strip().lower()
    if status not in {"public", "private", "closed"}:
        flash("Invalid status.", "error")
        return redirect(url_for("admin.dashboard"), 303)

    ok = reports_repo.update_status(report_id, status)
    if ok:
        flash("Status updated.", "success")
    else:
        # Either report not found or no change
        flash("Could not update status.", "error")
    return redirect(url_for("admin.dashboard"), 303)
