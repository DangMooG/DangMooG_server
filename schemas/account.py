from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class AccountCreate(BaseModel):
    email: EmailStr
    password: Optional[str]

    class Config:
        orm_mode = True


class ReadAccount(AccountCreate):
    account_id: int
    create_time: datetime
    update_time: datetime


class PatchAccount(BaseModel):
    username: Optional[str]
    available: Optional[bool]
    jail_until: Optional[datetime]

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str
    account_id: int


class RefreshToKen(BaseModel):
    refresh_token: Optional[str]

