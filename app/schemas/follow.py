from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class FollowResponse(BaseModel):
    id: int
    follower_id: int
    following_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class FollowerResponse(BaseModel):
    id: int
    username: str
    profile_pic_url: Optional[str]
    
    class Config:
        from_attributes = True


class FollowingResponse(BaseModel):
    id: int
    username: str
    profile_pic_url: Optional[str]
    
    class Config:
        from_attributes = True


class FollowStatusResponse(BaseModel):
    is_following: bool
    followers_count: int
    following_count: int
