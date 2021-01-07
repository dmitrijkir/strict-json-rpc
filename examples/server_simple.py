from aiohttp import web
from pydantic import BaseModel

from strict_json_rpc import JsonRpcServer, Depends

server = JsonRpcServer()


class GetUserRequest(BaseModel):
    user_id: str


class GetUserResponse(BaseModel):
    name: str


def get_last_name():
    return "kir"


@server.method("get_user")
async def get_user(
    request: GetUserRequest, last_name: str = Depends(get_last_name)
) -> GetUserResponse:
    print(last_name)
    return GetUserResponse(name="dmkir")


if __name__ == "__main__":
    application = web.Application(debug=True)
    application.add_routes(
        [
            web.post("/jsonrpc", server.dispatch),
            web.get("/jsonrpc/schema", server.schema),
        ]
    )
    web.run_app(application)
