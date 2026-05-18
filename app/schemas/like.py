from pydantic import BaseModel
from datetime import datetime


class LikeResponse(BaseModel):
    id: int
    user_id: int
    post_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class LikeCountResponse(BaseModel):
    post_id: int
    like_count: int
    is_liked: bool
