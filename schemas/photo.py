from datetime import datetime
from typing import Optional

from pydantic import BaseModel


"""
Photo 테이블 schema
"""


class PhotoUpload(BaseModel):
    post_id: int
    category_id: int
    status: int

    class Config:
        orm_mode = True


class PhotoComplete(PhotoUpload):
    url: str
    account_id: int


class ReadPhoto(PhotoComplete):
    photo_id: int
    create_time: datetime


class SearchPhoto(BaseModel):
    photo_id: Optional[int]
    url: Optional[str]
    post_id: Optional[int]
    category_id: Optional[int]
    status: Optional[int]
    account_id: Optional[int]