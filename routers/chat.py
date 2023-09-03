from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from starlette.responses import Response
from starlette.status import HTTP_204_NO_CONTENT

from core.schema import RequestPage
from core.utils import get_crud
from models.chat import Chat
from schemas import chat
from routers.account import get_current_user
from models.account import Account

from typing import List, Dict, Set

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)
"""
Chat table CRUD
"""


@router.post(
    "/", name="Chat record 생성", description="Chat 테이블에 Record 생성합니다", response_model=chat.RecordChat
)
async def create_post(req: chat.RecordChat, crud=Depends(get_crud), current_user: Account = Depends(get_current_user)):
    if req.sender_id == current_user.account_id:
        raise HTTPException(status_code=401, detail="Unauthorized request")
    return crud.create_record(Chat, req)


@router.post(
    "/page-list",
    name="Chat Page 리스트 조회",
    description="Chat 테이블의 페이지별 Record list 가져오는 API입니다.\
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
    return crud.paging_record(Chat, req)


@router.post(
    "/search",
    name="Chat 테이블에서 입력한 조건들에 부합하는 record 를 반환하는 API",
    description="body에 원하는 조건들을 입력하면 and로 필터 결과 리스트를 반환합니다\
        조건값이 str 일 경우 그 문자열을 포함하는 모든 record를 반환합니다.\
        조건값이 int,float 일 경우 그 값과 동일한 record만 반환합니다.\
        조건값이 list 경우 list 항목을 포함하는 모든 record를 반환합니다.\
    ",
    response_model=List[chat.ReadChat],
)
async def search_post(filters: chat.PatchChat, crud=Depends(get_crud)):
    return crud.search_record(Chat, filters)


@router.get(
    "/list",
    name="Chat 리스트 조회",
    description="Chat 테이블의 모든 Record를 가져옵니다",
    response_model=List[chat.ReadChat],
)
def get_list(crud=Depends(get_crud)):
    return crud.get_list(Chat)


@router.get(
    "/{id}",
    name="Chat record 가져오기",
    description="입력된 chat_id를 키로 해당하는 Record 반환합니다",
    response_model=chat.ReadChat,
)
def read_post(id: int, crud=Depends(get_crud)):
    filter = {"chat_id": id}
    db_record = crud.get_record(Chat, filter)
    if db_record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return db_record


@router.get(
    "/{post_id}",
    name="Chat room number record 가져오기",
    description="입력된 post id를 키로 chat room number를 반환합니다",
    response_model=chat.ReadChat,
)
def read_post(post_id: int, crud=Depends(get_crud), current_user: Account = Depends(get_current_user)):
    filter = {"post_id": post_id,
              "account_id": current_user.account_id}
    db_record = crud.get_record(Chat, filter)
    if db_record is None:
        return {"room_id": str(post_id) + str(current_user.account_id)}
    return {"room_id": str(post_id) + str(current_user.account_id)}


@router.patch(
    "/{id}",
    name="Chat 한 record 일부 내용 수정",
    description="수정하고자 하는 id의 record 일부 수정, record가 존재하지 않을시엔 404 오류 메시지반환합니다",
    response_model=chat.ReadChat,
)
async def update_post_sub(req: chat.PatchChat, id: int, crud=Depends(get_crud), current_user: Account = Depends(get_current_user)):
    if req.sender_id == current_user.account_id:
        raise HTTPException(status_code=401, detail="Unauthorized request")
    filter = {"chat_id": id}
    db_record = crud.get_record(Chat, filter)
    if db_record is None:
        raise HTTPException(status_code=404, detail="Record not found")

    return crud.patch_record(db_record, req)


@router.delete(
    "/{id}",
    name="Chat record 삭제",
    description="입력된 id에 해당하는 record를 삭제합니다.",
)
async def delete_post(id: int, crud=Depends(get_crud), current_user: Account = Depends(get_current_user)):
    filter = {"chat_id": id}
    db_record = crud.get_record(Chat, filter)
    if db_record.sender_id == current_user.account_id:
        raise HTTPException(status_code=401, detail="Unauthorized request")
    db_api = crud.delete_record(Chat, filter)
    if db_api != 1:
        raise HTTPException(status_code=404, detail="Record not found")
    return Response(status_code=HTTP_204_NO_CONTENT)


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
