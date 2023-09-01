from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import Response
from starlette.status import HTTP_204_NO_CONTENT

from core.schema import RequestPage
from core.utils import get_crud
from models.post import Post
from schemas import post
from routers.account import get_current_user
from models.account import Account


from typing import List

router = APIRouter(
    prefix="/post",
    tags=["Post"],
)
"""
Post table CRUD
"""


@router.post(
    "/create_post", name="Post record 생성", description="Post 테이블에 Record 생성합니다", response_model=post.ReadPost
)
async def create_post(req: post.BasePost, crud=Depends(get_crud), current_user: Account = Depends(get_current_user)):
    final = req.model_copy()
    final.account_id = current_user.account_id
    return crud.create_record(Post, final)


@router.post(
    "/page-list",
    name="Post Page 리스트 조회",
    description="Post 테이블의 페이지별 Record list 가져오는 API입니다.\
                Page는 0이 아닌 양수로 입력해야합니다\
                Size는 100개로 제한됩니다.",
)
async def page_post(req: RequestPage, crud=Depends(get_crud)):
    if req.page <= 0:
        raise HTTPException(status_code=400, detail="Page number should be positive")
    if req.size > 100:
        raise HTTPException(status_code=400, detail="Size should be below 100")
    if req.size <= 0:
        raise HTTPException(status_code=400, detail="Size should be positive")
    return crud.paging_record(Post, req)


@router.post(
    "/search",
    name="Post 테이블에서 입력한 조건들에 부합하는 record 를 반환하는 API",
    description="body에 원하는 조건들을 입력하면 and로 필터 결과 리스트를 반환합니다\
        조건값이 str 일 경우 그 문자열을 포함하는 모든 record를 반환합니다.\
        조건값이 int,float 일 경우 그 값과 동일한 record만 반환합니다.\
        조건값이 list 경우 list 항목을 포함하는 모든 record를 반환합니다.\
    ",
    response_model=List[post.ReadPost],
)
async def search_post(filters: post.PatchPost, crud=Depends(get_crud)):
    return crud.search_record(Post, filters)


@router.get(
    "/list",
    name="Post 리스트 조회",
    description="Post 테이블의 모든 Record를 가져옵니다",
    response_model=List[post.ReadPost],
)
def get_list(crud=Depends(get_crud)):
    return crud.get_list(Post)


@router.get(
    "/{id}",
    name="Post record 가져오기",
    description="입력된 id를 키로 해당하는 Record 반환합니다",
    response_model=post.ReadPost,
)
def read_post(id: int, crud=Depends(get_crud)):
    filter = {"post_id": id}
    db_record = crud.get_record(Post, filter)
    if db_record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return db_record


@router.put(
    "/{id}",
    name="Post 한 record 전체 내용 수정",
    description="수정하고자 하는 id의 record 전체 수정, record 수정 데이터가 존재하지 않을시엔 생성",
    response_model=post.ReadPost,
)
async def update_post(req: post.BasePost, id: int, crud=Depends(get_crud), current_user: Account = Depends(get_current_user)):
    final = req.model_copy()
    final.account_id = current_user.account_id
    filter = {"post_id": id}
    db_record = crud.get_record(Post, filter)
    if db_record is None:
        return crud.create_record(Post, final)

    if db_record.account_id == current_user.account_id:
        raise HTTPException(status_code=401, detail="Unauthorized request")

    return crud.update_record(db_record, final)


@router.patch(
    "/{id}",
    name="Post 한 record 일부 내용 수정",
    description="수정하고자 하는 id의 record 일부 수정, record가 존재하지 않을시엔 404 오류 메시지반환합니다",
    response_model=post.ReadPost,
)
async def update_post_sub(req: post.PatchPost, id: int, crud=Depends(get_crud), current_user: Account = Depends(get_current_user)):
    filter = {"post_id": id}
    db_record = crud.get_record(Post, filter)
    if db_record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    if db_record.account_id == current_user.account_id:
        raise HTTPException(status_code=401, detail="Unauthorized request")

    return crud.patch_record(db_record, req)


@router.delete(
    "/{id}",
    name="Post record 삭제",
    description="입력된 id에 해당하는 record를 삭제합니다.",
)
async def delete_post(id: int, crud=Depends(get_crud), current_user: Account = Depends(get_current_user)):
    filter = {"post_id": id}
    db_record = crud.get_record(Post, filter)
    if db_record.account_id == current_user.account_id:
        raise HTTPException(status_code=401, detail="Unauthorized request")
    db_api = crud.delete_record(Post, filter)
    if db_api != 1:
        raise HTTPException(status_code=404, detail="Record not found")
    return Response(status_code=HTTP_204_NO_CONTENT)
