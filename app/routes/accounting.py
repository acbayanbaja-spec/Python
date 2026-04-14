from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.models.enrollment import Enrollment
from app.models.payment import Payment
from app.services.notification_service import NotificationService
from app.utils.helpers import role_required

accounting_bp = Blueprint("accounting", __name__)


@accounting_bp.route("/dashboard")
@login_required
@role_required("accounting")
def dashboard():
    queue = Enrollment.query.filter_by(status="pending_accounting").order_by(Enrollment.created_at.asc()).all()
    return render_template("roles/accounting_dashboard.html", queue=queue)


@accounting_bp.route("/verify/<int:enrollment_id>", methods=["POST"])
@login_required
@role_required("accounting")
def verify(enrollment_id):
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    action = request.form.get("action")
    if action == "approve":
        enrollment.status = "pending_department"
        payment = Payment(
            enrollment_id=enrollment.id,
            amount=request.form.get("amount") or None,
            reference_number=request.form.get("reference_number"),
            receipt_path=enrollment.payment_receipt_path,
            status="verified",
            verified_by=current_user.id,
            verified_at=datetime.utcnow(),
        )
        db.session.add(payment)
        NotificationService.notify_by_role("department", "Accounting verified a payment for subject validation.")
        NotificationService.create_notification(enrollment.student_id, "Payment verified. Proceeding to department review.")
    else:
        enrollment.status = "rejected"
        enrollment.rejection_reason = request.form.get("reason", "Rejected by accounting.")
        NotificationService.create_notification(enrollment.student_id, "Enrollment rejected by accounting.", "status")

    db.session.commit()
    flash("Verification result saved.", "success")
    return redirect(url_for("accounting.dashboard"))
