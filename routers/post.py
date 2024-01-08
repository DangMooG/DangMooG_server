from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Body
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
from typing import Optional

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
    "/create_post",
    name="Post record 생성, 사진 기능 없음",
    description="Post 테이블에 Record 생성합니다, 게시물을 생성합니다.\n\n"
                "title은 글의 제목(string)입니다.\n\n"
                "price는 상품의 가격(integer)입니다.\n\n"
                "description은 게시물 내용(string) 즉, 상품의 상세 설명과 거래 형태에 대한 내용입니다.\n\n"
                "category_id는 해당 게시물이 어느 카테고리(integer)에 속하는지에 대한 내용입니다.",
    response_model=post.ReadPost,
    response_model_exclude={"account_id", "representative_photo_id", "liked", "create_time", "update_time"},
    responses={
                 200: {
                     "description": "정상적으로 게시물이 데이터베이스에 저장되었을 때의 출력입니다.",
                     "content": {
                         "application/json": {
                             "example": {
                                 "title": "짱구 띠부띠부 스티커 한정판",
                                 "price": 10000,
                                 "description": "정말 어렵게 획득한 짱구 스티커 입니다...\n대학 기숙사 A동에서 직거래 가능해요! 네고 사절입니다.",
                                 "category_id": 1,
                                 "status": 0,
                                 "use_locker": 1,
                                 "username": "your_nickname",
                                 "post_id": 1
                             }
                         }
                     }
                 }
             }
)
async def create_post(req: post.BasePost, crud=Depends(get_crud), current_user: Account = Depends(get_current_user)):
    print(current_user)
    upload = post.UploadPost(**req.dict(), account_id=current_user.account_id, username=current_user.username)
    return crud.create_record(Post, upload)


@router.post(
    "/create_with_photo", name="Post 사진(옵션)과 함께 생성", description="Post 테이블에 사진과 함께 Record를 생성합니다\n\n"
                                                                 "사진 없이 그냥 files=처럼 아무런 값 지정하는 것 없이 글을 "
                                                                 "생성할 수 있습니다.\n\n"
                                                                 "기본적으로 사용자의 닉네임이 설정되어야만 게시물을 작성할 수 있습니다.\n\n"
                                                                 "사진없이 글을 올릴 때와는 다르게 글의 내용에 들어갈 변수들은 쿼리(query)"
                                                                 "형식으로 작성되어야 합니다.\n\n"
                                                                 "title은 글의 제목(string)입니다.\n\n"
                                                                 "price는 상품의 가격(integer)입니다.\n\n"
                                                                 "description은 게시물 내용(string) 즉, 상품의 상세 설명과 거래 형태"
                                                                 "에 대한 내용입니다.\n\n"
                                                                 "category_id는 해당 게시물이 어느 카테고리(integer)에 속하는지에 "
                                                                 "대한 내용입니다.\n\n"
                                                                 "Request Body에 사진 파일들을 담으면 됩니다."
                                                                 "(사진 없이도 게시글 업로드는 가능합니다.)",
    response_model=post.PatchPost,
    response_model_exclude={"account_id", "liked", "create_time", "update_time"},
    responses={
                 200: {
                     "description": "정상적으로 게시물이 데이터베이스에 저장되었을 때의 출력입니다.",
                     "content": {
                         "application/json": {
                             "example": {
                                 "title": "짱구 띠부띠부 스티커 한정판",
                                 "price": 10000,
                                 "description": "정말 어렵게 획득한 짱구 스티커 입니다...\n대학 기숙사 A동에서 직거래 가능해요! 네고 사절입니다.",
                                 "category_id": 1,
                                 "status": 0,
                                 "use_locker": 0,
                                 "username": "your_nickname",
                                 "post_id": 7,
                                 "representative_photo_id": 13
                             }
                         }
                     }
                 }
             }
)
async def create_with_photo(req: post.BasePost = Depends(), files: Optional[List[UploadFile]] = None, crud=Depends(get_crud), current_user: Account = Depends(get_current_user)):
    upload = post.PhotoPost(**req.dict(), representative_photo_id=0, account_id=current_user.account_id, username=current_user.username)
    temp_post = crud.create_record(Post, upload)
    search_id = temp_post.post_id
    if not files:
        return temp_post
    for idx, file in enumerate(files):
        url = await upload_file(file, "post")
        temp_photo = photo.PhotoComplete(
            post_id=temp_post.post_id,
            category_id=temp_post.category_id,
            url=url,
            account_id=current_user.account_id
        )
        if idx == 0:
            temp = crud.create_record(Photo, temp_photo)
            rep_photo_id = temp.photo_id
        else:
            crud.create_record(Photo, temp_photo)
    request = {"representative_photo_id": rep_photo_id}
    crud.patch_record(temp_post, request)
    return crud.get_record(Post, {"post_id": search_id})


@router.post(
    "/page-list",
    name="Post Page 리스트 조회(web 최적화)",
    description="Post 테이블의 페이지별 Record list 가져오는 API입니다.\
                Page는 0이 아닌 양수로 입력해야합니다\
                Size는 100개로 제한됩니다.\n\n"
                "웹 페이지의 게시글 리스트 조회 형식이므로 앱에서는 사용을 비추천합니다.",
    response_model=post.ResponseModel
)
async def page_post(req: RequestPage, crud=Depends(get_crud)):
    if req.page <= 0:
        raise HTTPException(status_code=400, detail="Page number should be positive")
    if req.size > 100:
        raise HTTPException(status_code=400, detail="Size should be below 100")
    if req.size <= 0:
        raise HTTPException(status_code=400, detail="Size should be positive")
    return crud.paging_record(Post, req)


@router.get(
    "/app-paging",
    name="app을 위한 paging method",
    description="어플리케이션에서 페이징을 요쳥할 때 사용하는 api입니다. get method에 query로, \n\n"
                "size(int) - 받고자 하는 페이지 양\n\n"
                "checkpoint(int, None) - 현재 페이지 마지막 항목에 대한 값입니다. 처음 요청할 때는 아무것도 입력하지 않아도 됩니다.\n\n"
                "해당 api를 실행하면 response로 필요한 페이징과 다음 요청을 위한 next_checkpoint 값이 반환됩니다. 이걸 가지고 다음 요청의 "
                "checkpoint query값으로 활용하면 됩니다. 이는 페이징 로딩중에 새로운 게시물이 올라와도 중복해서 게시물을 로드 하지 않도록 하는 "
                "checkpoint 값입니다.\n\n"
                "성능 유지를 위해 size는 최대 99개의 요청까지 수용 가능합니다.\n\n"
                "가장 최신의 게시물부터 가져오며, 가장 끝의 게시물을 가져오게 되면 \"next_checkpoint\" 값이 -1로 반환됩니다.",
    response_model=post.AppResponseModel,
    responses={
        200: {
            "description": "GIST 메일을 통해서 회원가입 요청이 온다면 200 status code 표시와 함께, request body에 입력한"
                           "메일로 6자리의 랜덤 정수 코드가 보내집니다. \n\n"
                           "Response: 처음 가입시 status 값이 0으로 이미 회원일 경우 status 1과 함께 안내 메시지가 같이 "
                           "반환됩니다.",
            "content": {
                "application/json": {
                    "examples": {
                        "10개의 게시글이 있는 상태에서 checkpoint를 설정하지 않고 size를 2로 요청한 경우": {
                            "value": {
                                "items": [
                                    {
                                        "price": 10000,
                                        "post_id": 10,
                                        "description": "정말 어렵게 획득한 짱구 스티커 입니다...\n대학 기숙사 A동에서 직거래 가능해요! 네고 사절입니다.",
                                        "category_id": 1,
                                        "liked": 0,
                                        "update_time": "2023-10-18T13:12:04",
                                        "title": "test post 9999",
                                        "representative_photo_id": "null",
                                        "status": 0,
                                        "username": "trial_your_nickname",
                                        "create_time": "2023-10-18T13:12:04"
                                    },
                                    {
                                        "price": 10000,
                                        "post_id": 9,
                                        "description": "정말 어렵게 획득한 짱구 스티커 입니다...\n대학 기숙사 A동에서 직거래 가능해요! 네고 사절입니다.",
                                        "category_id": 1,
                                        "liked": 0,
                                        "update_time": "2023-10-18T13:11:59",
                                        "title": "test post 8888",
                                        "representative_photo_id": "null",
                                        "status": 0,
                                        "username": "trial_your_nickname",
                                        "create_time": "2023-10-18T13:11:59"
                                    }
                                ],
                                "next_checkpoint": 8
                            }
                        },
                        "바로 next_checkpoint -> 8을 checkpoint query에 넣어서 실행할 경우": {
                            "value": {
                                "items": [
                                    {
                                        "price": 10000,
                                        "post_id": 8,
                                        "description": "정말 어렵게 획득한 짱구 스티커 입니다...\n대학 기숙사 A동에서 직거래 가능해요! 네고 사절입니다.",
                                        "category_id": 1,
                                        "liked": 0,
                                        "update_time": "2023-10-18T13:11:54",
                                        "title": "test post 7777",
                                        "representative_photo_id": "null",
                                        "status": 0,
                                        "username": "trial_your_nickname",
                                        "create_time": "2023-10-18T13:11:54"
                                    },
                                    {
                                        "price": 10000,
                                        "post_id": 7,
                                        "description": "정말 어렵게 획득한 짱구 스티커 입니다...\n대학 기숙사 A동에서 직거래 가능해요! 네고 사절입니다.",
                                        "category_id": 1,
                                        "liked": 0,
                                        "update_time": "2023-10-18T13:11:46",
                                        "title": "test post 666",
                                        "representative_photo_id": "null",
                                        "status": 0,
                                        "username": "trial_your_nickname",
                                        "create_time": "2023-10-18T13:11:46"
                                    }
                                ],
                                "next_checkpoint": 6
                            }
                        },
                        "마지막에 1개가 남았는데 2개의 size를 요청할 경우": {
                            "value": {
                                "items": [
                                    {
                                        "price": 10000,
                                        "post_id": 1,
                                        "description": "정말 어렵게 획득한 짱구 스티커 입니다...\n대학 기숙사 A동에서 직거래 가능해요! 네고 사절입니다.",
                                        "category_id": 1,
                                        "liked": 0,
                                        "update_time": "2023-10-18T11:51:31",
                                        "title": "짱구 띠부띠부 스티커 한정판",
                                        "representative_photo_id": "null",
                                        "status": 0,
                                        "username": "trial_your_nickname",
                                        "create_time": "2023-10-18T11:51:31"
                                    }
                                ],
                                "next_checkpoint": -1
                            }
                        }
                    }
                }
            }
        },
    }
)
async def app_page_listing(size: int, checkpoint: Optional[int] = None, crud=Depends(get_crud), current_user: Account = Depends(get_current_user)):
    if size > 100:
        raise HTTPException(status_code=400, detail="Size should be below 100")
    if size <= 0:
        raise HTTPException(status_code=400, detail="Size should be positive")
    if checkpoint:
        return crud.app_paging_record(Post, size, checkpoint, current_user=current_user.account_id)
    else:
        return crud.app_paging_record(table=Post, size=size, account_id=current_user.account_id)



@router.post(
    "/search",
    name="Post 테이블에서 입력한 조건들에 부합하는 record 를 반환하는 API",
    description="body에 원하는 조건들을 입력하면 and로 필터 결과 리스트를 반환합니다\n\n"
                "조건값이 str 일 경우 그 문자열을 포함하는 모든 record를 반환합니다.\n\n"
                "조건값이 int,float 일 경우 그 값과 동일한 record만 반환합니다.\n\n"
                "조건값이 list 경우 list 항목을 포함하는 모든 record를 반환합니다.\n\n"
                "조건값은 dictionary 형태로 모델에서 검색가능한 [post_id, title, price, description, representative_photo_id, "
                "status, account_id, username, liked]\n\n"
                "위와 같은 목록들을 검색할 수 있습니다. 원하는 필드만 넣어서 검색할 수 있습니다.",
    response_model=List[post.PatchPost],
)
async def search_post(
        filters: dict = Body(..., examples=[{
            "post_id": 1,
            "title": "post title example",
            "price": 10000,
            "description": "post_description",
            "representative_photo_id": 1,
            "status": 0,
            "account_id": 1,
            "username": "이재선",
            "liked": 3
        }]), crud=Depends(get_crud)):
    return crud.search_record(Post, filters)


@router.post(
    "/my_post",
    name="Post 테이블에서 자신이 작성한 게시물의 post_id 목록을 불러오는 API",
    description="Header에 사용자가 자신의 토큰을 보내면, 자동으로 사용자가 쓴 글 post_id의 목록을 불러옵니다.",
    responses={
        200: {
            "description": "정상적으로 게시물이 데이터베이스에 저장되었을 때의 출력입니다.",
            "content": {
                "application/json": {
                    "example": {
                        "result":
                            [
                                10,
                                9,
                                8,
                                7,
                                6,
                                5,
                                4,
                                3,
                                2,
                                1
                            ]
                    }
                }
            }
        }
    }
)
async def get_my_post(current_user: Account = Depends(get_current_user), crud=Depends(get_crud)):
    posts = crud.search_record(Post, {"account_id": current_user.account_id})
    post_ids = [element.post_id for element in posts]
    return {"result": post_ids[::-1]}


@router.post(
    "/my_items",
    name="Post 테이블에서 자신이 구매한 게시물의 post_id 목록을 불러오는 API",
    description="Header에 사용자가 자신의 토큰을 보내면, 자동으로 사용자가 쓴 글 post_id의 목록을 불러옵니다.",
    responses={
        200: {
            "description": "정상적으로 게시물이 데이터베이스에서 가져와졌을 때의 출력입니다.",
            "content": {
                "application/json": {
                    "example": {
                        "result":
                            [
                                10,
                                9,
                                8,
                                7,
                                6,
                                5,
                                4,
                                3,
                                2,
                                1
                            ]
                    }
                }
            }
        }
    }
)
async def get_my_post(current_user: Account = Depends(get_current_user), crud=Depends(get_crud)):
    posts = crud.search_record(Post, {"buyer": current_user.account_id})
    post_ids = [element.post_id for element in posts]
    return {"result": post_ids[::-1]}


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
    description="수정하고자 하는 id의 record 일부 수정, record가 존재하지 않을시엔 404 오류 메시지반환합니다\n\n"
                "예시 중에 변경하고 싶은 key와 value만 지정하면 됩니다.",
    response_model=post.ReadPost,
    response_model_exclude={"account_id", "liked", "create_time", "update_time"},
    responses={
                 200: {
                     "description": "정상적으로 게시물이 데이터베이스에 업데이트 되었을 때의 출력입니다.",
                     "content": {
                         "application/json": {
                             "example": {
                                 "title": "짱구 띠부띠부 스티커 한정판",
                                 "price": 10000,
                                 "description": "정말 어렵게 획득한 짱구 스티커 입니다...\n대학 기숙사 A동에서 직거래 가능해요! 네고 사절입니다.",
                                 "category_id": 1,
                                 "status": 0,
                                 "use_locker": 0,
                                 "username": "your_nickname",
                                 "post_id": 7,
                                 "representative_photo_id": 13
                             }
                         }
                     }
                 }
             }
)
async def update_post_sub(id: int, req: dict = Body(..., examples=[{
    "post_id": 1,
    "title": "post title example",
    "price": 10000,
    "description": "post_description",
    "representative_photo_id": 1,
    "status": 0,
}]), crud=Depends(get_crud), current_user: Account = Depends(get_current_user)):
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
    if db_record.account_id != current_user.account_id or db_record is None:
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

