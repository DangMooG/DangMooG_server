from datetime import datetime
from typing import Optional, List

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
    create_time: datetime

    class Config:
        orm_mode = True


class Readroom(BaseModel):
    post_id: List[int]
    iam_buyer: List[bool]

    class Config:
        orm_mode = True


class PatchChat(BaseModel):
    chat_str: Optional[str]

    class Config:
        orm_mode = True


class OppoRoom(BaseModel):
    rooms: List[str]

    class Config:
        orm_mode = True


class OppoName(BaseModel):
    usernames: List[str]
    profiles: List[str]

    class Config:
        orm_mode = True


class RoomStatus(BaseModel):
    last_messages: List[str]
    update_times: List[datetime]
    counts: List[int]

    class Config:
        orm_mode = True


class RoomIDs(BaseModel):
    room_ids: List[str]

    class Config:
        orm_mode = True
