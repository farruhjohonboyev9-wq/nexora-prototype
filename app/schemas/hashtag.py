from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class HashtagResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class HashtagWithCountResponse(BaseModel):
    id: int
    name: str
    post_count: int
    
    class Config:
        from_attributes = True


class TrendingHashtagResponse(BaseModel):
    name: str
    post_count: int
    rank: int
