from sqlalchemy.orm import Session
from app.models.comment import Comment
from app.models.post import Post
from app.schemas.comment import CommentCreate
from app.service.notification import NotificationService
from fastapi import HTTPException


class CommentService:
    @staticmethod
    def create_comment(db: Session, post_id: int, author_id: int, data: CommentCreate) -> Comment:
        # Check if post exists
        
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        comment = Comment(
            post_id=post_id,
            author_id=author_id,
            content=data.content
        )
        db.add(comment)
        db.commit()
        db.refresh(comment)

        NotificationService.create_notification(
            db,
            user_id=post.author_id,
            actor_id=author_id,
            notification_type="comment",
            post_id=post_id,
            comment_id=comment.id
        )
        return comment
    
    @staticmethod
    def get_comment(db: Session, comment_id: int) -> Comment:
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        return comment
    
    @staticmethod
    def get_comments_by_post(db: Session, post_id: int, skip: int = 0, limit: int = 50):
        return db.query(Comment).filter(Comment.post_id == post_id)\
            .order_by(Comment.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def delete_comment(db: Session, comment_id: int, author_id: int) -> None:
        comment = CommentService.get_comment(db, comment_id)
        
        if comment.author_id != author_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
        
        db.delete(comment)
        db.commit()
    
    @staticmethod
    def get_comment_count(db: Session, post_id: int) -> int:
        return db.query(Comment).filter(Comment.post_id == post_id).count()
