from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr
    available: bool
    release: datetime

    class Config:
        orm_mode = True


class ReadUser(UserCreate):
    user_id: int
    create_time: datetime
    update_time: datetime


class PatchUser(BaseModel):
    username: Optional[str]
    password: Optional[str]
    email: Optional[EmailStr]
    available: Optional[bool]
    release: Optional[datetime]

    class Config:
        orm_mode = True