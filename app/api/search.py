from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.search import SearchResultResponse, SearchUserResponse, SearchPostDetailResponse
from app.service.search import SearchService

router = APIRouter(prefix="/search", tags=["search"])


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


@router.get("", response_model=SearchResultResponse)
def search(
    q: str,
    user_limit: int = 10,
    post_limit: int = 20,
    hashtag_limit: int = 10,
    current_user: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db)
):
    """Search users, posts, and hashtags"""
    if not q or len(q) < 2:
        raise HTTPException(status_code=400, detail="Query must be at least 2 characters")
    
    users = SearchService.search_users(db, q, user_limit)
    posts = SearchService.search_posts(db, q, post_limit)
    hashtags = SearchService.search_hashtags(db, q, hashtag_limit)
    
    return {
        "users": users,
        "posts": [
            {
                **p.__dict__,
                "author": p.author
            }
            for p in posts
        ],
        "hashtags": [h.name for h in hashtags]
    }


@router.get("/users", response_model=list[SearchUserResponse])
def search_users(
    q: str,
    limit: int = 10,
    current_user: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db)
):
    """Search users"""
    users = SearchService.search_users(db, q, limit)
    return users


@router.get("/posts", response_model=list[SearchPostDetailResponse])
def search_posts(
    q: str,
    limit: int = 20,
    current_user: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db)
):
    """Search posts"""
    posts = SearchService.search_posts(db, q, limit)
    return [
        {
            **p.__dict__,
            "author": p.author
        }
        for p in posts
    ]


@router.get("/hashtags")
def search_hashtags(
    q: str,
    limit: int = 10,
    current_user: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db)
):
    """Search hashtags"""
    hashtags = SearchService.search_hashtags(db, q, limit)
    return [{"name": h.name, "id": h.id} for h in hashtags]
