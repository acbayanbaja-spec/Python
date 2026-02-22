"""
Claim model for QR code-based item claims
"""
from app import db
from datetime import datetime

class Claim(db.Model):
    """Claim record for item retrieval"""
    __tablename__ = 'claims'
    
    id = db.Column(db.Integer, primary_key=True)
    claim_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('lost_items.id'), nullable=False)
    release_status = db.Column(db.String(20), default='pending', index=True)  # pending, released, cancelled
    released_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    release_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationship
    released_by_user = db.relationship('User', foreign_keys=[released_by], backref='claims_processed')
    
    def __repr__(self):
        return f'<Claim {self.claim_code}>'
