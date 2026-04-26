"""
Interaction log model for audit-ready activity history.
"""
from app import db
from datetime import datetime


class InteractionLog(db.Model):
    """Tracks meaningful system interactions by students and staff."""
    __tablename__ = 'interaction_logs'

    id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    target_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    action_type = db.Column(db.String(50), nullable=False, index=True)
    title = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text)
    reference_type = db.Column(db.String(50), nullable=True, index=True)
    reference_id = db.Column(db.Integer, nullable=True, index=True)
    metadata_json = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Relationship for actor user account
    actor = db.relationship('User', foreign_keys=[actor_id], backref='interaction_logs')

    def __repr__(self):
        return f'<InteractionLog {self.action_type} by {self.actor_id}>'
