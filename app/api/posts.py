from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.post import PostCreate, PostUpdate, PostDetailResponse
from app.service.post import PostService
from app.service.like import LikeService
from app.service.comment import CommentService
from app.service.media import UploadcareService

router = APIRouter(prefix="/posts", tags=["posts"])


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


@router.post("", response_model=PostDetailResponse)
async def create_post(
    content: str = Form(...),
    file: UploadFile = File(None),
    current_user: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db)
):
    """
    Create a new post with optional media attachment.
    
    Supports multipart form data:
    - content (required): Post text content
    - file (optional): Image or video file
    
    Supported media types:
    - Images: JPEG, PNG, WebP, GIF (max 50MB)
    - Videos: MP4, MOV, AVI (max 500MB)
    """
    media_url = None
    
    # Upload media if file provided
    if file:
        upload_result = await UploadcareService.upload_file(file, current_user.id)
        media_url = upload_result["url"]
    
    # Create post with media URL
    post_data = PostCreate(content=content, media_url=media_url)
    post = PostService.create_post(db, current_user.id, post_data)
    like_count = PostService.get_like_count(db, post.id)
    comment_count = PostService.get_comment_count(db, post.id)
    
    return {
        **post.__dict__,
        "author": current_user,
        "like_count": like_count,
        "comment_count": comment_count
    }


@router.get("/{post_id}", response_model=PostDetailResponse)
def get_post(
    post_id: int,
    current_user: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db)
):
    """Get a single post by ID"""
    post = PostService.get_post(db, post_id)
    like_count = PostService.get_like_count(db, post.id)
    comment_count = PostService.get_comment_count(db, post.id)
    
    return {
        **post.__dict__,
        "author": post.author,
        "like_count": like_count,
        "comment_count": comment_count
    }


@router.get("", response_model=list[PostDetailResponse])
def get_feed(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db)
):
    """Get feed with all posts"""
    posts = PostService.get_all_posts(db, skip, limit)
    
    result = []
    for post in posts:
        like_count = PostService.get_like_count(db, post.id)
        comment_count = PostService.get_comment_count(db, post.id)
        result.append({
            **post.__dict__,
            "author": post.author,
            "like_count": like_count,
            "comment_count": comment_count
        })
    
    return result


@router.put("/{post_id}", response_model=PostDetailResponse)
def update_post(
    post_id: int,
    data: PostUpdate,
    current_user: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db)
):
    """Update post (owner only)"""
    post = PostService.update_post(db, post_id, current_user.id, data)
    like_count = PostService.get_like_count(db, post.id)
    comment_count = PostService.get_comment_count(db, post.id)
    
    return {
        **post.__dict__,
        "author": post.author,
        "like_count": like_count,
        "comment_count": comment_count
    }


@router.delete("/{post_id}")
def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db)
):
    """Delete post (owner only)"""
    PostService.delete_post(db, post_id, current_user.id)
    return {"message": "Post deleted successfully"}
