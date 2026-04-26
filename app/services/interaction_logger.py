"""
Interaction logging service for timeline and audit history.
"""
import json

from app import db
from app.models.interaction_log import InteractionLog


class InteractionLogger:
    """Convenience methods for writing and reading interaction history."""

    @staticmethod
    def log(actor_id, action_type, title, description=None, target_user_id=None,
            reference_type=None, reference_id=None, metadata=None, commit=True):
        """Persist an interaction entry."""
        payload = None
        if metadata is not None:
            payload = json.dumps(metadata, ensure_ascii=True, default=str)

        entry = InteractionLog(
            actor_id=actor_id,
            target_user_id=target_user_id,
            action_type=action_type,
            title=title,
            description=description,
            reference_type=reference_type,
            reference_id=reference_id,
            metadata_json=payload
        )
        db.session.add(entry)
        if commit:
            db.session.commit()
        return entry

    @staticmethod
    def get_user_history(user_id, limit=30):
        """History visible to a student: own actions and actions targeting them."""
        return InteractionLog.query.filter(
            (InteractionLog.actor_id == user_id) |
            (InteractionLog.target_user_id == user_id)
        ).order_by(InteractionLog.created_at.desc()).limit(limit).all()
