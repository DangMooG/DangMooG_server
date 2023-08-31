from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from starlette import status
from starlette.responses import Response
from starlette.status import HTTP_204_NO_CONTENT
from passlib.context import CryptContext

from core.schema import RequestPage
from core.utils import get_crud
from models.account import Account
from schemas import account

from typing import List

from datetime import timedelta, datetime


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter(
    prefix="/account",
    tags=["Account"],
)
"""
Account table CRUD
"""


@router.post(
    "/account_create", name="Account record 생성", description="Account 테이블에 새로운 유저를 생성합니다", response_model=account.AccountCreate
)
async def create_account(req: account.AccountCreate, crud=Depends(get_crud)):
    db_account = req.model_copy()
    db_account.password = pwd_context.hash(req.password)
    print(db_account.password)
    return crud.create_record(Account, db_account)

@router.post(
    "/page-list",
    name="Account 리스트 조회",
    description="Account 테이블의 페이지별 Record list 가져오는 API입니다.\
                Page는 0이 아닌 양수로 입력해야합니다\
                Size는 100개로 제한됩니다.",
)
async def page_account(req: RequestPage, crud=Depends(get_crud)):
    if req.page <= 0:
        raise HTTPException(status_code=400, detail="Page number should be positive")
    if req.size > 100:
        raise HTTPException(status_code=400, detail="Size should be below 100")
    if req.size <= 0:
        raise HTTPException(status_code=400, detail="Size should be positive")
    return crud.paging_record(Account, req)


@router.post(
    "/search",
    name="Account 테이블에서 입력한 조건들에 부합하는 record 를 반환하는 API",
    description="body에 원하는 조건들을 입력하면 and로 필터 결과 리스트를 반환합니다\
        조건값이 str 일 경우 그 문자열을 포함하는 모든 record를 반환합니다.\
        조건값이 int,float 일 경우 그 값과 동일한 record만 반환합니다.\
        조건값이 list 경우 list 항목을 포함하는 모든 record를 반환합니다.\
    ",
    response_model=List[account.ReadAccount],
)
async def search_account(filters: account.AccountCreate, crud=Depends(get_crud)):
    return crud.search_record(Account, filters)


@router.get(
    "/list",
    name="Account 리스트 조회",
    description="Account 테이블의 모든 Record를 가져옵니다",
    response_model=List[account.ReadAccount],
)
def get_list(crud=Depends(get_crud)):
    return crud.get_list(Account)


@router.get(
    "/{id}",
    name="Account record 가져오기",
    description="입력된 id를 키로 해당하는 Record 반환합니다",
    response_model=account.ReadAccount,
)
def read_account(id: int, crud=Depends(get_crud)):
    filter = {"account_id": id}
    db_record = crud.get_record(Account, filter)
    if db_record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return db_record


@router.put(
    "/{id}",
    name="Account의 한 record 전체 내용 수정",
    description="수정하고자 하는 id의 record 전체 수정, record 수정 데이터가 존재하지 않을시엔 생성",
    response_model=account.ReadAccount,
)
async def update_post(req: account.AccountCreate, id: int, crud=Depends(get_crud)):
    filter = {"account_id": id}
    db_record = crud.get_record(Account, filter)
    if db_record is None:
        return crud.create_record(Account, req)

    return crud.update_record(db_record, req)


@router.patch(
    "/{id}",
    name="Account의 한 record 일부 내용 수정",
    description="수정하고자 하는 id의 record 일부 수정, record가 존재하지 않을시엔 404 오류 메시지반환합니다",
    response_model=account.ReadAccount,
)
async def update_post_sub(req: account.PatchAccount, id: int, crud=Depends(get_crud)):
    filter = {"account_id": id}
    db_record = crud.get_record(Account, filter)
    if db_record is None:
        raise HTTPException(status_code=404, detail="Record not found")

    return crud.patch_record(db_record, req)


@router.delete(
    "/{id}",
    name="Account record 삭제",
    description="입력된 id에 해당하는 record를 삭제합니다.",
)
async def delete_account(id: int, crud=Depends(get_crud)):
    filter = {"account_id": id}
    db_api = crud.delete_record(Account, filter)
    if db_api != 1:
        raise HTTPException(status_code=404, detail="Record not found")
    return Response(status_code=HTTP_204_NO_CONTENT)


ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
SECRET_KEY = "805b4d64afe69895a39822c07f92fc709ae8e250d1ef49c0b1dc3bbfa072090e"
ALGORITHM = "HS256"


@router.post("/login", response_model=account.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                           crud=Depends(get_crud)):

    # check user and password
    filter = {"username": form_data.username}
    user = crud.get_record(Account, filter)
    if not user or not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # make access token
    data = {
        "sub": user.username,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username
    }