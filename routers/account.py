from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Body, Form, Query
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from jose import jwt, JWTError
from starlette import status
from starlette.responses import Response
from starlette.status import HTTP_204_NO_CONTENT, HTTP_200_OK
from typing_extensions import Annotated
from passlib.context import CryptContext
from pydantic import Field

from core.schema import RequestPage
from core.utils import get_crud
from models.account import Account, Blame
from models.post import Post
from models.chat import Room
from schemas import account

from typing import List, Union
from os import environ
from datetime import timedelta, datetime
import dotenv

import smtplib
from email.mime.text import MIMEText
import random

dotenv.load_dotenv(verbose=True)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter(
    prefix="/account",
    tags=["Account"],
)


async def send_mail(to_who):
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


async def blame(blame_user, blamed_id, content, account_id):
    sender = "dotorit2023@gmail.com"
    if blame_user:
        txt = '사용자'
    else:
        txt = '게시물'
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(sender, environ["MAIL_API_KEY"])
        msg = MIMEText(
            f'{content}')
        msg['Subject'] = f'{account_id}번 사용자가 {blamed_id}번의 {txt}을 신고하였습니다.'
        msg['From'] = sender
        msg['To'] = sender
        smtp.sendmail(sender, sender, msg.as_string())
        smtp.quit()
    return 0


async def rate_limit(email):
    global last_request_time
    current_time = datetime.now()
    if email in last_request_time:
        # 마지막 요청 시간과 현재 시간 비교
        if current_time - last_request_time[email] < timedelta(minutes=1):
            raise HTTPException(status_code=429, detail="Too many requests. Please wait a minute.")
    # 현재 시간 업데이트
    last_request_time[email] = current_time



"""
Account table CRUD
"""
last_request_time = {}


@router.post("/mail_send",
             name="Gist mail 인증 메일 발송",
             description="기본적으로 회원가입을 진행하기 위한 메일 발송을 위해 사용합니다.\n\n"
                         "이미 회원이라면 로그인 토큰을 발급받기 위한 과정으로 사용됩니다.\n\n"
                         "필요한 것은 GIST메일(gm 메일도 가능) 하나뿐 입니다.",
             responses={
                 200: {
                     "description": "GIST 메일을 통해서 회원가입 요청이 온다면 200 status code 표시와 함께, request body에 입력한"
                                    "메일로 6자리의 랜덤 정수 코드가 보내집니다. \n\n"
                                    "Response: 처음 가입시 status 값이 0으로 이미 회원일 경우 status 1과 함께 안내 메시지가 같이 "
                                    "반환됩니다.",
                     "content": {
                         "application/json": {
                             "examples": {
                                 "처음 가입 시": {
                                     "value": {
                                         "status": 0,
                                         "message": "메일을 전송하였습니다."
                                     }
                                 },
                                 "이미 가입된 계정일 경우": {
                                     "value": {
                                         "status": 1,
                                         "message": "이미 존재하는 계정입니다."
                                     }
                                 }
                             }
                         }
                     }
                 },
                 401: {
                     "description": "지스트 메일을 사용하지 않을 경우의 출력입니다. status code 401",
                     "content": {
                         "application/json": {
                             "example": {
                                 "detail": "Not valid request, please use gist mail"
                             }
                         }
                     }
                 }
             }
             )
async def mail_verification(req: account.AccountCreate, crud=Depends(get_crud)):
    if req.email == "dangmoog123@gist.ac.kr" or req.email == "dotorit123@gist.ac.kr" or req.email == "gist123@gist.ac.kr":
        mail_id = req.email.split("@")[0]
        await rate_limit(mail_id)
        filter = {"email": mail_id}
        is_exist = crud.get_record(Account, filter)
        if is_exist:
            return JSONResponse(jsonable_encoder([{
                "status": 1,
                "message": "이미 존재하는 계정입니다."
            }]))
        else:
            req.email = mail_id
            db_account = account.AccountSet(**req.dict(), password=pwd_context.hash(environ["SPECIAL_PWD"]), gm=0)
            crud.create_record(Account, db_account)
            return JSONResponse(jsonable_encoder([{
                "status": 0,
                "message": "테스트 계정을 생성하였습니다."
            }]))
    if "@gist.ac.kr" not in req.email and "@gm.gist.ac.kr" not in req.email:
        raise HTTPException(status_code=401, detail="Not valid request, please use gist mail")
    mail_id, domain = req.email.split("@")
    await rate_limit(mail_id)
    filter = {"email": mail_id}
    is_exist = crud.get_record(Account, filter)
    verification_number = await send_mail(req.email)
    if is_exist:
        update = account.AccountReceate(password=pwd_context.hash(verification_number))
        crud.patch_record(is_exist, update)
        if is_exist.available == 3:
            crud.patch_record(is_exist, {"available": 2})
            return JSONResponse(jsonable_encoder([{
                "status": 0,
                "message": "재가입 계정입니다."
            }]))

        return JSONResponse(jsonable_encoder([{
            "status": 1,
            "message": "이미 존재하는 계정입니다."
        }]))
    else:
        req.email = mail_id
        db_account = account.AccountSet(
            **req.dict(),
            password=pwd_context.hash(verification_number),
            gm=1 if domain.startswith("gm") else 0
        )
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
    "/verification", name="Mail 인증 번호 확인 API", description="보낸 인증 메일의 번호에 대한 확인과 함께 테이블에 유저 생성이 완료됩니다.\n\n"
                                                           "fcm은 사용자의 알림을 받기위한 클라우드메시징 토큰값을 넣는 곳입니다."
                                                           "추가로, 사전에 유저닉네임 설정이 필요합니다. \n\n"
                                                           "로그인의 형식에 필요한 username은 email의 @앞의 아이디 부분이며, "
                                                           "password는 메일로 발송된 인증코드입니다.\n\n"
                                                           "5분 이내에 해당 주소를 통해서 메일 인증 즉, 로그인이 진행되어야 합니다.",
    response_model=account.Token,
    responses={
                 200: {
                     "description": "access_token은 사용자의 자동 로그인, 사용자 인증을 위한 토큰입니다.(반드시 앱 내에서 저장하고"
                                    "있어야합니다.)\n\n"
                                    "token_type은 사용자의 토큰 인증 방식에 관한 내용입니다. JWT에서는 Bearer방식을 사용합니다.\n\n"
                                    "account_id는 사용자의 계정 식별 번호입니다. 토큰 내에 암호화 되어 저장될 수 입니다.\n\n"
                                    "is_username은 사용자가 현재 닉네임(DB에서 username)을 설정했는지 여부입니다. 설정했다면 1로"
                                    "표시되고 아직 닉네임을 설정하지 않았다면 0으로 표시됩니다.",
                     "content": {
                         "application/json": {
                             "example": {
                                 "access_token": "encrypted hash value",
                                 "token_type": "bearer",
                                 "account_id": 127,
                                 "is_username": 1
                             }
                         }
                     }
                 },
                 401: {
                     "description": "잘못된 비밀번호를 입력했을 때 나오는 출력입니다. status code 401",
                     "content": {
                         "application/json": {
                             "example": {
                                 "detail": "Incorrect username or password"
                             }
                         }
                     }
                 }
             }
)
async def active_account(fcm: Annotated[str, Form()] = "temporary", form_data: OAuth2PasswordRequestForm = Depends(),
                         crud=Depends(get_crud)):
    filter = {"email": form_data.username}  # email input required
    user = crud.get_record(Account, filter)
    crud.patch_record(user, {"fcm": fcm})
    if not user or not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if datetime.now() > user.update_time + timedelta(minutes=10) and (form_data.username != "dangmoog123" or form_data.username != "dotorit123" or form_data.username != "gist123"):
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
        "account_id": user.account_id,
        "is_username": 1 if user.username else 0
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
    "/me",
    name="Account token 유효 확인 및 유저 스스로 정보 획득",
    description="현재 유저가 자신이 가지고 있는 토큰이 유효하는지 알려주고 스스로의 정보를 획득할 수 있는 api입니다.\n\n"
                "-H 'Authorization: Bearer {token hash} \n\n"
                "위 같이 헤더에 Bearer방식으로 토큰을 넣어서 post하면 됩니다.",
    response_model=account.ReadAccount,
    response_model_exclude={"create_time", "update_time", "jail_until", "gm", "name_time"},
    responses={
        200: {
            "description": "정상적으로 인증이 완료되었을 때.\n\n"
                           "account_id는 사용자 식별용 id이며 정수형태입니다.\n\n"
                           "username은 사용자의 닉네임입니다. 설정하지 않았다면 null값을 반환합니다.\n\n"
                           "email은 사용자의 GIST메일의 아이디 부분만을 가져옵니다.\n\n"
                           "profile_url은 사용자가 설정한 프로필 사진을 저장하고 있는 URL입니다. 설정하지 않았다면 null을 반환합니다.",
            "content": {
                "application/json": {
                    "example": {
                        "status": 1,
                        "account_id": 1,
                        "username": "jaesun",
                        "email": "rejaealsun@gm.gist.ac.kr",
                        "profile_url": "https:// object_storage_url"
                    }
                }
            }
        },
        401: {
            "description": "로그인 하지 않고 시도할 경우의 반환값입니다.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Not authenticated"
                    }
                }
            }
        }
    }
)
async def check_token(current_user: Account = Depends(get_current_user)):
    result = current_user.to_dict()
    if result["gm"]:
        result["email"] = result["email"] + "@gm.gist.ac.kr"
    else:
        result["email"] = result["email"] + "@gist.ac.kr"
    return result


@router.patch(
    "/fcm_update", name="fcm 토큰 업데이트", description="Account의 fcm이 유효하지 않을때, 새롭게 fcm을 업데이트 하는 api입니다."
                                                   "쿼리 fcm에 토큰을 기입해서 요청해주세요."
)
async def update_fcm_token(fcm: Union[str, None] = Query(default=None), current_user: Account = Depends(get_current_user), crud=Depends(get_crud)):
    return crud.patch_record(current_user, {"fcm": fcm})



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


@router.post(
    "/check_name_duplication", name="Account 닉네임 중복확인", description="body data로 온 username이 데이터베이스에 이미 존재하는 "
                                                                    "항목인지 확인합니다. 중복일 경우 409를 돌려줍니다.",
    responses={
        200: {
            "description": "단순히 200 status code를 반환합니다.",
            "content": {
                "application/json": {
                    "example": 200
                }
            }
        },
        409: {
            "description": "이미 존재하는 닉네임이라는 것을 알려주는 status code입니다.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Already reserved username"
                    }
                }
            }
        }
    }
)
async def check_duplication(req: account.NicnameSet, crud=Depends(get_crud)):
    filter = {"username": req.username}
    if crud.get_record(Account, filter):
        raise HTTPException(status_code=409, detail="Already reserved username")

    return HTTP_200_OK


@router.patch(
    "/set_username", name="Account 닉네임 설정 및 변경", description="Account의 username(서비스 내에서는 닉네임)을 설정합니다.",
    response_model=account.NicnameSet,
    responses={
        200: {
            "description": "설정된 닉네임을 다시 반환합니다.",
            "content": {
                "application/json": {
                    "example": {
                        "username": "the_nickname_is_yours_now!"
                    }
                }
            }
        },
        404: {
            "description": "사용자를 찾을 수 없을 때 반환하는 status code입니다.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Record not found"
                    }
                }
            }
        },
        409: {
            "description": "이미 존재하는 닉네임이라는 것을 알려주는 status code입니다.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Already reserved username"
                    }
                }
            }
        }
    }
)
async def update_post_sub(req: account.NicnameSet, crud=Depends(get_crud), current_user: Account = Depends(get_current_user)):
    filter = {"account_id": current_user.account_id}
    db_record = crud.get_record(Account, filter)
    if db_record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    filter = {"username": req.username}
    if crud.get_record(Account, filter):
        raise HTTPException(status_code=409, detail="Already reserved username")
    if current_user.available:
        crud.patch_record(db_record, {"available": current_user.available-1, "name_time": datetime.now()})
        return crud.patch_record(db_record, req)
    limit_day = db_record.name_time + timedelta(days=30)
    if current_user.available == 0 and datetime.now() < limit_day:
        raise HTTPException(status_code=401, detail=f"{limit_day} 이후에 닉네임을 변결할 수 있습니다.")
    return crud.patch_record(db_record, req)


@router.post(
    "/bank",
    name="사용자의 계좌 정보 입력 및 수정",
    description="사용자의 계좌 정보를 설정합니다. 토큰과 함께, 은행명, 계좌번호를 전송하면 됩니다. \n\n"
                "기본적으로 계좌번호는 AES 양방향 암호화를 통해서 암호화 및 복호화 됩니다.",
    response_model=account.ReadAccount,
    response_model_exclude={"create_time", "update_time", "available", "jail_until"},
)
async def bank_post(req: account.BankSet, crud=Depends(get_crud), current_user: Account = Depends(get_current_user)):
    filter = {"account_id": current_user.account_id}
    db_record = crud.get_record(Account, filter)
    if db_record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return crud.patch_record(db_record, req)


@router.patch(
    "/set_user_profile_photo",
    name="Account profile photo 업로드 및 설정",
    description="사용자의 프로필 이미지를 설정합니다. 토큰과 함께, 설정할 사진을 전송하면 됩니다.",
    response_model=account.ReadAccount,
    response_model_exclude={"create_time", "update_time", "available", "jail_until"},
    responses={
        200: {
            "description": "변경된 사용자의 정보를 다시 반환합니다.",
            "content": {
                "application/json": {
                    "example": {
                        "account_id": 1,
                        "username": "jaesun",
                        "email": "rejaealsun",
                        "profile_url": "https:// changed_profile_url"
                    }
                }
            }
        },
        404: {
            "description": "사용자를 찾을 수 없을 때 반환하는 status code입니다.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Record not found"
                    }
                }
            }
        }
    }
)
async def update_post_sub(file: UploadFile = File(...), current_use: Account = Depends(get_current_user), crud=Depends(get_crud)):
    filter = {"account_id": current_use.account_id}
    db_record = crud.get_record(Account, filter)
    if db_record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    from routers.photo import upload_file
    url = await upload_file(file, "profile")
    temp = account.PhotoAccount(profile_url=url)
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
    description="body에 원하는 조건들을 입력하면 and로 필터 결과 리스트를 반환합니다.\n\n"
                "조건값이 str 일 경우 그 문자열을 포함하는 모든 record를 반환합니다.\n\n"
                "조건값이 int,float 일 경우 그 값과 동일한 record만 반환합니다.\n\n"
                "조건값이 list 경우 list 항목을 포함하는 모든 record를 반환합니다.\n\n"
                "dict로 검색가능 필드는 account_id(int), username(str), email(str), profile_url(str), available(int) 입니다."
                "\n\n모든 필드에 값을 넣어서 검색하지 않아도 됩니다. 원하는 필드만 사용하여서 검색이 가능합니다.",
    response_model=List[account.ReadAccount],
    response_model_exclude={"create_time", "update_time", "available", "jail_until"}
)
async def search_account(filters: dict = Body(..., examples=[{
    "account_id": 1,
    "username": "jaesun",
    "email": "rejaealsun",
    "profile_url": "https:// my_profile_url",
    "available": 1
  }]), crud=Depends(get_crud)):
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


@router.post(
    "/blame",
    name="계정 신고 post",
    description="신고기능 api.\n\n"
                "다른 사용자의 게시물을 신고하는 기능을 위한 api 입니다.\n\n"
                "필요한 것은 blame_user(유저신고면 이곳에 1 아니고 게시물 신고면 0 입력), blamed_id, "
                "content(내용) + blamer_id(신고자 account_id)토큰(header) 입니다."
)
async def create_blame(req: account.CreateBlame, current_user: Account = Depends(get_current_user), crud=Depends(get_crud)):
    await blame(req.blame_user, req.blamed_id, req.content, current_user.account_id)
    return crud.create_record(Blame, account.UploadBlame(**req.dict(), blamer_id=current_user.account_id))


@router.get(
    "/list_blame",
    name="Blame 리스트 조회",
    description="Blame 테이블의 모든 Record를 가져옵니다",
    response_model=List[account.ReadBlame],
)
def get_list(crud=Depends(get_crud)):
    return crud.get_list(Blame)


@router.delete(
    "/",
    name="Account record 삭제",
    description="입력된 id에 해당하는 Account record를 삭제합니다.",
)
async def delete_account(current_user: Account=Depends(get_current_user), crud=Depends(get_crud)):
    filter = {"account_id": current_user.account_id}
    record = crud.get_record(Account, filter)
    posts = crud.search_record(Post, filter)
    for post in posts:
        crud.patch_record(post, {"status": 3, "username": "알 수 없는 사용자"})
    crud.patch_record(record, {"available": 3})
    seller_rooms = crud.search_record(Room, {"seller_id": current_user.account_id})
    buyer_rooms = crud.search_record(Room, {"buyer_id": current_user.account_id})
    for r in seller_rooms:
        if status is not None:
            crud.patch_record(r, {"status": -1})
        else:
            crud.patch_record(r, {"status": current_user.account_id})
    for r in buyer_rooms:
        if status is not None:
            crud.patch_record(r, {"status": -1})
        else:
            crud.patch_record(r, {"status": current_user.account_id})
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return Response(status_code=HTTP_204_NO_CONTENT)
