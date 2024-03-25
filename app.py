import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging


from routers import (post, account, category, chat, photo, locker)

from core.db import Base, engine

from mangum import Mangum
import sentry_sdk

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)

fastapi_app = FastAPI(title="DangMooG", debug=True)

origins = [
    "http://127.0.0.1/",
    "http://127.0.0.1:8000/",
    "http://localhost/",
    "http://localhost:8000/"
]

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
Base.metadata.create_all(bind=engine)


@fastapi_app.get("/healthcheck")
async def health_check():
    return {"message": "OK"}


fastapi_app.include_router(post.router, prefix="/meta")
fastapi_app.include_router(account.router, prefix="/meta")
fastapi_app.include_router(category.router, prefix="/meta")
fastapi_app.include_router(chat.router, prefix="/meta")
fastapi_app.include_router(photo.router, prefix="/meta")
fastapi_app.include_router(locker.router, prefix="/meta")

# for serverless package
handler = Mangum(fastapi_app)
# 실행 명령어 디버깅용
# uvicorn app:fastapi_app --reload
# --host 0.0.0.0 --port 80
# 파이썬 코드로 실행시
# if __name__ == "__main__":
#     uvicorn.run(fastapi_app
#                 , host = "0.0.0.0"
#                 , port = 80)
