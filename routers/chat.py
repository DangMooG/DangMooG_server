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
        return {"room_id": ifroom[1].room_id}
    seller = crud.search_record(Account, {"username": crud.get_record(Post, {"post_id": req.post_id}).username})
    chat_room = crud.create_record(Room, chat.RoomCreate(**req.dict(), seller_id=seller[0].account_id, buyer_id=current_user.account_id, status=0))
    return {"room_id": chat_room.room_id}




@router.get(
    "/list",
    name="Chat 리스트 조회",
    description="Chat 테이블의 모든 Record를 가져옵니다",
    response_model=List[chat.ReadChat],
)
def get_list(crud=Depends(get_crud)):
    return crud.get_list(Chat)


@router.get(
    "/{room_id}",
    name="채팅방 정보 가져오기",
    description="입력된 room_id를 키로 해당하는 채팅방의 정보를 반환합니다",
    response_model=chat.Readroom,
)
def read_post(room_id: int, crud=Depends(get_crud)):
    filter = {"room_id": room_id}
    db_record = crud.get_record(Room, filter)
    if db_record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return db_record



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
