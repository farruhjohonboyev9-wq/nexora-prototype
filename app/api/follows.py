from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.follow import FollowResponse, FollowerResponse, FollowStatusResponse
from app.service.follow import FollowService

router = APIRouter(prefix="/follows", tags=["follows"])


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


@router.post("/users/{user_id}", response_model=FollowResponse)
def follow_user(
    user_id: int,
    current_user: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db)
):
    """Follow a user"""
    follow = FollowService.follow_user(db, current_user.id, user_id)
    return follow


@router.delete("/users/{user_id}")
def unfollow_user(
    user_id: int,
    current_user: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db)
):
    """Unfollow a user"""
    FollowService.unfollow_user(db, current_user.id, user_id)
    return {"message": "Unfollowed successfully"}


@router.get("/users/{user_id}/followers", response_model=list[FollowerResponse])
def get_followers(
    user_id: int,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db)
):
    """Get followers of a user"""
    follows = FollowService.get_followers(db, user_id, skip, limit)
    return [f.follower for f in follows]


@router.get("/users/{user_id}/following", response_model=list[FollowerResponse])
def get_following(
    user_id: int,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db)
):
    """Get users that a user follows"""
    follows = FollowService.get_following(db, user_id, skip, limit)
    return [f.following for f in follows]


@router.get("/users/{user_id}/status", response_model=FollowStatusResponse)
def get_follow_status(
    user_id: int,
    current_user: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db)
):
    """Get follow status and counts"""
    is_following = FollowService.is_following(db, current_user.id, user_id)
    followers_count = FollowService.get_followers_count(db, user_id)
    following_count = FollowService.get_following_count(db, user_id)
    
    return {
        "is_following": is_following,
        "followers_count": followers_count,
        "following_count": following_count
    }
