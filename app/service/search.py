from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.models.user import User
from app.models.post import Post
from app.models.hashtag import Hashtag
from app.models.hashtag_post import PostHashtag
from fastapi import HTTPException


class SearchService:
    @staticmethod
    def search_users(db: Session, query: str, limit: int = 10) -> list:
        """Search users by username or bio"""
        if not query or len(query) < 2:
            raise HTTPException(status_code=400, detail="Query too short")
        
        search_term = f"%{query}%"
        users = db.query(User).filter(
            or_(
                User.username.ilike(search_term),
                User.bio.ilike(search_term)
            )
        ).limit(limit).all()
        
        return users
    
    @staticmethod
    def search_posts(db: Session, query: str, limit: int = 20) -> list:
        """Search posts by content or hashtag"""
        if not query or len(query) < 2:
            raise HTTPException(status_code=400, detail="Query too short")
        
        search_term = f"%{query}%"
        posts = db.query(Post).outerjoin(
            PostHashtag,
            Post.id == PostHashtag.post_id
        ).outerjoin(
            Hashtag,
            Hashtag.id == PostHashtag.hashtag_id
        ).filter(
            or_(
                Post.content.ilike(search_term),
                Hashtag.name.ilike(search_term)
            )
        ).order_by(Post.created_at.desc()).distinct().limit(limit).all()
        
        return posts
    
    @staticmethod
    def search_hashtags(db: Session, query: str, limit: int = 10) -> list:
        """Search hashtags by name"""
        if not query or len(query) < 1:
            raise HTTPException(status_code=400, detail="Query too short")
        
        search_term = f"%{query}%"
        hashtags = db.query(Hashtag).filter(
            Hashtag.name.ilike(search_term)
        ).limit(limit).all()
        
        return hashtags
