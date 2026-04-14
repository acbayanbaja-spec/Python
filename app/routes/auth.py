from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app import db
from app.models.user import User

auth_bp = Blueprint("auth", __name__)


def _redirect_by_role(user):
    endpoint_map = {
        "student": "student.dashboard",
        "registrar": "registrar.dashboard",
        "accounting": "accounting.dashboard",
        "admin": "admin.dashboard",
        "sao": "sao.dashboard",
        "department": "department.dashboard",
    }
    return redirect(url_for(endpoint_map.get(user.role, "auth.login")))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return _redirect_by_role(current_user)

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        student_number = request.form.get("student_number", "").strip()
        year_level = int(request.form.get("year_level", 1))

        if not full_name or not email or not password or not student_number:
            flash("All fields are required.", "danger")
            return render_template("auth/register.html")
        if User.query.filter_by(email=email).first():
            flash("Email already exists.", "warning")
            return render_template("auth/register.html")

        student = User(
            full_name=full_name,
            email=email,
            role="student",
            student_number=student_number,
            year_level=year_level,
        )
        student.set_password(password)
        db.session.add(student)
        db.session.commit()
        flash("Student account created. Please login.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return _redirect_by_role(current_user)
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return _redirect_by_role(user)
        flash("Invalid credentials.", "danger")
    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
