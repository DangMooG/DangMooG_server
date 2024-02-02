from datetime import datetime
from typing import Optional

from pydantic import BaseModel


"""
Photo 테이블 schema
"""


class PhotoUpload(BaseModel):
    post_id: int
    category_id: int

    class Config:
        orm_mode = True


class PhotoComplete(PhotoUpload):
    url: str
    account_id: int


class ReadPhoto(BaseModel):
    url: str
    create_time: datetime

    class Config:
        orm_mode = True


class SearchPhoto(BaseModel):
    photo_id: Optional[int]
    url: Optional[str]
    post_id: Optional[int]
    category_id: Optional[int]
    account_id: Optional[int]


class MPhotoStart(BaseModel):
    room_id: str

    class Config:
        orm_mode = True


class MPhotoUpload(BaseModel):
    room_id: str
    url: str
    message_id: int
    account_id: int

    class Config:
        orm_mode = True


class MPhotoRead(MPhotoUpload):
    m_photo_id: int
    create_time: datetime

    class Config:
        orm_mode = True
