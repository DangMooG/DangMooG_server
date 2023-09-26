
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from starlette.responses import Response
from starlette.status import HTTP_204_NO_CONTENT, HTTP_401_UNAUTHORIZED

from core.schema import RequestPage
from core.utils import get_crud
from models.photo import Photo
from models.post import Post
from models.liked import Liked
from schemas import post, photo
from routers.account import get_current_user
from routers.photo import upload_file
from models.account import Account

import boto3

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
    upload = post.UploadPost(**req.dict(), account_id=current_user.account_id, username=current_user.username)
    return crud.create_record(Post, upload)

@router.post(
    "/create_with_photo", name="Post 사진과 함께 생성", description="Post 테이블에 사진과 함께 Record를 생성합니다",
)
async def create_with_photo(req: post.BasePost = Depends(), files: List[UploadFile] = File(...), crud=Depends(get_crud), current_user: Account = Depends(get_current_user)):
    upload = post.PhotoPost(**req.dict(), representative_photo_id=0, account_id=current_user.account_id, username=current_user.username)
    temp_post = crud.create_record(Post, upload)
    for idx, file in enumerate(files):
        url = await upload_file(file)
        temp_photo = photo.PhotoComplete(
            post_id=temp_post.post_id,
            category_id=temp_post.category_id,
            status=0,
            url=url,
            account_id=current_user.account_id
        )
        if idx == 0:
            temp = crud.create_record(Photo, temp_photo)
            rep_photo_id = temp.photo_id
        else:
            crud.create_record(Photo, temp_photo)
    request = {"representative_photo_id": rep_photo_id}
    return crud.patch_record(temp_post, request)


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
async def update_post(req: post.PhotoPost, id: int, crud=Depends(get_crud), current_user: Account = Depends(get_current_user)):
    if req.account_id != current_user.account_id:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Unauthorized request")
    filter = {"post_id": id}
    db_record = crud.get_record(Post, filter)
    if db_record is None:
        return crud.create_record(Post, req)

    if db_record.account_id == current_user.account_id:
        raise HTTPException(status_code=401, detail="Unauthorized request")

    return crud.update_record(db_record, req)


@router.patch(
    "/{id}",
    name="Post 한 record 일부 내용 수정",
    description="수정하고자 하는 id의 record 일부 수정, record가 존재하지 않을시엔 404 오류 메시지반환합니다",
    response_model=post.ReadPost,
)
async def update_post_sub(req: post.PatchPost, id: int, crud=Depends(get_crud), current_user: Account = Depends(get_current_user)):
    if req.account_id != current_user.account_id:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Unauthorized request")
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
    if id != current_user.account_id or db_record is None:
        raise HTTPException(status_code=401, detail="Unauthorized request")
    db_api = crud.delete_record(Post, filter)
    if db_api != 1:
        raise HTTPException(status_code=404, detail="Record not found")
    return Response(status_code=HTTP_204_NO_CONTENT)


@router.post(
    "/like_up",
    name="Post like +1",
    description="입력된 id에 해당하는 post의 좋아요를 사용자의 계정으로 1개 증가시킵니다.",
)
async def like_up(id: int, crud=Depends(get_crud), current_user: Account = Depends(get_current_user)):
    filter = {"post_id": id}
    db_record = crud.get_record(Post, filter)
    if db_record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    filter_model = post.LikedPatch(post_id=id, account_id=current_user.account_id)
    is_duplicated = crud.search_record(Liked, filter_model)
    if is_duplicated:
        raise HTTPException(status_code=409, detail="You already like it")
    patch = {"liked": db_record.liked+1}
    crud.patch_record(db_record, patch)
    return crud.create_record(Liked, post.LikedPatch(post_id=id, account_id=current_user.account_id))


@router.post(
    "/like_back",
    name="Post like -1",
    description="이전에 입력된 id에 해당하는 post에 추가된 좋아요를 사용자의 계정으로 1개 감소시킵니다.",
)
async def like_back(id: int, crud=Depends(get_crud), current_user: Account = Depends(get_current_user)):
    filter = {"post_id": id, "account_id": current_user.account_id}
    db_record = crud.search_record(Liked, filter)
    if len(db_record) < 1:
        raise HTTPException(status_code=404, detail="Record not found")
    post_record = crud.get_record(Post, {"post_id": id})
    patch = {"liked": post_record.liked-1}
    crud.patch_record(post_record, patch)
    db_api = crud.delete_record(Liked, {"liked_id": db_record[0].liked_id})
    if db_api != 1:
        raise HTTPException(status_code=404, detail="Record not found")
    return Response(status_code=HTTP_204_NO_CONTENT)

@router.post(
    "/get_like_list",
    name="like list extraction",
    description="현재 이용자의 좋아요한 게시물의 리스트를 가져옵니다"
)
async def like_list(crud=Depends(get_crud), current_user: Account = Depends(get_current_user)):
    filter = {"account_id": current_user.account_id}
    db_record = crud.search_record(Liked, filter)
    if len(db_record) < 1:
        raise HTTPException(status_code=404, detail="Record not found")
    return db_record

