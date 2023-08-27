from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import Response
from starlette.status import HTTP_204_NO_CONTENT
from passlib.context import CryptContext

from core.schema import RequestPage
from core.utils import get_crud
from models.user import User
from schemas import user

from typing import List

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter(
    prefix="/user",
    tags=["User"],
)
"""
User table CRUD
"""


@router.post(
    "/user_create", name="Post record 생성", description="User 테이블에 새로운 유저를 생성합니다", response_model=user.UserCreate
)
async def create_post(req: user.UserCreate, crud=Depends(get_crud)):
    db_user = req.copy()
    db_user.password = pwd_context.hash(req.password)
    return crud.create_record(User, db_user)