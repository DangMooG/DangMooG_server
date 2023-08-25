from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from starlette import status

from core import user_crud
from core.schema import RequestPage
from core.utils import get_db
from schemas import user

router = APIRouter(
    prefix="/user"
)


@router.post("/user_create", name="회원가입",
             description="유저 회원가입을 위한 api입니다."
                         "userid, 비밀번호, 이메일, is_super 총 4개의 input이 필요합니다."
                         "is_super는 관리자 계정의 여부입니다. 관리자 전용 암호를 입력해서 회원가입을 진행해주세요.",
                         status_code=status.HTTP_204_NO_CONTENT)
def user_create(_user_create: user.UserCreate, db: Session = Depends(get_db)):
    if _user_create.is_super == "sundaegukbap":
        _user_create.is_super = True
    else:
        _user_create.is_super = False
    user_crud.create_user(db=db, user_create=_user_create)
