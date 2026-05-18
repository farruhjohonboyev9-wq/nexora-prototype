from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.like import LikeResponse, LikeCountResponse
from app.service.like import LikeService

router = APIRouter(prefix="/likes", tags=["likes"])


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


@router.post("/posts/{post_id}", response_model=LikeResponse)
def like_post(
    post_id: int,
    current_user: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db)
):
    """Like a post"""
    like = LikeService.like_post(db, current_user.id, post_id)
    return like


@router.delete("/posts/{post_id}")
def unlike_post(
    post_id: int,
    current_user: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db)
):
    """Unlike a post"""
    LikeService.unlike_post(db, current_user.id, post_id)
    return {"message": "Post unliked successfully"}


@router.get("/posts/{post_id}/count", response_model=LikeCountResponse)
def get_like_count(
    post_id: int,
    current_user: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db)
):
    """Get like count and check if current user liked"""
    like_count = LikeService.get_like_count(db, post_id)
    is_liked = LikeService.is_liked_by_user(db, current_user.id, post_id)
    
    return {
        "post_id": post_id,
        "like_count": like_count,
        "is_liked": is_liked
    }
