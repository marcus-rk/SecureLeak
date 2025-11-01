from flask import Blueprint, abort, render_template

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


_REPORT_ROWS = [
    ("SQL injection demo", "public", "high"),
    ("Missing CSP", "private", "medium"),
    ("Insecure direct object reference", "private", "high"),
    ("Outdated TLS configuration", "public", "medium"),
    ("Directory traversal proof", "public", "high"),
    ("Broken access control - admin bypass", "private", "high"),
    ("Default credentials audit", "public", "medium"),
    ("Session fixation scenario", "private", "medium"),
    ("Cross-site scripting field test", "public", "high"),
    ("CSRF token leak reproduction", "private", "high"),
    ("Open redirect sample", "public", "medium"),
    ("Logging injection case", "private", "medium"),
    ("YAML deserialization check", "private", "high"),
    ("XML external entity attempt", "public", "high"),
    ("Insecure cookie flags", "public", "medium"),
    ("Rate limit bypass profile", "private", "medium"),
    ("JWT tampering scenario", "private", "high"),
    ("Password reset abuse", "public", "high"),
    ("Uploaded file type bypass", "public", "high"),
    ("Subresource integrity missing", "public", "medium"),
    ("SSRF metadata access", "private", "high"),
    ("Prototype pollution payload", "public", "high"),
    ("Cache poisoning preview", "private", "medium"),
    ("Clickjacking frame test", "public", "medium"),
    ("DNS rebinding lab", "private", "high"),
    ("Mail header injection", "public", "medium"),
    ("OAuth misconfiguration example", "private", "medium"),
    ("API enumeration suite", "public", "medium"),
    ("Websocket auth skip", "private", "high"),
    ("Command injection sandbox", "public", "high"),
    ("GraphQL introspection enabled", "public", "medium"),
    ("CORS wildcard origin", "public", "medium"),
    ("Mixed content resources", "public", "low"),
    ("LDAP injection probe", "private", "high"),
    ("Brute force login window", "private", "medium"),
    ("Memory disclosure via trace", "public", "medium"),
    ("CRLF injection sample", "public", "medium"),
    ("MFA downgrade workflow", "private", "high"),
    ("Partner webhook spoofing", "private", "high"),
    ("Path parameter tampering", "public", "medium"),
    ("Access log exposure", "public", "low"),
    ("Stored XSS comment stream", "public", "high"),
    ("Payment webhook replay", "private", "high"),
    ("Desync request smuggling", "private", "high"),
    ("Compression oracle test", "public", "medium"),
    ("Password policy weakness", "public", "low"),
    ("Error stack trace leak", "public", "low"),
    ("Predictable password reset token", "private", "high"),
    ("Side-channel timing probe", "private", "medium"),
    ("Deprecated cipher suite usage", "public", "medium"),
]

SAMPLE_REPORTS = [
    {
        "id": idx,
        "title": title,
        "status": status,
        "severity": severity,
        "summary": f"Detailed walkthrough highlighting {title.lower()} and recommended mitigations.",
    }
    for idx, (title, status, severity) in enumerate(_REPORT_ROWS, start=1)
]


@reports_bp.route("/", methods=["GET"])
def list_reports() -> str:
    return render_template("reports_list.html", reports=SAMPLE_REPORTS)


@reports_bp.route("/new", methods=["GET", "POST"])
def new_report() -> str:
    return render_template("report_new.html")


@reports_bp.route("/<int:report_id>", methods=["GET"])
def view_report(report_id: int) -> str:
    report = next((item for item in SAMPLE_REPORTS if item["id"] == report_id), None)
    if report is None:
        abort(404)
    return render_template("report_detail.html", report=report)
