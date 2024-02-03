import ast
import json

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from starlette.responses import Response
from starlette.status import HTTP_204_NO_CONTENT

from core.schema import RequestPage
from core.utils import get_crud
from models.chat import *
from schemas import chat, photo
from routers.account import get_current_user
from routers.photo import upload_file
from models.account import Account
from models.photo import MPhoto
from models.post import Post

from typing import List, Dict, Set, Optional

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)
"""
Chat table CRUD
"""


@router.post(
    "/photo_chat", name="사진 보내기 전용 채팅", description="Message 테이블에 사진 함께 Record를 생성합니다\n\n"
                                                                 "들어갈 변수들은 쿼리(query)"
                                                                 "형식으로 작성되어야 합니다.\n\n"
                                                                 "Request Body에 사진 파일들을 담으면 됩니다.",
    response_model=chat.RecordChat
)
async def create_with_photo(files: List[UploadFile], req: photo.MPhotoStart = Depends(), crud=Depends(get_crud), current_user: Account = Depends(get_current_user)):
    room_information = crud.search_record(Room, {"room_id": req.room_id})[0]
    if room_information.buyer_id == current_user.account_id:
        is_from_buyer = 1
    else:
        is_from_buyer = 0
    temp_chat: Message = crud.create_record(Message, chat.Message(
        room_id=req.room_id,
        is_from_buyer=is_from_buyer,
        is_photo=1,
        content="img",
        read=0
    ))
    update_content = []
    for idx, file in enumerate(files):
        url = await upload_file(file, "message")
        temp_photo = photo.MPhotoUpload(
            url=url,
            message_id=temp_chat.message_id,
            account_id=current_user.account_id
        )
        crud.create_record(MPhoto, temp_photo)
        update_content.append(url)
    temp_chat = crud.patch_record(temp_chat, {"content": json.dumps(update_content)})
    return temp_chat


@router.post(
    "/create_post_chat_room", name="chat room 조회", description="채팅방의 socket 접속을 위한 방의 UUID를 가져옵니다.\n\n"
                                                       "본인임을 인증하기 위해서 토큰이 필요하고, 추가로 접근하고자 하는 게시물의 post id를 "
                                                       "같이 담아서 보내야 합니다.\n\n"
                                                               "만약 기존에 방이 존재하다면 기존에 생성된 채팅방의 room_id를 보냅니다.",
)
async def get_chatroom(req: chat.RoomNumber, crud=Depends(get_crud), current_user: Account = Depends(get_current_user)):
    ifroom = crud.search_record(Room, {"post_id": req.post_id, "buyer_id": current_user.account_id})
    if ifroom:
        return {"room_id": ifroom[0].room_id}
    seller = crud.search_record(Account, {"account_id": crud.get_record(Post, {"post_id": req.post_id}).account_id})
    chat_room = crud.create_record(Room, chat.RoomCreate(**req.dict(), seller_id=seller[0].account_id, buyer_id=current_user.account_id, status=0))
    return {"room_id": chat_room.room_id}


@router.get(
    "/unread/{room_id}",
    name="채팅방에서 안읽은 메시지만 가져오기 + 읽음 처리",
    description="한 채팅방의 않읽은 메시지를 가져옵니다\n\n"
                "가져옴과 동시에 읽음처리가 진행됩니다.",
    response_model=List[chat.RecordChat],
)
def get_unread_list(room_id: str, crud=Depends(get_crud)):
    messages: List[chat.RecordChat] = crud.search_record(Message, {"room_id": room_id, "read": 0})
    for m in messages:
        crud.patch_record(m, {"read": 1})  # 읽음 처리
        m.read = 1
        if m.is_photo:
            m.content = ast.literal_eval(m.content)
    return messages


@router.get(
    "/all/{room_id}",
    name="채팅방에서 모든 메시지 가져오기",
    description="한 채팅방의 모든 메시지를 가져옵니다.\n\n"
                "가져옴과 동시에 읽음처리가 진행됩니다.",
    response_model=List[chat.RecordChat],
)
def get_all_list(room_id: str, crud=Depends(get_crud)):
    messages: List[Message] = crud.search_record(Message, {"room_id": room_id})
    for idx, m in enumerate(messages):
        if m.read == 0:
            crud.patch_record(m, {"read": 1})  # 읽음 처리
            m.read = 1
        if m.is_photo:
            print(m.content, type(m.content))
            messages[idx].content = ast.literal_eval(m.content)
    return messages


@router.post(
    "/room_info",
    name="채팅방 정보 가져오기",
    description="입력된 room_id 리스트를 받아서 각각의 키로 해당하는 채팅방의 정보를 반환합니다 \n\n"
                "정보는 해당 채팅방의 post_id의 리스트와 iam_buyer 내가 구매자인지 판단하는 bool 리스트 입니다.",
    response_model=chat.Readroom,
)
def read_post(req: chat.OppoRoom, current_user: Account = Depends(get_current_user), crud=Depends(get_crud)):
    ids = []
    iams = []
    repr_photos = []
    for room in req.rooms:
        temp: Room = crud.get_record(Room, {"room_id": room})
        if temp is None:
            raise HTTPException(status_code=404, detail="Record not found room")
        if temp.buyer_id == current_user.account_id:
            iams.append(True)
        else:
            iams.append(False)
        ids.append(temp.post_id)

        temp_post: Post = crud.get_record(Post, {"post_id": temp.post_id})
        if temp_post is None:
            raise HTTPException(status_code=404, detail="Record not found on post")
        if temp_post.representative_photo_id:
            repr_photos.append(temp_post.representative_photo_id)
        else:
            repr_photos.append(0)

    return chat.Readroom(post_id=ids, iam_buyer=iams, repr_photo_id=repr_photos)


@router.post(
    "/my_opponents",
    name="나의 채팅방 별 상대 이름 가져오기",
    description="채팅방 UUID리스트를 보내면, 각 UUID에 해당하는 상대방의 닉내임의 리스트를 반환합니다.\n\n"
                "자신의 account id를 보내는 것이 아닌 헤더에 로그인 토큰을 보내야 합니다.",
    response_model=chat.OppoName
)
def get_opponents_name(req: chat.OppoRoom, current_user: Account = Depends(get_current_user), crud=Depends(get_crud)):
    res = []
    profiles = []
    for room in req.rooms:
        temp: Room = crud.get_record(Room, {"room_id": room})
        if current_user.account_id == temp.buyer_id:
            seller = crud.get_record(Account, {"account_id": temp.seller_id})
            res.append(seller.username)
            if seller.profile_url:
                profiles.append(seller.profile_url)
            else:
                profiles.append(None)
        else:
            buyer = crud.get_record(Account, {"account_id": temp.buyer_id})
            res.append(buyer.username)
            if buyer.profile_url:
                profiles.append(buyer.profile_url)
            else:
                profiles.append(None)

    return chat.OppoName(usernames=res, profiles=profiles)


@router.post(
    "/my_room_status",
    name="나의 채팅방 별 마지막 채팅과 않읽은 채팅의 개수 불러오기",
    description="채팅방 UUID리스트를 보내면, 각 UUID에 해당하는 채팅방의 마지막 채팅과과 얼마나 채팅을 읽어야 하는 지 알려줍니다.\n\n"
                "자신의 account id를 보내는 것이 아닌 헤더에 로그인 토큰을 보내야 합니다. \n\n"
                "입력 - 채팅방 UUID 리스트, 출력 - lasts: 각 리스트 순번에 맞는 마지막 메시지 목록, counts: 각 리스트 순번에 맞는 읽어야 하는 메지시 수",
    response_model=chat.RoomStatus
)
def get_room_status(req: chat.OppoRoom, current_user: Account = Depends(get_current_user), crud=Depends(get_crud)):
    lasts = []
    times = []
    counts = []

    for room in req.rooms:
        count = 0
        last: Message = crud.search_record(Message, {"room_id": room})
        if last:
            if last[-1].is_photo:
                lasts.append(ast.literal_eval(last[-1].content))
            else:
                lasts.append(last[-1].content)
            times.append(last[-1].create_time)
        else:
            lasts.append(None)
            times.append(None)

        unread: List[Message] = crud.search_record(Message, {"room_id": room, "read": 0})
        info: Room = crud.get_record(Room, {"room_id": room})

        if info.buyer_id == current_user.account_id:
            from_buyer = True
        else:
            from_buyer = False

        if unread:
            if unread[0].is_from_buyer:
                if not from_buyer:
                    count += len(unread)
            else:
                if from_buyer:
                    count += len(unread)

        counts.append(count)

    return chat.RoomStatus(last_messages=lasts, update_times=times, counts=counts)


@router.post(
    "/my_rooms",
    name="나의 채팅방 UUID 가져오기",
    description="Header에 JWT 토큰을 담아서 보내면, 자신이 속해있는 채팅방의 UUID를 불러옵니다.\n\n"
                "나간 처리된 채팅방은 불러 오지 않도록 설계되었습니다.",
    response_model=chat.RoomIDs
)
def get_my_room_ids(current_user: Account = Depends(get_current_user), crud=Depends(get_crud)):
    res = []
    rooms_sell = crud.search_record(Room, {"seller_id": current_user.account_id})
    rooms_buy = crud.search_record(Room, {"buyer_id": current_user.account_id})

    for r1 in rooms_sell:
        if r1.status == current_user.account_id or r1.status == -1:
            continue
        res.append(r1.room_id)
    for r2 in rooms_buy:
        if r2.status == current_user.account_id or r2.status == -1:
            continue
        res.append(r2.room_id)

    return chat.RoomIDs(room_ids=res)

