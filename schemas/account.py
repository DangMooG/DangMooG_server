from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AccountCreate(BaseModel):
    email: str = Field(..., example="my_gist_id@gist.ac.kr")

    class Config:
        orm_mode = True


class AccountSet(AccountCreate):
    password: str

    class Config:
        orm_mode = True


class AccountReceate(BaseModel):
    password: str

    class Config:
        orm_mode = True


class ReadAccount(BaseModel):
    account_id: int
    username: Optional[str]
    email: str
    profile_url: Optional[str]
    available: Optional[int]
    jail_until: Optional[datetime]
    create_time: datetime
    update_time: datetime


class PatchAccount(BaseModel):
    available: Optional[bool]
    jail_until: Optional[datetime]

    class Config:
        orm_mode = True


class NicnameSet(BaseModel):
    username: Optional[str] = Field(..., example="trial_your_nickname")

    class Config:
        orm_mode = True

class PhotoAccount(BaseModel):
    profile_url: str


class Token(BaseModel):
    access_token: str
    token_type: str
    account_id: int
    is_username: int


class RefreshToKen(BaseModel):
    refresh_token: Optional[str]

