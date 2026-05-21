from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.post import PostCreate, PostUpdate, PostDetailResponse
from app.service.post import PostService
from app.service.media import UploadcareService

router = APIRouter(prefix="/posts", tags=["Posts"])


# ========================
# DB
# ========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ========================
# CURRENT USER
# ========================
def get_current_user_obj(
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


# ========================
# CREATE POST
# ========================
@router.post("/", response_model=PostDetailResponse)
async def create_post(
    content: str = Form(...),
    file: UploadFile = File(None),
    current_user: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db)
):
    media_url = None

    if file:
        upload_result = await UploadcareService.upload_file(file, current_user.id)
        media_url = upload_result["url"]

    post_data = PostCreate(content=content, media_url=media_url)

    post = PostService.create_post(db, current_user.id, post_data)

    return {
        **post.__dict__,
        "author": post.author,
        "like_count": PostService.get_like_count(db, post.id),
        "comment_count": PostService.get_comment_count(db, post.id)
    }


# ========================
# GET ALL POSTS (FEED)
# ========================
@router.get("/", response_model=list[PostDetailResponse])
def get_feed(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db)
):
    posts = PostService.get_all_posts(db, skip, limit)

    return [
        {
            **post.__dict__,
            "author": post.author,
            "like_count": PostService.get_like_count(db, post.id),
            "comment_count": PostService.get_comment_count(db, post.id)
        }
        for post in posts
    ]


# ========================
# GET ONE POST
# ========================
@router.get("/{post_id}", response_model=PostDetailResponse)
def get_post(
    post_id: int,
    current_user: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db)
):
    post = PostService.get_post(db, post_id)

    return {
        **post.__dict__,
        "author": post.author,
        "like_count": PostService.get_like_count(db, post.id),
        "comment_count": PostService.get_comment_count(db, post.id)
    }


# ========================
# UPDATE POST
# ========================
@router.put("/{post_id}", response_model=PostDetailResponse)
def update_post(
    post_id: int,
    data: PostUpdate,
    current_user: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db)
):
    post = PostService.update_post(db, post_id, current_user.id, data)

    return {
        **post.__dict__,
        "author": post.author,
        "like_count": PostService.get_like_count(db, post.id),
        "comment_count": PostService.get_comment_count(db, post.id)
    }


# ========================
# DELETE POST
# ========================
@router.delete("/{post_id}")
def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db)
):
    PostService.delete_post(db, post_id, current_user.id)
    return {"message": "Post deleted successfully"}
