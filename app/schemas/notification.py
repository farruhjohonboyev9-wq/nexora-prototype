from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class NotificationResponse(BaseModel):
    id: int
    notification_type: str  # like, comment, follow
    actor_id: int
    post_id: Optional[int]
    comment_id: Optional[int]
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class NotificationDetailResponse(NotificationResponse):
    actor: "UserBasic"


class UserBasic(BaseModel):
    id: int
    username: str
    profile_pic_url: Optional[str]
    
    class Config:
        from_attributes = True


class MarkNotificationResponse(BaseModel):
    id: int
    is_read: bool


class UnreadCountResponse(BaseModel):
    unread_count: int
