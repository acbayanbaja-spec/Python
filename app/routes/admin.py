import csv
import io

from flask import Blueprint, flash, redirect, render_template, request, send_file, url_for
from flask_login import login_required
from sqlalchemy import func

from app import db
from app.models.enrollment import Enrollment
from app.models.user import User
from app.utils.helpers import role_required

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/dashboard")
@login_required
@role_required("admin")
def dashboard():
    total_enrolled = Enrollment.query.filter_by(status="approved").count()
    pending_approvals = Enrollment.query.filter(Enrollment.status.like("pending_%")).count()
    total_users = User.query.count()
    status_breakdown = (
        db.session.query(Enrollment.status, func.count(Enrollment.id))
        .group_by(Enrollment.status)
        .all()
    )
    return render_template(
        "admin/dashboard.html",
        total_enrolled=total_enrolled,
        pending_approvals=pending_approvals,
        total_users=total_users,
        status_breakdown=status_breakdown,
    )


@admin_bp.route("/users", methods=["GET", "POST"])
@login_required
@role_required("admin")
def users():
    if request.method == "POST":
        user = User(
            full_name=request.form.get("full_name", "").strip(),
            email=request.form.get("email", "").strip().lower(),
            role=request.form.get("role", "student"),
            student_number=request.form.get("student_number") or None,
            year_level=int(request.form.get("year_level", 1)),
        )
        user.set_password(request.form.get("password", "password123"))
        db.session.add(user)
        db.session.commit()
        flash("User created.", "success")
        return redirect(url_for("admin.users"))
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=users)


@admin_bp.route("/reports")
@login_required
@role_required("admin")
def reports():
    approved = Enrollment.query.filter_by(status="approved").count()
    pending = Enrollment.query.filter(Enrollment.status.like("pending_%")).count()
    rejected = Enrollment.query.filter_by(status="rejected").count()
    return render_template("admin/reports.html", approved=approved, pending=pending, rejected=rejected)


@admin_bp.route("/export-csv")
@login_required
@role_required("admin")
def export_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Enrollment ID", "Student", "Semester", "School Year", "Status"])
    rows = Enrollment.query.all()
    for row in rows:
        writer.writerow([row.id, row.student.full_name, row.semester, row.school_year, row.status])

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype="text/csv",
        as_attachment=True,
        download_name="enrollment_report.csv",
    )
