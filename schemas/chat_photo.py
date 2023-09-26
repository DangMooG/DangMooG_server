from datetime import datetime
from pydantic import BaseModel


"""
Photo 테이블 schema
"""


class ChatPhotoRequest(BaseModel):
    chat_id: int

    class Config:
        orm_mode = True


class ChatPhotoUpload(ChatPhotoRequest):
    url: str

    class Config:
        orm_mode = True


class ReadPhoto(ChatPhotoUpload):
    chatphoto_id: int
    create_time: datetime
