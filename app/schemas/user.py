from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class UserProfileResponse(BaseModel):
    id: int
    username: str
    email: str
    bio: Optional[str]
    profile_pic_url: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    username: Optional[str] = None
    bio: Optional[str] = None
    profile_pic_url: Optional[str] = None
