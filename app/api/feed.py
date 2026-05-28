from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import traceback

from app.db.session import SessionLocal
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.post import PostDetailResponse
from app.service.feed import FeedService

router = APIRouter(prefix="/feed", tags=["feed"])


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


@router.get("/personalized", response_model=list[PostDetailResponse])
def get_personalized_feed(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db)
):
    """Get personalized feed (posts from followed users) - REQUIRES AUTH"""
    try:
        from app.service.post import PostService
        
        posts = FeedService.get_personalized_feed(db, current_user.id, skip, limit)
        
        return [
            {
                "id": p.id,
                "author_id": p.author_id,
                "content": p.content,
                "media_url": p.media_url,
                "created_at": p.created_at,
                "updated_at": p.updated_at,
                "author": {
                    "id": p.author.id,
                    "username": p.author.username,
                    "profile_pic_url": p.author.profile_pic_url
                },
                "like_count": PostService.get_like_count(db, p.id),
                "comment_count": PostService.get_comment_count(db, p.id)
            }
            for p in posts
        ]
    except Exception as e:
        print(f"❌ Personalized feed error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/engagement", response_model=list[PostDetailResponse])
def get_feed_by_engagement(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get feed sorted by engagement (likes + comments) - PUBLIC endpoint"""
    try:
        from app.service.post import PostService
        
        posts = FeedService.get_feed_by_engagement(db, None, skip, limit)
        
        return [
            {
                "id": p.id,
                "author_id": p.author_id,
                "content": p.content,
                "media_url": p.media_url,
                "created_at": p.created_at,
                "updated_at": p.updated_at,
                "author": {
                    "id": p.author.id,
                    "username": p.author.username,
                    "profile_pic_url": p.author.profile_pic_url
                },
                "like_count": PostService.get_like_count(db, p.id),
                "comment_count": PostService.get_comment_count(db, p.id)
            }
            for p in posts
        ]
    except Exception as e:
        print(f"❌ Engagement feed error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/users/{user_id}", response_model=list[PostDetailResponse])
def get_user_feed(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get feed from a specific user - PUBLIC endpoint"""
    try:
        from app.service.post import PostService
        
        posts = FeedService.get_user_feed(db, user_id, skip, limit)
        
        return [
            {
                "id": p.id,
                "author_id": p.author_id,
                "content": p.content,
                "media_url": p.media_url,
                "created_at": p.created_at,
                "updated_at": p.updated_at,
                "author": {
                    "id": p.author.id,
                    "username": p.author.username,
                    "profile_pic_url": p.author.profile_pic_url
                },
                "like_count": PostService.get_like_count(db, p.id),
                "comment_count": PostService.get_comment_count(db, p.id)
            }
            for p in posts
        ]
    except Exception as e:
        print(f"❌ User feed error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
