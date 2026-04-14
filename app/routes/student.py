from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.models.enrollment import Enrollment
from app.models.notification import Notification
from app.services.ai_recommender import detect_irregular_status, recommend_subjects
from app.services.notification_service import NotificationService
from app.utils.helpers import role_required, save_uploaded_file

student_bp = Blueprint("student", __name__)


@student_bp.route("/dashboard")
@login_required
@role_required("student")
def dashboard():
    enrollments = Enrollment.query.filter_by(student_id=current_user.id).order_by(Enrollment.created_at.desc()).all()
    recommendations = recommend_subjects(current_user.id)
    irregular = detect_irregular_status(current_user.id)
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(6).all()
    return render_template(
        "student/dashboard.html",
        enrollments=enrollments,
        recommendations=recommendations,
        irregular=irregular,
        notifications=notifications,
    )


@student_bp.route("/enrollment/new", methods=["GET", "POST"])
@login_required
@role_required("student")
def new_enrollment():
    if request.method == "POST":
        action = request.form.get("action", "submit")
        payment_file = request.files.get("payment_receipt")
        id_file = request.files.get("id_document")

        enrollment = Enrollment(
            student_id=current_user.id,
            semester=request.form.get("semester", "1st Semester"),
            school_year=request.form.get("school_year", "2026-2027"),
            program=request.form.get("program", "BSIT"),
            year_level=int(request.form.get("year_level", current_user.year_level)),
            is_new_student=request.form.get("is_new_student") == "yes",
            notes=request.form.get("notes", "").strip(),
            is_draft=(action == "save_draft"),
            status="draft" if action == "save_draft" else "submitted",
        )

        if payment_file and payment_file.filename:
            enrollment.payment_receipt_path = save_uploaded_file(payment_file, "payments")
        if id_file and id_file.filename:
            enrollment.id_document_path = save_uploaded_file(id_file, "ids")

        if action != "save_draft":
            enrollment.status = "pending_registrar" if enrollment.is_new_student else "pending_accounting"
            next_role = "registrar" if enrollment.is_new_student else "accounting"
            NotificationService.notify_by_role(next_role, f"New enrollment submitted by {current_user.full_name}.")

        db.session.add(enrollment)
        db.session.commit()
        flash("Enrollment saved." if action == "save_draft" else "Enrollment submitted successfully.", "success")
        return redirect(url_for("student.dashboard"))
    return render_template("student/enrollment_form.html")


@student_bp.route("/history")
@login_required
@role_required("student")
def history():
    enrollments = Enrollment.query.filter_by(student_id=current_user.id).order_by(Enrollment.created_at.desc()).all()
    return render_template("student/history.html", enrollments=enrollments)
