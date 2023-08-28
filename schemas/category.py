from datetime import datetime
from typing import Optional

from pydantic import BaseModel



"""
Category 테이블 schema
"""


class CreateCategory(BaseModel):
    name: str


class ReadCategory(CreateCategory):
    category_id: int
    create_time: datetime
    update_time: datetime


class PatchCategory(BaseModel):
    name: Optional[str]

    class Config:
        orm_mode = True
