from datetime import datetime
from typing import Optional

from pydantic import BaseModel


"""
Chat 테이블 schema
"""


class RoomNumber(BaseModel):
    post_id: int

    class Config:
        orm_mode = True


class RoomCreate(RoomNumber):
    buyer_id: int
    seller_id: int
    status: int

    class Config:
        orm_mode = True


class RoomID(BaseModel):
    room_id: int


class RecordChat(BaseModel):
    message_id: int
    is_from_buyer: int
    content: str
    read: int

    class Config:
        orm_mode = True


class Readroom(BaseModel):
    post_id: int

    class Config:
        orm_mode = True


class PatchChat(BaseModel):
    chat_str: Optional[str]

    class Config:
        orm_mode = True
