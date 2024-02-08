from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UseLocker(BaseModel):
    locker_id: int
    status: Optional[int]
    post_id: Optional[int]
    account_id: Optional[int]

    class Config:
        orm_mode = True


class ReadLocker(UseLocker):
    name: str
    create_time: datetime
    update_time: datetime

    class Config:
        orm_mode = True


class LockerAuth(BaseModel):
    post_id: int
    locker_id: int
    password: str

    class Config:
        orm_mode = True


class AuthUpload(LockerAuth):
    photo_url: str

    class Config:
        orm_mode = True


class AuthRead(LockerAuth):
    locker_auth_id: int
    photo_url: str
    is_over: int
    create_time: datetime
    update_time: datetime

    class Config:
        orm_mode = True


class LockerPass(BaseModel):
    locker_id: int
    name: str
    photo_url: str
    password: str

    class Config:
        orm_mode = True
