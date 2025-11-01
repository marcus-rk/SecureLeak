from flask import Blueprint, redirect, render_template, request, session, url_for

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login() -> str:
    if request.method == "POST":
        session["user_id"] = request.form.get("email", "demo@example.com")
        return redirect(url_for("reports.list_reports"))
    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register() -> str:
    if request.method == "POST":
        return redirect(url_for("auth.login"))
    return render_template("register.html")


@auth_bp.route("/logout", methods=["POST"])
def logout() -> str:
    session.clear()
    return redirect(url_for("auth.login"))
