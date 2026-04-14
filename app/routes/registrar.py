from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app import db
from app.models.enrollment import Enrollment
from app.services.notification_service import NotificationService
from app.utils.helpers import role_required

registrar_bp = Blueprint("registrar", __name__)


@registrar_bp.route("/dashboard")
@login_required
@role_required("registrar")
def dashboard():
    queue = Enrollment.query.filter_by(status="pending_registrar").order_by(Enrollment.created_at.asc()).all()
    return render_template("roles/registrar_dashboard.html", queue=queue)


@registrar_bp.route("/review/<int:enrollment_id>", methods=["POST"])
@login_required
@role_required("registrar")
def review(enrollment_id):
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    action = request.form.get("action")
    if action == "approve":
        enrollment.status = "pending_department"
        NotificationService.notify_by_role("department", "Registrar approved an enrollment for subject validation.")
        NotificationService.create_notification(enrollment.student_id, "Registrar approved your enrollment.")
    else:
        enrollment.status = "rejected"
        enrollment.rejection_reason = request.form.get("reason", "Rejected by registrar.")
        NotificationService.create_notification(enrollment.student_id, "Enrollment rejected by registrar.", "status")
    db.session.commit()
    flash("Enrollment updated.", "success")
    return redirect(url_for("registrar.dashboard"))
