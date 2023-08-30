from datetime import datetime
from typing import Optional

from pydantic import BaseModel



"""
Chat 테이블 schema
"""


class RecordChat(BaseModel):
    post_id: int
    room_id: int
    is_seller: int
    account_id: int
    chat_str: str

    class Config:
        orm_mode = True


class ReadChat(RecordChat):
    chat_id: int
    create_time: datetime
    update_time: datetime


class PatchChat(BaseModel):
    post_id: Optional[int]
    room_id: Optional[int]
    is_seller: Optional[int]
    account_id: Optional[int]
    chat_str: Optional[str]
    status: Optional[int]

    class Config:
        orm_mode = True
