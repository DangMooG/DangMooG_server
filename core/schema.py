from pydantic import BaseModel


class RequestPage(BaseModel):
    page: int
    size: int

    class Config:
        orm_mode = True
