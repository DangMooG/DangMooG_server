from models.chat import *
from models.account import Account
from core.utils import get_crud
import ast
from dotenv import load_dotenv
load_dotenv()
def get_all_list(room_id: str):
    crud_generator = get_crud()
    crud = next(crud_generator)
    messages = crud.search_record(Message, {"room_id": room_id})
    messages = crud.patch_all(messages, {"read": 1})
    for idx, m in enumerate(messages):
        if m.is_photo:
            if m.content == "img":
                continue
            messages[idx].content = ast.literal_eval(m.content)
    return messages

ms = get_all_list("70c3e30e-73e4-4ce5-8134-10f17cd30fa1")
for ma in ms:
    print(ma.content)
