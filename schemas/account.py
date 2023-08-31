from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class AccountCreate(BaseModel):
    username: str
    password: str
    email: EmailStr
    available: int
    jail_until: datetime

    class Config:
        orm_mode = True


class ReadAccount(AccountCreate):
    account_id: int
    create_time: datetime
    update_time: datetime


class PatchAccount(BaseModel):
    username: Optional[str]
    password: Optional[str]
    email: Optional[EmailStr]
    available: Optional[bool]
    jail_until: Optional[datetime]

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str
    username: str