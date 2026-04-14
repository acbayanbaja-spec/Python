from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app import db
from app.models.enrollment import Enrollment
from app.services.notification_service import NotificationService
from app.utils.helpers import role_required

department_bp = Blueprint("department", __name__)


@department_bp.route("/dashboard")
@login_required
@role_required("department")
def dashboard():
    queue = Enrollment.query.filter_by(status="pending_department").order_by(Enrollment.created_at.asc()).all()
    return render_template("roles/department_dashboard.html", queue=queue)


@department_bp.route("/validate/<int:enrollment_id>", methods=["POST"])
@login_required
@role_required("department")
def validate(enrollment_id):
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    action = request.form.get("action")
    if action == "approve":
        enrollment.status = "pending_sao"
        NotificationService.notify_by_role("sao", "Department validated an enrollment for ID verification.")
        NotificationService.create_notification(enrollment.student_id, "Department validated your subjects.")
    else:
        enrollment.status = "rejected"
        enrollment.rejection_reason = request.form.get("reason", "Rejected by department.")
        NotificationService.create_notification(enrollment.student_id, "Enrollment rejected by department.", "status")
    db.session.commit()
    flash("Department review saved.", "success")
    return redirect(url_for("department.dashboard"))
