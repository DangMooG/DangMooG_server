from fastapi import FastAPI, Depends

from schemas.post import BasePost

fastapi_app = FastAPI(title="DangMooG", debug=True)


@fastapi_app.post("/test")
def test(req: BasePost):

    return req
