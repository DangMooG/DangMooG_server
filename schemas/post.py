from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


"""
Post 테이블 schema
"""


class BasePost(BaseModel):
    title: str = Field(..., example="짱구 띠부띠부 스티커 한정판")
    price: int = Field(..., example=10000)
    description: str = Field(..., example="정말 어렵게 획득한 짱구 스티커 입니다...\n대학 기숙사 A동에서 직거래 가능해요! 네고 사절입니다.")
    category_id: int = Field(..., example=3)
    status: int = Field(..., example=0)

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


class Item(BaseModel):
    price: int
    post_id: int
    description: str
    category_id: int
    liked: int
    update_time: datetime
    title: str
    representative_photo_id: Optional[int]
    status: int
    username: str
    create_time: datetime

    class Config:
        orm_mode = True


class ResponseModel(BaseModel):
    items: List[Item]
    total_pages: int
    page: int
    size: int
    total_row: int


class AppResponseModel(BaseModel):
    items: List[Item]
    next_checkpoint: int

