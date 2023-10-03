from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import (post, account, category, chat, photo, locker)

from core.db import Base, engine

fastapi_app = FastAPI(title="DangMooG", debug=True)

origins = [
    "http://127.0.0.1/",
    "http://127.0.0.1:8000/",
    "http://localhost/",
    "http://localhost:8000/",
    "https://port-0-dangmoog-api-server-p8xrq2mlfc80j33.sel3.cloudtype.app/",
    "https://port-0-dangmoog-api-server-p8xrq2mlfc80j33.sel3.cloudtype.app:443/",
    "https://port-0-dangmoog-api-server-p8xrq2mlfc80j33.sel3.cloudtype.app:8000/"
]

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
Base.metadata.create_all(bind=engine)


fastapi_app.include_router(post.router, prefix="/meta")
fastapi_app.include_router(account.router, prefix="/meta")
fastapi_app.include_router(category.router, prefix="/meta")
fastapi_app.include_router(chat.router, prefix="/meta")
fastapi_app.include_router(photo.router, prefix="/meta")
fastapi_app.include_router(locker.router, prefix="/meta")


# 실행 명령어
# uvicorn app:fastapi_app --reload
# --host 0.0.0.0 --port 80
# 파이썬 코드로 실행시
# if __name__ == "__main__":
#     uvicorn.run(fastapi_app
#                 , host = "0.0.0.0"
#                 , port = 80)
