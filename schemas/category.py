from datetime import datetime
from typing import Optional

from pydantic import BaseModel



"""
Category 테이블 schema
"""


class Category(BaseModel):
    id: int
    name: str


