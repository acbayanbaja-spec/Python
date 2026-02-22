"""
Lost Item model for user-reported lost items
"""
from app import db
from datetime import datetime

class LostItem(db.Model):
    """Lost item reported by users"""
    __tablename__ = 'lost_items'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    item_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False, index=True)
    color = db.Column(db.String(50))
    date_lost = db.Column(db.Date, nullable=False)
    location_lost = db.Column(db.String(200))
    image_path = db.Column(db.String(255))
    status = db.Column(db.String(20), default='pending', index=True)  # pending, matched, claimed
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    matches = db.relationship('Match', backref='lost_item', lazy='dynamic', cascade='all, delete-orphan')
    claims = db.relationship('Claim', backref='lost_item', lazy='dynamic', cascade='all, delete-orphan')
    
    def is_high_priority(self):
        """Check if item is in common categories (high priority)"""
        common_categories = ['ID', 'Wallet', 'Phone']
        return self.category in common_categories
    
    def __repr__(self):
        return f'<LostItem {self.item_name}>'
