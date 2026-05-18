from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.hashtag import Hashtag
from app.models.hashtag_post import PostHashtag
from app.models.post import Post
import re


class HashtagService:
    HASHTAG_PATTERN = r'#(\w+)'
    
    @staticmethod
    def extract_hashtags(text: str) -> list:
        """Extract hashtags from text"""
        if not text:
            return []
        
        hashtags = re.findall(HashtagService.HASHTAG_PATTERN, text)
        return [tag.lower() for tag in hashtags]
    
    @staticmethod
    def create_or_get_hashtags(db: Session, hashtag_names: list) -> list:
        """Create or get hashtags"""
        hashtags = []
        
        for name in hashtag_names:
            tag = db.query(Hashtag).filter(Hashtag.name == name.lower()).first()
            
            if not tag:
                tag = Hashtag(name=name.lower())
                db.add(tag)
            
            hashtags.append(tag)
        
        db.commit()
        return hashtags
    
    @staticmethod
    def attach_hashtags_to_post(db: Session, post_id: int, hashtag_ids: list) -> None:
        """Attach hashtags to a post"""
        for hashtag_id in hashtag_ids:
            # Check if already attached
            existing = db.query(PostHashtag).filter(
                PostHashtag.post_id == post_id,
                PostHashtag.hashtag_id == hashtag_id
            ).first()
            
            if not existing:
                post_hashtag = PostHashtag(post_id=post_id, hashtag_id=hashtag_id)
                db.add(post_hashtag)
        
        db.commit()

    @staticmethod
    def sync_post_hashtags(db: Session, post_id: int, hashtag_names: list) -> None:
        """Sync post hashtags by removing old tags and attaching new ones"""
        tags = HashtagService.create_or_get_hashtags(db, hashtag_names)
        db.query(PostHashtag).filter(PostHashtag.post_id == post_id).delete()
        db.commit()
        HashtagService.attach_hashtags_to_post(db, post_id, [tag.id for tag in tags])
    
    @staticmethod
    def get_hashtag_posts(db: Session, hashtag_id: int, skip: int = 0, limit: int = 20):
        """Get posts for a hashtag"""
        posts = db.query(Post).join(
            PostHashtag,
            Post.id == PostHashtag.post_id
        ).filter(
            PostHashtag.hashtag_id == hashtag_id
        ).order_by(Post.created_at.desc()).offset(skip).limit(limit).all()
        
        return posts
    
    @staticmethod
    def get_trending_hashtags(db: Session, limit: int = 10) -> list:
        """Get trending hashtags by post count"""
        trending = db.query(
            Hashtag.name,
            func.count(PostHashtag.post_id).label("post_count")
        ).join(
            PostHashtag,
            Hashtag.id == PostHashtag.hashtag_id
        ).group_by(Hashtag.id, Hashtag.name).order_by(
            desc("post_count")
        ).limit(limit).all()
        
        return trending
    
    @staticmethod
    def get_hashtag_by_name(db: Session, name: str) -> Hashtag:
        """Get hashtag by name"""
        return db.query(Hashtag).filter(
            Hashtag.name == name.lower()
        ).first()
