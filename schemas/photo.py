from datetime import datetime
from typing import Optional

from pydantic import BaseModel, HttpUrl



"""
Photo 테이블 schema
"""


class PhotoUpload(BaseModel):
    title: str
    url: HttpUrl
    post_id: str
    category_id: int
    status: int
    user_id: int

    class Config:
        orm_mode = True


class ReadPhoto(PhotoUpload):
    photo_id: int
    create_time: datetime
    update_time: datetime



class PatchPhoto(BaseModel):
    title: Optional[str]
    url: Optional[HttpUrl]
    post_id: Optional[str]
    category_id: Optional[int]
    status: Optional[int]
    user_id: Optional[int]

    class Config:
        orm_mode = True
