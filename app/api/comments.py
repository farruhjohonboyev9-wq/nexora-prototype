from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentDetailResponse
from app.service.comment import CommentService

router = APIRouter(prefix="/comments", tags=["comments"])


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


@router.post("/posts/{post_id}", response_model=CommentDetailResponse)
def add_comment(
    post_id: int,
    data: CommentCreate,
    current_user: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db)
):
    """Add comment to a post"""
    comment = CommentService.create_comment(db, post_id, current_user.id, data)
    return {
        **comment.__dict__,
        "author": comment.author
    }


@router.get("/posts/{post_id}", response_model=list[CommentDetailResponse])
def get_post_comments(
    post_id: int,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db)
):
    """Get all comments for a post"""
    comments = CommentService.get_comments_by_post(db, post_id, skip, limit)
    return [
        {
            **comment.__dict__,
            "author": comment.author
        }
        for comment in comments
    ]


@router.delete("/{comment_id}")
def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db)
):
    """Delete comment (owner only)"""
    CommentService.delete_comment(db, comment_id, current_user.id)
    return {"message": "Comment deleted successfully"}
