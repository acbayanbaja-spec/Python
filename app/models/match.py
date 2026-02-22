"""
Match model for AI-matched lost and found items
"""
from app import db
from datetime import datetime

class Match(db.Model):
    """Match between lost and found items"""
    __tablename__ = 'matches'
    
    id = db.Column(db.Integer, primary_key=True)
    lost_item_id = db.Column(db.Integer, db.ForeignKey('lost_items.id'), nullable=False, index=True)
    found_item_id = db.Column(db.Integer, db.ForeignKey('found_items.id'), nullable=False, index=True)
    score = db.Column(db.Float, nullable=False)  # 0-100 match score
    status = db.Column(db.String(20), default='suggested', index=True)  # suggested, confirmed, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Ensure unique match per lost-found pair
    __table_args__ = (db.UniqueConstraint('lost_item_id', 'found_item_id', name='unique_match'),)
    
    def __repr__(self):
        return f'<Match {self.lost_item_id}-{self.found_item_id} (score: {self.score})>'
