from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import traceback

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
    q: str = Query(..., min_length=2),
    user_limit: int = Query(10, ge=1, le=50),
    post_limit: int = Query(20, ge=1, le=100),
    hashtag_limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Search users, posts, and hashtags - PUBLIC endpoint"""
    try:
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
    except Exception as e:
        print(f"❌ Search error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/users", response_model=list[SearchUserResponse])
def search_users(
    q: str = Query(..., min_length=2),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Search users - PUBLIC endpoint"""
    try:
        users = SearchService.search_users(db, q, limit)
        return users
    except Exception as e:
        print(f"❌ Search users error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/posts", response_model=list[SearchPostDetailResponse])
def search_posts(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search posts - PUBLIC endpoint"""
    try:
        posts = SearchService.search_posts(db, q, limit)
        return [
            {
                **p.__dict__,
                "author": p.author
            }
            for p in posts
        ]
    except Exception as e:
        print(f"❌ Search posts error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/hashtags")
def search_hashtags(
    q: str = Query(..., min_length=2),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Search hashtags - PUBLIC endpoint"""
    try:
        hashtags = SearchService.search_hashtags(db, q, limit)
        return [{"name": h.name, "id": h.id} for h in hashtags]
    except Exception as e:
        print(f"❌ Search hashtags error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
