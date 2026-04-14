"""
User model for authentication and role management
"""
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    """User model with role-based access control"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # admin, staff, student
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    lost_items = db.relationship('LostItem', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    # Specify primaryjoin to resolve ambiguity (user_id vs released_by)
    # This relationship is for claims made BY the user (user_id), not claims processed BY the user (released_by)
    claims = db.relationship('Claim', primaryjoin='User.id == Claim.user_id', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin'
    
    def is_staff(self):
        """Check if user is staff"""
        return self.role == 'staff'
    
    def is_student(self):
        """Check if user is student"""
        return self.role == 'student'
    
    def __repr__(self):
        return f'<User {self.email}>'
