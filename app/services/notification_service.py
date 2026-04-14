from app import db
from app.models.notification import Notification
from app.models.user import User


class NotificationService:
    @staticmethod
    def create_notification(user_id: int, message: str, category: str = "general") -> Notification:
        notification = Notification(
            user_id=user_id,
            message=message,
            category=category,
            is_read=False
        )
        db.session.add(notification)
        db.session.commit()
        return notification

    @staticmethod
    def mark_as_read(notification_id: int, user_id: int) -> bool:
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
        count = Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).update({'is_read': True})
        db.session.commit()
        return count

    @staticmethod
    def get_unread_count(user_id: int) -> int:
        return Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).count()

    @staticmethod
    def notify_by_role(role: str, message: str, category: str = "workflow"):
        users = User.query.filter_by(role=role, is_active=True).all()
        for user in users:
            db.session.add(Notification(user_id=user.id, message=message, category=category, is_read=False))
        db.session.commit()
