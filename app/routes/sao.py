from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app import db
from app.models.enrollment import Enrollment
from app.services.notification_service import NotificationService
from app.utils.helpers import role_required

sao_bp = Blueprint("sao", __name__)


@sao_bp.route("/dashboard")
@login_required
@role_required("sao")
def dashboard():
    queue = Enrollment.query.filter_by(status="pending_sao").order_by(Enrollment.created_at.asc()).all()
    return render_template("roles/sao_dashboard.html", queue=queue)


@sao_bp.route("/validate-id/<int:enrollment_id>", methods=["POST"])
@login_required
@role_required("sao")
def validate_id(enrollment_id):
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    action = request.form.get("action")
    if action == "approve":
        enrollment.status = "approved"
        enrollment.is_draft = False
        NotificationService.create_notification(enrollment.student_id, "Enrollment fully approved.", "status")
    else:
        enrollment.status = "rejected"
        enrollment.rejection_reason = request.form.get("reason", "Rejected by SAO.")
        NotificationService.create_notification(enrollment.student_id, "Enrollment rejected by SAO.", "status")

    db.session.commit()
    flash("SAO decision saved.", "success")
    return redirect(url_for("sao.dashboard"))
