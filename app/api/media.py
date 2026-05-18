from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.service.media import UploadcareService
from app.schemas.media import MediaUploadResponse, MediaDeleteResponse

router = APIRouter(prefix="/media", tags=["media"])


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


@router.post("/upload", response_model=MediaUploadResponse)
async def upload_media(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user_obj)
):
    """
    Upload media to Uploadcare.
    
    Supports: JPEG, PNG, WebP, GIF images and MP4, MOV, AVI videos
    Max image size: 50MB
    Max video size: 500MB
    
    Returns:
    - uuid: Uploadcare file UUID
    - url: CDN URL for accessing the file
    - media_type: 'image' or 'video'
    - file_size: Size of uploaded file in bytes
    - filename: Original filename
    """
    result = await UploadcareService.upload_file(file, current_user.id)
    return MediaUploadResponse(**result)


@router.delete("/delete/{file_uuid}", response_model=MediaDeleteResponse)
async def delete_media(
    file_uuid: str,
    current_user: User = Depends(get_current_user_obj)
):
    """
    Delete media file from Uploadcare.
    
    Requires authentication. User can only delete files they uploaded.
    """
    UploadcareService.delete_file(file_uuid)
    return {
        "message": "File deleted successfully",
        "uuid": file_uuid
    }


@router.get("/{file_uuid}")
async def get_media_url(
    file_uuid: str,
    width: int = None,
    height: int = None,
    current_user: User = Depends(get_current_user_obj)
):
    """
    Get optimized CDN URL for a media file.
    
    Optional parameters:
    - width: Resize image to this width (pixels)
    - height: Resize image to this height (pixels)
    
    Returns CDN URL with optional transformations applied.
    """
    cdn_url = UploadcareService.get_cdn_url(file_uuid, width, height)
    return {
        "url": cdn_url,
        "uuid": file_uuid,
        "width": width,
        "height": height
    }