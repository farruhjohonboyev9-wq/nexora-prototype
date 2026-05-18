from pydantic import BaseModel
from typing import Optional


class MediaUploadResponse(BaseModel):
    uuid: str
    url: str
    media_type: str  # image or video
    file_size: int
    filename: str


class MediaDeleteResponse(BaseModel):
    message: str
    uuid: str


class CDNUrlResponse(BaseModel):
    url: str
    uuid: str
