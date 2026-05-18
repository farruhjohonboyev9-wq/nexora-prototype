from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PostCreate(BaseModel):
    content: str
    media_url: Optional[str] = None


class PostUpdate(BaseModel):
    content: Optional[str] = None
    media_url: Optional[str] = None


class PostResponse(BaseModel):
    id: int
    author_id: int
    content: str
    media_url: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PostDetailResponse(PostResponse):
    author: "UserBasic"
    like_count: int
    comment_count: int


class UserBasic(BaseModel):
    id: int
    username: str
    profile_pic_url: Optional[str]
    
    class Config:
        from_attributes = True
