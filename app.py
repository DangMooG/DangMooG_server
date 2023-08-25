from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import (post)

from core.db import Base, engine

fastapi_app = FastAPI(title="DangMooG", debug=True)

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
Base.metadata.create_all(bind=engine)


fastapi_app.include_router(post.router, prefix="/meta")

# 실행 디렉토리
# /Users/saewonkye/Workspace/api_metadata/

# 실행 명령어
# uvicorn app.app:fastapi_app --host 0.0.0.0 --port 80 --reload

# 파이썬 코드로 실행시
# if __name__ == "__main__":
#     uvicorn.run(fastapi_app
#                 , host = "0.0.0.0"
#                 , port = 80)
