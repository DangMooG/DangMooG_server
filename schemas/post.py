from datetime import datetime
from typing import Optional

from pydantic import BaseModel


"""
Post 테이블 schema
"""


class BasePost(BaseModel):
    title: str
    price: int
    description: str
    category_id: int
    status: int

    class Config:
        orm_mode = True


class PhotoPost(BasePost):
    account_id: int
    username: str
    representative_photo_id: int


class UploadPost(BasePost):
    account_id: int
    username: str


class ReadPost(PhotoPost):
    post_id: int
    representative_photo_id: Optional[int]
    username: str
    liked: int
    create_time: datetime
    update_time: datetime


class PatchPost(BaseModel):
    title: Optional[str]
    price: Optional[int]
    description: Optional[str]
    category_id: Optional[int]
    status: Optional[int]
    account_id: int
    representative_photo_id: Optional[int]
    liked: Optional[int]

    class Config:
        orm_mode = True


class LikedPatch(BaseModel):
    post_id: int
    account_id: int

    class Config:
        orm_mode = True


class ReadLiked(LikedPatch):
    liked_id: int
    create_time: datetime
