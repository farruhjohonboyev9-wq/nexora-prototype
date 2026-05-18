from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.follow import Follow
from app.models.user import User
from app.service.notification import NotificationService
from fastapi import HTTPException


class FollowService:
    @staticmethod
    def follow_user(db: Session, follower_id: int, following_id: int) -> Follow:
        # Check if target user exists
        target_user = db.query(User).filter(User.id == following_id).first()
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Prevent self-follow
        if follower_id == following_id:
            raise HTTPException(status_code=400, detail="Cannot follow yourself")
        
        # Check if already following
        existing = db.query(Follow).filter(
            Follow.follower_id == follower_id,
            Follow.following_id == following_id
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Already following this user")
        
        try:
            follow = Follow(follower_id=follower_id, following_id=following_id)
            db.add(follow)
            db.commit()
            db.refresh(follow)

            NotificationService.create_notification(
                db,
                user_id=following_id,
                actor_id=follower_id,
                notification_type="follow"
            )
            return follow
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Error following user")
    
    @staticmethod
    def unfollow_user(db: Session, follower_id: int, following_id: int) -> None:
        follow = db.query(Follow).filter(
            Follow.follower_id == follower_id,
            Follow.following_id == following_id
        ).first()
        
        if not follow:
            raise HTTPException(status_code=404, detail="Not following this user")
        
        db.delete(follow)
        db.commit()
    
    @staticmethod
    def get_followers(db: Session, user_id: int, skip: int = 0, limit: int = 50):
        return db.query(Follow).filter(Follow.following_id == user_id).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_following(db: Session, user_id: int, skip: int = 0, limit: int = 50):
        return db.query(Follow).filter(Follow.follower_id == user_id).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_followers_count(db: Session, user_id: int) -> int:
        return db.query(Follow).filter(Follow.following_id == user_id).count()
    
    @staticmethod
    def get_following_count(db: Session, user_id: int) -> int:
        return db.query(Follow).filter(Follow.follower_id == user_id).count()
    
    @staticmethod
    def is_following(db: Session, follower_id: int, following_id: int) -> bool:
        follow = db.query(Follow).filter(
            Follow.follower_id == follower_id,
            Follow.following_id == following_id
        ).first()
        return follow is not None
