from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, File
from starlette.responses import Response
from starlette.status import HTTP_204_NO_CONTENT

from core.schema import RequestPage
from core.utils import get_crud
from models.chat import *
from schemas import chat, chat_photo
from routers.account import get_current_user
from routers.photo import upload_file
from models.account import Account
from models.photo import ChatPhoto
from models.post import Post

from typing import List, Dict, Set

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)
"""
Chat table CRUD
"""


@router.post(
    "/create_post_chat_room", name="chat room 조회", description="채팅방의 Websocket 접속을 위한 방의 UUID를 가져옵니다.\n\n"
                                                       "본인임을 인증하기 위해서 토큰이 필요하고, 추가로 접근하고자 하는 게시물의 post id를 "
                                                       "같이 담아서 보내야 합니다.\n\n"
                                                               "만약 기존에 방이 존재하다면 기존에 생성된 채팅방의 room_id를 보냅니다.",
)
async def get_chatroom(req: chat.RoomNumber, crud=Depends(get_crud), current_user: Account = Depends(get_current_user)):
    ifroom = crud.search_record(Room, {"post_id": req.post_id, "buyer_id": current_user.account_id})
    if ifroom:
        return {"room_id": ifroom[0].room_id}
    seller = crud.search_record(Account, {"username": crud.get_record(Post, {"post_id": req.post_id}).username})
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
    messages = crud.search_record(Message, {"room_id": room_id, "read": 0})
    for m in messages:
        crud.patch_record(m, {"read": 1})  # 읽음 처리
        m.read = 1
    return messages


@router.get(
    "/all/{room_id}",
    name="채팅방에서 모든 메시지 가져오기",
    description="한 채팅방의 모든 메시지를 가져옵니다.\n\n"
                "가져옴과 동시에 읽음처리가 진행됩니다.",
    response_model=List[chat.RecordChat],
)
def get_all_list(room_id: str, crud=Depends(get_crud)):
    messages = crud.search_record(Message, {"room_id": room_id, "read": 0})
    for m in messages:
        if m.read == 0:
            crud.patch_record(m, {"read": 1})  # 읽음 처리
            m.read = 1
    return messages


@router.get(
    "/{room_id}",
    name="채팅방 정보 가져오기",
    description="입력된 room_id를 키로 해당하는 채팅방의 정보를 반환합니다",
    response_model=chat.Readroom,
)
def read_post(room_id: str, current_user: Account = Depends(get_current_user), crud=Depends(get_crud)):
    filter = {"room_id": room_id}
    db_record = crud.get_record(Room, filter)
    if db_record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    if db_record.buyer_id == current_user.account_id:
        from_buyer = True
    else:
        from_buyer = False

    return chat.Readroom(post_id=db_record.post_id, iam_buyer=from_buyer)


@router.post(
    "/my_opponents",
    name="나의 채팅방 별 상대 이름 가져오기",
    description="채팅방 UUID리스트를 보내면, 각 UUID에 해당하는 상대방의 닉내임의 리스트를 반환합니다.\n\n"
                "자신의 account id를 보내는 것이 아닌 헤더에 로그인 토큰을 보내야 합니다.",
    response_model=chat.OppoName
)
def get_opponents_name(req: chat.OppoRoom, current_user: Account = Depends(get_current_user), crud=Depends(get_crud)):
    res = []
    for room in req.rooms:
        temp: Room = crud.get_record(Room, {"room_id": room})
        if current_user.account_id == temp.buyer_id:
            seller = crud.get_record(Account, {Account, {"account_id": temp.seller_id}})
            res.append(seller.username)
        else:
            buyer = crud.get_record(Account, {Account, {"account_id": temp.buyer_id}})
            res.append(buyer.username)

    return chat.OppoName(usernames=res)


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
    count = []

    for room in req.rooms:
        last: Message = crud.search_record(Message, {"room_id": room})[0]
        lasts.append(last.content)
        times.append(last.create_time)
        unread: List[Message] = crud.search_record(Message, {"room_id": room, "read": 0})
        info: Room = crud.get_record(Room, {"room_id": room})
        if info.buyer_id == current_user.account_id:
            from_buyer = True
        else:
            from_buyer = False

        if unread[0].is_from_buyer:
            if not from_buyer:
                count += len(unread)
        else:
            if from_buyer:
                count += len(unread)

        count.append(count)

    return chat.RoomStatus(lasts=lasts, update_times=times, counts=count)


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
        res.append(r1.room_id)
    for r2 in rooms_buy:
        res.append(r2.room_id)

    return chat.RoomIDs(room_ids=res)


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room: str):
        await websocket.accept()
        if room in self.active_connections:
            self.active_connections[room].add(websocket)
        else:
            self.active_connections[room] = {websocket}

    def disconnect(self, websocket: WebSocket, room: str):
        self.active_connections[room].remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str, room: str):
        for connection in self.active_connections[room]:
            await connection.send_text(message)


manager = ConnectionManager()


@router.websocket("/ws/{room_name}")
async def websocket_endpoint(websocket: WebSocket, room_name: str):
    await manager.connect(websocket, room_name)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(data, room_name)
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_name)
        await manager.broadcast(f"Client left the chat room: {room_name}", room_name)
