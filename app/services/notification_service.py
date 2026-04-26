"""
Notification Service for creating and managing user notifications
"""
from app import db
from app.models.notification import Notification
from app.models.user import User
from datetime import datetime

class NotificationService:
    """Service for handling notifications"""
    
    @staticmethod
    def create_notification(user_id: int, message: str) -> Notification:
        """Create a new notification for a user"""
        notification = Notification(
            user_id=user_id,
            message=message,
            is_read=False
        )
        db.session.add(notification)
        db.session.commit()
        return notification
    
    @staticmethod
    def mark_as_read(notification_id: int, user_id: int) -> bool:
        """Mark a notification as read"""
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=user_id
        ).first()
        
        if notification:
            notification.is_read = True
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def mark_all_as_read(user_id: int) -> int:
        """Mark all notifications as read for a user"""
        count = Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).update({'is_read': True})
        db.session.commit()
        return count
    
    @staticmethod
    def get_unread_count(user_id: int) -> int:
        """Get count of unread notifications"""
        return Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).count()
    
    @staticmethod
    def notify_match_found(user_id: int, lost_item_name: str, match_score: float):
        """Notify user when a match is found"""
        message = f"Potential match found for '{lost_item_name}' (Match Score: {match_score}%)"
        return NotificationService.create_notification(user_id, message)
    
    @staticmethod
    def notify_item_claimed(user_id: int, item_name: str):
        """Notify user when item is claimed"""
        message = f"Your item '{item_name}' has been successfully claimed!"
        return NotificationService.create_notification(user_id, message)
    
    @staticmethod
    def notify_status_update(user_id: int, item_name: str, status: str):
        """Notify user of status update"""
        message = f"Status update for '{item_name}': {status}"
        return NotificationService.create_notification(user_id, message)

    @staticmethod
    def notify_staff_new_lost_item(student_name: str, item_name: str, category: str, location: str = None):
        """Notify all staff/admin users about a newly reported lost item."""
        location_text = location or 'Unknown location'
        message = (
            f"New lost report from {student_name}: '{item_name}' "
            f"[{category}] at {location_text}"
        )
        staff_users = User.query.filter(User.role.in_(['staff', 'admin'])).all()
        created = 0
        for staff_user in staff_users:
            notification = Notification(
                user_id=staff_user.id,
                message=message,
                is_read=False
            )
            db.session.add(notification)
            created += 1
        db.session.commit()
        return created
