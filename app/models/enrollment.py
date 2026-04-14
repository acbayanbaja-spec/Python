from datetime import datetime

from app import db


class Enrollment(db.Model):
    __tablename__ = "enrollments"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    semester = db.Column(db.String(50), nullable=False)
    school_year = db.Column(db.String(20), nullable=False)
    program = db.Column(db.String(120), nullable=False)
    year_level = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(40), nullable=False, default="draft")
    is_draft = db.Column(db.Boolean, default=True)
    is_new_student = db.Column(db.Boolean, default=False)
    payment_receipt_path = db.Column(db.String(255), nullable=True)
    id_document_path = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student = db.relationship("User", back_populates="enrollments")
    payments = db.relationship("Payment", back_populates="enrollment", cascade="all, delete-orphan")

    def next_status(self):
        if self.is_new_student and self.status == "submitted":
            return "pending_registrar"
        if not self.is_new_student and self.status == "submitted":
            return "pending_accounting"
        if self.status in ("pending_registrar", "pending_accounting"):
            return "pending_department"
        if self.status == "pending_department":
            return "pending_sao"
        if self.status == "pending_sao":
            return "approved"
        return self.status
