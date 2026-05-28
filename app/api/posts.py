from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, Query
from sqlalchemy.orm import Session
import traceback

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
# CURRENT USER (REQUIRED)
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
    try:
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
    except Exception as e:
        print(f"❌ Create post error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error creating post: {str(e)}")


# ========================
# GET ALL POSTS (PUBLIC FEED)
# ========================
@router.get("/", response_model=list[PostDetailResponse])
def get_feed(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all posts - PUBLIC endpoint, no auth required"""
    try:
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
    except Exception as e:
        print(f"❌ Get feed error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error fetching posts: {str(e)}")


# ========================
# GET ONE POST
# ========================
@router.get("/{post_id}", response_model=PostDetailResponse)
def get_post(
    post_id: int,
    db: Session = Depends(get_db)
):
    """Get single post - PUBLIC endpoint, no auth required"""
    try:
        post = PostService.get_post(db, post_id)

        return {
            **post.__dict__,
            "author": post.author,
            "like_count": PostService.get_like_count(db, post.id),
            "comment_count": PostService.get_comment_count(db, post.id)
        }
    except Exception as e:
        print(f"❌ Get post error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error fetching post: {str(e)}")


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
    try:
        post = PostService.update_post(db, post_id, current_user.id, data)

        return {
            **post.__dict__,
            "author": post.author,
            "like_count": PostService.get_like_count(db, post.id),
            "comment_count": PostService.get_comment_count(db, post.id)
        }
    except Exception as e:
        print(f"❌ Update post error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error updating post: {str(e)}")


# ========================
# DELETE POST
# ========================
@router.delete("/{post_id}")
def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db)
):
    try:
        PostService.delete_post(db, post_id, current_user.id)
        return {"message": "Post deleted successfully"}
    except Exception as e:
        print(f"❌ Delete post error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error deleting post: {str(e)}")
