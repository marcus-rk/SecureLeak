from flask import Blueprint, render_template

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


@reports_bp.route("/", methods=["GET"])
def list_reports() -> str:
    sample_reports = [
        {"title": "SQL injection demo", "status": "public", "severity": "high"},
        {"title": "Missing CSP", "status": "private", "severity": "medium"},
    ]
    return render_template("reports_list.html", reports=sample_reports)


@reports_bp.route("/new", methods=["GET", "POST"])
def new_report() -> str:
    return render_template("report_new.html")
