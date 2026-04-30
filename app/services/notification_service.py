from app import db
from app.models.notification import Notification
from datetime import datetime


class NotificationService:
    @staticmethod
    def create_notification(user_id, actor_id, notification_type, post_id=None, comment_id=None):
        if user_id == actor_id:
            return None

        notification = Notification(
            user_id=user_id,
            actor_id=actor_id,
            notification_type=notification_type,
            post_id=post_id,
            comment_id=comment_id
        )
        db.session.add(notification)
        db.session.commit()

        return notification

    @staticmethod
    def get_user_notifications(user_id, limit=None, unread_only=False):
        query = Notification.query.filter_by(user_id=user_id)

        if unread_only:
            query = query.filter_by(is_read=False)

        query = query.order_by(Notification.created_at.desc())

        if limit:
            query = query.limit(limit)

        return query.all()

    @staticmethod
    def mark_as_read(notification_id):
        notification = Notification.query.get(notification_id)
        if notification:
            notification.is_read = True
            db.session.commit()
        return notification

    @staticmethod
    def mark_all_as_read(user_id):
        Notification.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
        db.session.commit()

    @staticmethod
    def delete_notification(notification_id):
        notification = Notification.query.get(notification_id)
        if notification:
            db.session.delete(notification)
            db.session.commit()
        return notification

    @staticmethod
    def get_unread_count(user_id):
        return Notification.query.filter_by(user_id=user_id, is_read=False).count()
