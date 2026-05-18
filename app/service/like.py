from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.like import Like
from app.models.post import Post
from app.service.notification import NotificationService
from fastapi import HTTPException


class LikeService:
    @staticmethod
    def like_post(db: Session, user_id: int, post_id: int) -> Like:
        # Check if post exists
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # Check if already liked
        existing_like = db.query(Like).filter(
            Like.user_id == user_id,
            Like.post_id == post_id
        ).first()
        
        if existing_like:
            raise HTTPException(status_code=400, detail="Post already liked")
        
        try:
            like = Like(user_id=user_id, post_id=post_id)
            db.add(like)
            db.commit()
            db.refresh(like)

            NotificationService.create_notification(
                db,
                user_id=post.author_id,
                actor_id=user_id,
                notification_type="like",
                post_id=post_id
            )
            return like
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Error liking post")
    
    @staticmethod
    def unlike_post(db: Session, user_id: int, post_id: int) -> None:
        like = db.query(Like).filter(
            Like.user_id == user_id,
            Like.post_id == post_id
        ).first()
        
        if not like:
            raise HTTPException(status_code=404, detail="Like not found")
        
        db.delete(like)
        db.commit()
    
    @staticmethod
    def get_like_count(db: Session, post_id: int) -> int:
        return db.query(Like).filter(Like.post_id == post_id).count()
    
    @staticmethod
    def is_liked_by_user(db: Session, user_id: int, post_id: int) -> bool:
        like = db.query(Like).filter(
            Like.user_id == user_id,
            Like.post_id == post_id
        ).first()
        return like is not None
