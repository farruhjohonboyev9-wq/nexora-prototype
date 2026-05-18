from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.post import Post
from app.models.follow import Follow
from app.models.user import User


class FeedService:
    @staticmethod
    def get_personalized_feed(db: Session, user_id: int, skip: int = 0, limit: int = 20):
        """Get feed with posts from followed users"""
        # Get list of user IDs that current user follows
        following_ids = db.query(Follow.following_id).filter(
            Follow.follower_id == user_id
        ).all()
        
        following_ids = [f[0] for f in following_ids]
        
        # Include own posts as well
        following_ids.append(user_id)
        
        if not following_ids:
            return []
        
        # Get posts from followed users, sorted by latest
        posts = db.query(Post).filter(
            Post.author_id.in_(following_ids)
        ).order_by(Post.created_at.desc()).offset(skip).limit(limit).all()
        
        return posts
    
    @staticmethod
    def get_feed_by_engagement(db: Session, user_id: int, skip: int = 0, limit: int = 20):
        """Get feed sorted by engagement (likes + comments)"""
        from sqlalchemy import func, and_
        from app.models.like import Like
        from app.models.comment import Comment
        
        # Get followed user IDs
        following_ids = db.query(Follow.following_id).filter(
            Follow.follower_id == user_id
        ).all()
        
        following_ids = [f[0] for f in following_ids]
        following_ids.append(user_id)
        
        if not following_ids:
            return []
        
        # Calculate engagement score (likes + comments)
        posts = db.query(Post).outerjoin(Like).outerjoin(Comment).filter(
            Post.author_id.in_(following_ids)
        ).group_by(Post.id).order_by(
            func.count(Like.id) + func.count(Comment.id) * 2
        ).offset(skip).limit(limit).all()
        
        return posts
    
    @staticmethod
    def get_user_feed(db: Session, user_id: int, skip: int = 0, limit: int = 20):
        """Get posts from a specific user"""
        posts = db.query(Post).filter(
            Post.author_id == user_id
        ).order_by(Post.created_at.desc()).offset(skip).limit(limit).all()
        
        return posts
