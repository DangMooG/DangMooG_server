from datetime import datetime
from typing import Optional

from pydantic import BaseModel


"""
Chat 테이블 schema
"""


class RecordChat(BaseModel):
    post_id: int
    room_id: Optional[int]
    receiver_id: Optional[int]
    is_photo: int
    chat_str: Optional[str]

    class Config:
        orm_mode = True


class SaveChat(RecordChat):
    sender_id: int

    class Config:
        orm_mode = True


class ReadChat(SaveChat):
    chat_id: int
    create_time: datetime
    update_time: datetime


class PatchChat(BaseModel):
    chat_str: Optional[str]

    class Config:
        orm_mode = True
