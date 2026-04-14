from datetime import datetime

from app import db


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    enrollment_id = db.Column(db.Integer, db.ForeignKey("enrollments.id"), nullable=False, index=True)
    amount = db.Column(db.Numeric(10, 2), nullable=True)
    reference_number = db.Column(db.String(120), nullable=True)
    receipt_path = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(40), nullable=False, default="pending")
    verified_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    verified_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    enrollment = db.relationship("Enrollment", back_populates="payments")
