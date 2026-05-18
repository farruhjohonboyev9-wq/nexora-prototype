from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.hashtag import HashtagResponse, TrendingHashtagResponse
from app.service.hashtag import HashtagService

router = APIRouter(prefix="/hashtags", tags=["hashtags"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user_obj(email: str = Depends(get_current_user), db: Session = Depends(get_db)) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.get("/trending", response_model=list[TrendingHashtagResponse])
def get_trending(
    limit: int = 10,
    current_user: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db)
):
    """Get trending hashtags"""
    trending = HashtagService.get_trending_hashtags(db, limit)
    return [
        {
            "name": name,
            "post_count": count,
            "rank": idx + 1
        }
        for idx, (name, count) in enumerate(trending)
    ]


@router.get("/{hashtag_name}/posts")
def get_hashtag_posts(
    hashtag_name: str,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db)
):
    """Get posts for a hashtag"""
    hashtag = HashtagService.get_hashtag_by_name(db, hashtag_name)
    
    if not hashtag:
        raise HTTPException(status_code=404, detail="Hashtag not found")
    
    posts = HashtagService.get_hashtag_posts(db, hashtag.id, skip, limit)
    
    return [
        {
            "id": p.id,
            "content": p.content,
            "author_id": p.author_id,
            "media_url": p.media_url,
            "created_at": p.created_at,
            "author": {
                "id": p.author.id,
                "username": p.author.username,
                "profile_pic_url": p.author.profile_pic_url
            }
        }
        for p in posts
    ]
