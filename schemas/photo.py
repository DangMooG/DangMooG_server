from datetime import datetime
from typing import Optional

from pydantic import BaseModel


"""
Photo 테이블 schema
"""


class PhotoUpload(BaseModel):
    url: Optional[str]
    post_id: int
    category_id: int
    status: int
    account_id: int

    class Config:
        orm_mode = True


class ReadPhoto(PhotoUpload):
    photo_id: int
    create_time: datetime
    update_time: datetime



class PatchPhoto(BaseModel):
    url: Optional[str]
    post_id: Optional[str]
    category_id: Optional[int]
    status: Optional[int]
    account_id: Optional[int]

    class Config:
        orm_mode = True
