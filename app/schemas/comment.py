from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CommentCreate(BaseModel):
    content: str


class CommentResponse(BaseModel):
    id: int
    post_id: int
    author_id: int
    content: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CommentDetailResponse(CommentResponse):
    author: "UserBasic"


class UserBasic(BaseModel):
    id: int
    username: str
    profile_pic_url: Optional[str]
    
    class Config:
        from_attributes = True
