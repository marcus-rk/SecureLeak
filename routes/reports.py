from flask import Blueprint, render_template

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


@reports_bp.route("/", methods=["GET"])
def list_reports() -> str:
    sample_reports = [
        {"title": "SQL injection demo", "status": "public", "severity": "high"},
        {"title": "Missing CSP", "status": "private", "severity": "medium"},
        {"title": "Insecure direct object reference", "status": "private", "severity": "high"},
        {"title": "Outdated TLS configuration", "status": "public", "severity": "medium"},
        {"title": "Directory traversal proof", "status": "public", "severity": "high"},
        {"title": "Broken access control - admin bypass", "status": "private", "severity": "high"},
        {"title": "Default credentials audit", "status": "public", "severity": "medium"},
        {"title": "Session fixation scenario", "status": "private", "severity": "medium"},
        {"title": "Cross-site scripting field test", "status": "public", "severity": "high"},
        {"title": "CSRF token leak reproduction", "status": "private", "severity": "high"},
        {"title": "Open redirect sample", "status": "public", "severity": "medium"},
        {"title": "Logging injection case", "status": "private", "severity": "medium"},
        {"title": "YAML deserialization check", "status": "private", "severity": "high"},
        {"title": "XML external entity attempt", "status": "public", "severity": "high"},
        {"title": "Insecure cookie flags", "status": "public", "severity": "medium"},
        {"title": "Rate limit bypass profile", "status": "private", "severity": "medium"},
        {"title": "JWT tampering scenario", "status": "private", "severity": "high"},
        {"title": "Password reset abuse", "status": "public", "severity": "high"},
        {"title": "Uploaded file type bypass", "status": "public", "severity": "high"},
        {"title": "Subresource integrity missing", "status": "public", "severity": "medium"},
        {"title": "SSRF metadata access", "status": "private", "severity": "high"},
        {"title": "Prototype pollution payload", "status": "public", "severity": "high"},
        {"title": "Cache poisoning preview", "status": "private", "severity": "medium"},
        {"title": "Clickjacking frame test", "status": "public", "severity": "medium"},
        {"title": "DNS rebinding lab", "status": "private", "severity": "high"},
        {"title": "Mail header injection", "status": "public", "severity": "medium"},
        {"title": "OAuth misconfiguration example", "status": "private", "severity": "medium"},
        {"title": "API enumeration suite", "status": "public", "severity": "medium"},
        {"title": "Websocket auth skip", "status": "private", "severity": "high"},
        {"title": "Command injection sandbox", "status": "public", "severity": "high"},
        {"title": "GraphQL introspection enabled", "status": "public", "severity": "medium"},
        {"title": "CORS wildcard origin", "status": "public", "severity": "medium"},
        {"title": "Mixed content resources", "status": "public", "severity": "low"},
        {"title": "LDAP injection probe", "status": "private", "severity": "high"},
        {"title": "Brute force login window", "status": "private", "severity": "medium"},
        {"title": "Memory disclosure via trace", "status": "public", "severity": "medium"},
        {"title": "CRLF injection sample", "status": "public", "severity": "medium"},
        {"title": "MFA downgrade workflow", "status": "private", "severity": "high"},
        {"title": "Partner webhook spoofing", "status": "private", "severity": "high"},
        {"title": "Path parameter tampering", "status": "public", "severity": "medium"},
        {"title": "Access log exposure", "status": "public", "severity": "low"},
        {"title": "Stored XSS comment stream", "status": "public", "severity": "high"},
        {"title": "Payment webhook replay", "status": "private", "severity": "high"},
        {"title": "Desync request smuggling", "status": "private", "severity": "high"},
        {"title": "Compression oracle test", "status": "public", "severity": "medium"},
        {"title": "Password policy weakness", "status": "public", "severity": "low"},
        {"title": "Error stack trace leak", "status": "public", "severity": "low"},
        {"title": "Predictable password reset token", "status": "private", "severity": "high"},
        {"title": "Side-channel timing probe", "status": "private", "severity": "medium"},
        {"title": "Deprecated cipher suite usage", "status": "public", "severity": "medium"},
    ]
    return render_template("reports_list.html", reports=sample_reports)


@reports_bp.route("/new", methods=["GET", "POST"])
def new_report() -> str:
    return render_template("report_new.html")
