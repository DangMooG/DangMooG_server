from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from starlette.responses import Response
from starlette.status import HTTP_204_NO_CONTENT

from core.schema import RequestPage
from core.utils import get_crud
from models.photo import Photo
from models.post import Post
from models.account import Account
from routers.account import get_current_user
from schemas import photo, post

from typing import List
from os import environ
import dotenv

import boto3

dotenv.load_dotenv(verbose=True)

router = APIRouter(
    prefix="/photo",
    tags=["Photo"],
)
"""
Photo table CRUD
"""

async def upload_file(file: File(...)):
    try:
        # s3 클라이언트 생성
        s3 = boto3.client(
            service_name="s3",
            region_name="ap-northeast-2",
            aws_access_key_id=environ["S3_ACCESS"],
            aws_secret_access_key=environ["S3_SECRET"],
        )
    except Exception as e:
        print(e)
    else:
        s3.upload_fileobj(file.file, "dangmuzi-photo", file.filename)
        return "https://dangmuzi-photo.s3.ap-northeast-2.amazonaws.com/"+file.filename



@router.post(
    "/", name="Photo record 생성", description="Photo 테이블에 Record 생성합니다\n"
                                             "여러장 가능합니다."
)
async def create_post(req: photo.PhotoUpload = Depends(), files: List[UploadFile] = File(...), current_user: Account = Depends(get_current_user), crud=Depends(get_crud)):
    for idx, file in enumerate(files):
        url = await upload_file(file)
        temp = photo.PhotoComplete(**req.dict(), url=url, account_id=current_user.account_id)
        if idx == 0:
            temp = crud.create_record(Photo, temp)
            rep_photo_id = temp.photo_id
        else:
            crud.create_record(Photo, temp)
    temp_post = crud.get_record(Post, {"post_id": req.post_id})
    request = post.PhotoPost(representative_photo_id=rep_photo_id)
    return crud.patch_record(temp_post, request)


@router.post(
    "/page-list",
    name="Photo Page 리스트 조회",
    description="Photo 테이블의 페이지별 Record list 가져오는 API입니다.\
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
    return crud.paging_record(Photo, req)


@router.post(
    "/search",
    name="Photo 테이블에서 입력한 조건들에 부합하는 record 를 반환하는 API",
    description="body에 원하는 조건들을 입력하면 and로 필터 결과 리스트를 반환합니다\
        조건값이 str 일 경우 그 문자열을 포함하는 모든 record를 반환합니다.\
        조건값이 int,float 일 경우 그 값과 동일한 record만 반환합니다.\
        조건값이 list 경우 list 항목을 포함하는 모든 record를 반환합니다.\
    ",
    response_model=List[photo.ReadPhoto],
)
async def search_post(filters: photo.SearchPhoto, crud=Depends(get_crud)):
    return crud.search_record(Photo, filters)


@router.get(
    "/list",
    name="Photo 리스트 조회",
    description="Photo 테이블의 모든 Record를 가져옵니다",
    response_model=List[photo.ReadPhoto],
)
def get_list(crud=Depends(get_crud)):
    return crud.get_list(Photo)


@router.get(
    "/{id}",
    name="Photo record 가져오기",
    description="입력된 id를 키로 해당하는 Record 반환합니다",
    response_model=photo.ReadPhoto,
)
def read_post(id: int, crud=Depends(get_crud)):
    filter = {"photo_id": id}
    db_record = crud.get_record(Photo, filter)
    if db_record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return db_record


@router.delete(
    "/{id}",
    name="Photo record 삭제",
    description="입력된 id에 해당하는 record를 삭제합니다.",
)
async def delete_post(id: int, crud=Depends(get_crud)):
    filter = {"photo_id": id}
    db_api = crud.delete_record(Photo, filter)
    if db_api != 1:
        raise HTTPException(status_code=404, detail="Record not found")
    return Response(status_code=HTTP_204_NO_CONTENT)
