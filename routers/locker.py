from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import Response
from starlette.status import HTTP_204_NO_CONTENT, HTTP_401_UNAUTHORIZED

from core.utils import get_crud
from models.locker import Locker
from schemas import locker
from routers.account import get_current_user
from models.account import Account
from models.post import Post

from typing import List

router = APIRouter(
    prefix="/locker",
    tags=["Locker"],
)
"""
Chat table CRUD
"""


@router.post(
    "/search",
    name="locker 테이블에서 입력한 조건들에 부합하는 record 를 반환하는 API",
    description="body에 원하는 조건들을 입력하면 and로 필터 결과 리스트를 반환합니다\n"
                "조건값이 str 일 경우 그 문자열을 포함하는 모든 record를 반환합니다.\n"
                "조건값이 int,float 일 경우 그 값과 동일한 record만 반환합니다.\n"
                "조건값이 list 경우 list 항목을 포함하는 모든 record를 반환합니다.\n"
                "dict형으로 locker_id(int), name(str), status(int), post_id(int), account_id(int)를 field로 받을 수 있습니다.",
    response_model=List[locker.ReadLocker],
)
async def search_post(filters: dict, crud=Depends(get_crud)):
    return crud.search_record(Locker, filters)


@router.get(
    "/list",
    name="locker 모든 리스트 조회",
    description="Post 테이블의 모든 Record를 가져옵니다",
    response_model=List[locker.ReadLocker],
)
def get_list(crud=Depends(get_crud)):
    for one_locker in crud.get_list(Locker):
        if one_locker.post_id is not None:
            if one_locker.post_id is None and one_locker.account_id is None and datetime.now() > one_locker.update_time + timedelta(minutes=5):
                crud.patch_record(one_locker, {"status": 1, "account_id": None})
            elif one_locker.post_id is None and datetime.now() > one_locker.update_time + timedelta(minutes=30):
                crud.patch_record(one_locker, {"status": 1, "account_id": None})
            corresponded_post = crud.get_record(Post, {"post_id": one_locker.post_id})
            if corresponded_post.status == 2:
                crud.patch_record(one_locker, {"status": 1, "post_id": None, "account_id": None})
    return crud.get_list(Locker)



@router.get(
    "/{id}",
    name="Locker record 가져오기",
    description="입력된 id를 키로 해당하는 Record 반환합니다",
    response_model=locker.ReadLocker,
)
def read_post(id: int, crud=Depends(get_crud)):
    filter = {"locker_id": id}
    db_record = crud.get_record(Locker, filter)
    if db_record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return db_record

@router.patch(
    "/{id}",
    name="Locker 하나의 record 내용 수정(예약, 사용완료 등 상태 변경 시 사용)",
    description="수정하고자 하는 id의 record 일부 수정, record가 존재하지 않을시엔 404 오류 메시지반환합니다\n\n"
                "처음 선택할 때 - {\"account_id\": {user_account_id}}\n\n"
                "최종 선택할 때 - {\"post_id\": {post_id_of_seller}} ",
    response_model=locker.ReadLocker,
)
async def update_post_sub(req: dict, id: int, crud=Depends(get_crud), current_user: Account = Depends(get_current_user)):
    filter = {"locker_id": id}
    db_record = crud.get_record(Locker, filter)
    if db_record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    if db_record.status == 0 and db_record.account_id != current_user.account_id:
        raise HTTPException(status_code=401, detail="Unauthorized request")
    return crud.patch_record(db_record, {**req, "account_id": current_user.account_id})
