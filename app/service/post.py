from sqlalchemy.orm import Session
from app.models.post import Post
from app.models.like import Like
from app.models.comment import Comment
from app.schemas.post import PostCreate, PostUpdate
from app.service.hashtag import HashtagService
from app.models.hashtag_post import PostHashtag
from fastapi import HTTPException


class PostService:
    @staticmethod
    def create_post(db: Session, author_id: int, data: PostCreate) -> Post:
        post = Post(
            author_id=author_id,
            content=data.content,
            media_url=data.media_url
        )
        db.add(post)
        db.commit()
        db.refresh(post)

        hashtag_names = HashtagService.extract_hashtags(data.content)
        if hashtag_names:
            HashtagService.sync_post_hashtags(db, post.id, hashtag_names)

        return post
    
    @staticmethod
    def get_post(db: Session, post_id: int) -> Post:
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        return post
    
    @staticmethod
    def get_all_posts(db: Session, skip: int = 0, limit: int = 20):
        return db.query(Post).order_by(Post.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_post(db: Session, post_id: int, author_id: int, data: PostUpdate) -> Post:
        post = PostService.get_post(db, post_id)
        
        if post.author_id != author_id:
            raise HTTPException(status_code=403, detail="Not authorized to update this post")
        
        if data.content is not None:
            post.content = data.content
            hashtag_names = HashtagService.extract_hashtags(data.content)
            HashtagService.sync_post_hashtags(db, post.id, hashtag_names)
        if data.media_url is not None:
            post.media_url = data.media_url
        
        db.commit()
        db.refresh(post)
        return post
    
    @staticmethod
    def delete_post(db: Session, post_id: int, author_id: int) -> None:
        post = PostService.get_post(db, post_id)
        
        if post.author_id != author_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this post")
        
        db.delete(post)
        db.commit()
    
    @staticmethod
    def get_like_count(db: Session, post_id: int) -> int:
        return db.query(Like).filter(Like.post_id == post_id).count()
    
    @staticmethod
    def get_comment_count(db: Session, post_id: int) -> int:
        return db.query(Comment).filter(Comment.post_id == post_id).count()
