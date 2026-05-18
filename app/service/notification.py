from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.notification import Notification
from app.models.user import User
from fastapi import HTTPException
import re


class NotificationService:
    @staticmethod
    def create_notification(
        db: Session,
        user_id: int,
        actor_id: int,
        notification_type: str,
        post_id: int = None,
        comment_id: int = None
    ) -> Notification:
        """Create a new notification"""
        # Prevent self-notifications
        if user_id == actor_id:
            return None
        
        # Check for duplicate like/follow/comment notifications
        query = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.actor_id == actor_id,
            Notification.notification_type == notification_type,
            Notification.is_read == False
        )

        if notification_type == "like":
            query = query.filter(Notification.post_id == post_id)
        elif notification_type == "comment":
            query = query.filter(Notification.comment_id == comment_id)

        existing = query.first()
        if existing:
            return existing
        
        notification = Notification(
            user_id=user_id,
            actor_id=actor_id,
            notification_type=notification_type,
            post_id=post_id,
            comment_id=comment_id
        )
        
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification
    
    @staticmethod
    def get_user_notifications(db: Session, user_id: int, skip: int = 0, limit: int = 20):
        """Get notifications for a user"""
        notifications = db.query(Notification).filter(
            Notification.user_id == user_id
        ).order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
        
        return notifications
    
    @staticmethod
    def mark_as_read(db: Session, notification_id: int, user_id: int) -> Notification:
        """Mark notification as read"""
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        notification.is_read = True
        db.commit()
        db.refresh(notification)
        return notification
    
    @staticmethod
    def mark_all_as_read(db: Session, user_id: int) -> None:
        """Mark all notifications as read"""
        db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({"is_read": True})
        db.commit()
    
    @staticmethod
    def get_unread_count(db: Session, user_id: int) -> int:
        """Get count of unread notifications"""
        return db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).count()
    
    @staticmethod
    def delete_notification(db: Session, notification_id: int, user_id: int) -> None:
        """Delete a notification"""
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        db.delete(notification)
        db.commit()
