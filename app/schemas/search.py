from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class SearchUserResponse(BaseModel):
    id: int
    username: str
    profile_pic_url: Optional[str]
    bio: Optional[str]
    
    class Config:
        from_attributes = True


class SearchPostResponse(BaseModel):
    id: int
    content: str
    author_id: int
    media_url: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class SearchPostDetailResponse(SearchPostResponse):
    author: SearchUserResponse


class SearchResultResponse(BaseModel):
    users: List[SearchUserResponse] = []
    posts: List[SearchPostDetailResponse] = []
    hashtags: List[str] = []
