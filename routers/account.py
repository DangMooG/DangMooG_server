from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from jose import jwt, JWTError
from starlette import status
from starlette.responses import Response
from starlette.status import HTTP_204_NO_CONTENT, HTTP_200_OK
from passlib.context import CryptContext

from core.schema import RequestPage
from core.utils import get_crud
from models.account import Account
from schemas import account

from typing import List
from os import environ
from datetime import timedelta, datetime

import smtplib
from email.mime.text import MIMEText
import random
import traceback

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter(
    prefix="/account",
    tags=["Account"],
)


def send_mail(to_who):
    token = ''.join(random.choices('0123456789', k=6))
    sender = "dotorit2023@gmail.com"
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(sender, environ["MAIL_API_KEY"])
        msg = MIMEText(
            '안녕하세요, \n\n'
            '지스트 중고장터 \"도토릿\" 가입을 위한 인증번호는 아래와 같습니다.\n\n'
            f'[{token}]\n\n'
            '5분 내에 인증번호 입력창에 인증을 완료해주셔야 합니다. 감사합니다')
        msg['Subject'] = '도토릿 지스트 중고장터 서비스 이용을 위한 인증 메일입니다.'
        msg['From'] = sender
        msg['To'] = to_who
        smtp.sendmail(sender, to_who, msg.as_string())
        smtp.quit()
    return token


"""
Account table CRUD
"""


@router.post("/mail_send", name="Gist mail 인증 메일 발송", description="기본적으로 회원가입을 진행하기 위해서 사용합니다.\n"
                                                                  "이미 회원이라면 로그인 토큰을 발급받기 위한 과정으로 사용됩니다."
                                                                  "필요한 것은 메일 하나뿐 입니다.\n"
                                                                  "password는 None을 보내도 상관없습니다.")
async def mail_verification(req: account.AccountCreate, crud=Depends(get_crud)):
    if "@gist.ac.kr" not in req.email and "@gm.gist.ac.kr" not in req.email:
        raise HTTPException(status_code=401, detail="Not valid request, please use gist mail")
    mail_id = req.email.split("@")[0]
    filter = {"email": mail_id}
    is_exist = crud.get_record(Account, filter)
    verification_number = send_mail(req.email)
    if is_exist:
        update = account.AccountReceate(password=pwd_context.hash(verification_number))
        crud.patch_record(is_exist, update)
        return JSONResponse(jsonable_encoder([{
            "status": 1,
            "message": "이미 존재하는 계정입니다."
        }]))
    else:
        db_account = account.AccountSet(**req.dict(), password=pwd_context.hash(verification_number))
        crud.create_record(Account, db_account)
        return JSONResponse(jsonable_encoder([{
            "status": 0,
            "message": "메일을 전송하였습니다."
        }]))


ACCESS_TOKEN_EXPIRE_DAYS = 30 * 6
SECRET_KEY = environ["ACCESS_TOKEN_HASH"]
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/meta/account/verification")


@router.post(
    "/verification", name="Mail 인증 번호 확인 API", description="보낸 인증 메일의 번호에 대한 확인과 함께 테이블에 유저 생성이 완료됩니다.\n"
                                                           "추가로 username생성이 필요합니다.\n"
                                                           "로그인의 형식에 필요한 username은 email의 @앞의 아이디 부분이며, password는 메일로 발송된 인증코드입니다.\n"
                                                           "5분 이내에 해당 주소를 통해서 메일 인증 즉, 로그인이 진행되어야 합니다.",
    response_model=account.Token
)
async def active_account(form_data: OAuth2PasswordRequestForm = Depends(),
                         crud=Depends(get_crud)):
    filter = {"email": form_data.username}  # email input required
    user = crud.get_record(Account, filter)
    if not user or not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if datetime.now() > user.update_time + timedelta(minutes=10):
        raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail="Authentication number has expired")

    # make access token
    data = {
        "sub": str(user.account_id),
        "exp": datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    }
    access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "account_id": user.account_id
    }


def get_current_user(token: str = Depends(oauth2_scheme),
                     crud=Depends(get_crud)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        account_id: str = payload.get("sub")
        if datetime.fromtimestamp(payload.get("exp")) < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if account_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    else:
        filter = {"account_id": account_id}
        user = crud.get_record(Account, filter)
        if user is None:
            raise credentials_exception
        return user


@router.post(
    "/is_valid_token", name="Account token 유효 확인", description="현재 유저가 자신이 가지고 있는 토큰이 유효하는지 알려주는 api입니다."
)
async def check_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        account_id: str = payload.get("sub")
        if datetime.fromtimestamp(payload.get("exp")) < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if account_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    else:
        return HTTP_200_OK


@router.post(
    "/jail_control", name="Account 교도소 관리", description="Account의 available, jail_until을 설정하여 악성 유저의 계정을 정지합니다.",
    response_model=account.AccountCreate
)
async def update_post_sub(req: account.PatchAccount, current_user: Account = Depends(get_current_user), crud=Depends(get_crud)):
    filter = {"account_id": current_user.account_id}
    db_record = crud.get_record(Account, filter)
    if db_record is None:
        raise HTTPException(status_code=404, detail="Record not found")

    return crud.patch_record(db_record, req)


@router.patch(
    "/set_username", name="Account 닉네임 설정 및 변경", description="Account의 username(서비스 내에서는 별명)을 설정합니다.",
    response_model=account.AccountCreate
)
async def update_post_sub(req: account.NicnameSet, crud=Depends(get_crud), current_user: Account = Depends(get_current_user)):
    filter = {"account_id": current_user.account_id}
    db_record = crud.get_record(Account, filter)
    if db_record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    filter = {"username": req.username}
    if crud.get_record(Account, filter):
        raise HTTPException(status_code=409, detail="Already reserved username")

    return crud.patch_record(db_record, req)


@router.patch(
    "/set_user_profile_photo", name="Account record 생성", description="Account의 username, available, jail_until을 설정합니다",
    response_model=account.AccountCreate
)
async def update_post_sub(req: account.PhotoAccount, file: UploadFile = File(...), current_use: Account = Depends(get_current_user), crud=Depends(get_crud)):
    filter = {"account_id": current_use.account_id}
    db_record = crud.get_record(Account, filter)
    if db_record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    from routers.photo import upload_file
    url = await upload_file(file)
    temp = req.model_copy()
    temp.url = url
    return crud.patch_record(db_record, temp)


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


@router.delete(
    "/",
    name="Account record 삭제",
    description="입력된 id에 해당하는 record를 삭제합니다.",
)
async def delete_account(current_user: Account=Depends(get_current_user), crud=Depends(get_crud)):
    filter = {"account_id": current_user.account_id}
    db_api = crud.delete_record(Account, filter)
    if db_api != 1:
        raise HTTPException(status_code=404, detail="Record not found")
    return Response(status_code=HTTP_204_NO_CONTENT)
