"""
Found Item model for staff-logged found items
"""
from app import db
from datetime import datetime

class FoundItem(db.Model):
    """Found item logged by staff"""
    __tablename__ = 'found_items'
    
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    item_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False, index=True)
    color = db.Column(db.String(50))
    date_found = db.Column(db.Date, nullable=False)
    location_found = db.Column(db.String(200))
    storage_location = db.Column(db.String(200))
    priority_flag = db.Column(db.Boolean, default=False, index=True)
    image_path = db.Column(db.String(255))
    status = db.Column(db.String(20), default='available', index=True)  # available, matched, claimed
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    staff = db.relationship('User', backref='found_items_logged')
    matches = db.relationship('Match', backref='found_item', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<FoundItem {self.item_name}>'
