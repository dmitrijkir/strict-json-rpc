from aiohttp import web
from pydantic import BaseModel

from strict_json_rpc import JsonRpcServer, Depends, Router
from strict_json_rpc.context import Context
from strict_json_rpc.middleware.base import BaseMiddleware

router = Router()


class GetUserRequest(BaseModel):
    user_id: str


class GetUserResponse(BaseModel):
    name: str


def get_last_name():
    return "kir"


@router.method("get_user")
async def get_user(
    request: GetUserRequest, last_name: str = Depends(get_last_name)
) -> GetUserResponse:
    print(last_name)
    return GetUserResponse(name="dmkir")


class TestMidle(BaseMiddleware):
    async def dispatch(self, context: Context, call_next):
        print("start mdl 1")
        response = await call_next(context)
        print("end midle 11")
        return response


class TestMidle2(BaseMiddleware):
    async def dispatch(self, context: Context, call_next):
        print("start mdl 2")
        response = await call_next(context)
        print("end midle 22")
        return response


server = JsonRpcServer(routes=[router], middlewares=[TestMidle, TestMidle2])


if __name__ == "__main__":
    application = web.Application(debug=True)
    application.add_routes(
        [
            web.post("/jsonrpc", server.dispatch),
            web.get("/jsonrpc/schema", server.schema),
        ]
    )
    web.run_app(application)
