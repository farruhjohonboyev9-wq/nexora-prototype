"""
Uploadcare media service for handling image and video uploads.
Direct upload to Uploadcare CDN with secure URL generation.
"""

import requests
import hashlib
import hmac
import time
from typing import Optional
from fastapi import HTTPException, UploadFile
from app.core.config import settings


class UploadcareService:
    """
    Service for managing media uploads to Uploadcare.
    Handles image and video uploads with validation and CDN URL generation.
    """
    
    # File type constraints
    ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
    ALLOWED_VIDEO_TYPES = {"video/mp4", "video/quicktime", "video/x-msvideo", "video/mpeg"}
    
    @staticmethod
    def validate_credentials() -> bool:
        """Validate Uploadcare API credentials"""
        if not settings.UPLOADCARE_PUBLIC_KEY or not settings.UPLOADCARE_PRIVATE_KEY:
            raise HTTPException(
                status_code=500,
                detail="Uploadcare credentials not configured"
            )
        return True
    
    @staticmethod
    def validate_file(file: UploadFile) -> bool:
        """Validate file type and size"""
        allowed_types = UploadcareService.ALLOWED_IMAGE_TYPES | UploadcareService.ALLOWED_VIDEO_TYPES
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file.content_type}. Allowed: images and videos"
            )
        
        return True
    
    @staticmethod
    def is_video(content_type: str) -> bool:
        """Check if file is video"""
        return content_type in UploadcareService.ALLOWED_VIDEO_TYPES
    
    @staticmethod
    def is_image(content_type: str) -> bool:
        """Check if file is image"""
        return content_type in UploadcareService.ALLOWED_IMAGE_TYPES
    
    @staticmethod
    async def upload_file(file: UploadFile, user_id: int) -> dict:
        """
        Upload file directly to Uploadcare.
        Returns CDN URL and metadata.
        """
        UploadcareService.validate_credentials()
        UploadcareService.validate_file(file)
        
        try:
            file_content = await file.read()
            file_size = len(file_content)
            
            # Validate file size based on type
            if UploadcareService.is_video(file.content_type):
                max_size = settings.MAX_VIDEO_SIZE
                media_type = "video"
            else:
                max_size = settings.MAX_FILE_SIZE
                media_type = "image"
            
            if file_size > max_size:
                raise HTTPException(
                    status_code=400,
                    detail=f"File size exceeds {max_size / 1024 / 1024:.0f}MB limit"
                )
            
            # Upload to Uploadcare
            upload_url = f"{settings.UPLOADCARE_API_BASE_URL}/upload/"
            
            files_data = {
                "file": (file.filename, file_content, file.content_type),
                "UPLOADCARE_PUB_KEY": settings.UPLOADCARE_PUBLIC_KEY,
            }
            
            response = requests.post(upload_url, files=files_data)
            
            if response.status_code not in [200, 201]:
                raise HTTPException(
                    status_code=500,
                    detail=f"Uploadcare upload failed: {response.text}"
                )
            
            data = response.json()
            file_uuid = data.get("file") or data.get("uuid")
            
            if not file_uuid:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to retrieve file UUID from Uploadcare"
                )
            
            # Build CDN URL
            cdn_url = f"https://ucarecdn.com/{file_uuid}/"
            
            return {
                "uuid": file_uuid,
                "url": cdn_url,
                "media_type": media_type,
                "file_size": file_size,
                "filename": file.filename
            }
            
        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=500,
                detail=f"Upload service error: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error during upload: {str(e)}"
            )
    
    @staticmethod
    def delete_file(file_uuid: str) -> bool:
        """
        Delete file from Uploadcare.
        Requires private key authentication.
        """
        UploadcareService.validate_credentials()
        
        try:
            delete_url = f"{settings.UPLOADCARE_API_BASE_URL}/files/{file_uuid}/"
            
            # Build auth header
            timestamp = str(int(time.time()))
            sign_string = f"{file_uuid}{timestamp}{settings.UPLOADCARE_PRIVATE_KEY}"
            signature = hashlib.md5(sign_string.encode()).hexdigest()
            
            headers = {
                "Authorization": f"Uploadcare.Simple {settings.UPLOADCARE_PUBLIC_KEY}:{signature}",
                "Date": timestamp
            }
            
            response = requests.delete(delete_url, headers=headers)
            
            if response.status_code not in [200, 204]:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to delete file from Uploadcare"
                )
            
            return True
            
        except requests.exceptions.RequestException:
            raise HTTPException(
                status_code=500,
                detail="Delete service error"
            )
    
    @staticmethod
    def get_cdn_url(file_uuid: str, width: Optional[int] = None, height: Optional[int] = None) -> str:
        """
        Generate optimized CDN URL with optional transformations.
        Supports resizing, format conversion, etc.
        """
        cdn_url = f"https://ucarecdn.com/{file_uuid}/"
        
        params = []
        if width:
            params.append(f"w/{width}")
        if height:
            params.append(f"h/{height}")
        
        if params:
            cdn_url += "-/".join(params) + "/"
        
        return cdn_url
