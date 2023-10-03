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
