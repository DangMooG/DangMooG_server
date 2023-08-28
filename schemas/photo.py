from datetime import datetime
from typing import Optional

from pydantic import BaseModel, HttpUrl



"""
Photo 테이블 schema
"""


class PhotoUpload(BaseModel):
    title: str
    description: Optional[str]
    url: Optional[int]
    description: str
    category_id: int
    status: int
    user_id: int
    view_count: Optional[int]
    comment_id: Optional[int]

    class Config:
        orm_mode = True


class ReadPost(BasePost):
    post_id: int
    create_time: datetime
    update_time: datetime



class PatchPost(BaseModel):
    title: Optional[str]
    price: Optional[int]
    photo_id: Optional[int]
    description: Optional[str]
    category_id: Optional[int]
    status: Optional[int]
    user_id: Optional[int]
    view_count: Optional[int]
    comment_id: Optional[int]

    class Config:
        orm_mode = True
