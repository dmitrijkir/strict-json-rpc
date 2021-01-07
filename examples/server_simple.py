from typing import Tuple, Union, Dict, List

from aiohttp import web
from pydantic import BaseModel
import json

from strict_json_rpc import JsonRpcServer, Depends, Router, BaseConverter, Context

router = Router()


class AioHttpConverter(BaseConverter):
    @classmethod
    async def unpack_request(cls, *args, **kwargs) -> Tuple[Union[Dict, List], Context]:
        request: web.Request = args[0]
        body = await request.json()
        return body, Context(body=body, header=dict(request.headers))

    @classmethod
    async def pack_response(cls, response: Tuple[Dict, Context]):
        body, context = response
        return web.Response(
            body=json.dumps(body), headers={"Content-Type": "application/json"}
        )

    @classmethod
    async def pack_batch_response(cls, response: List[Tuple[Dict, Context]]):
        return web.Response(
            body=json.dumps([item[0] for item in response]),
            headers={"Content-Type": "application/json"},
        )


class GetUserRequest(BaseModel):
    user_id: str


class GetUserResponse(BaseModel):
    name: str
    user_id: int


def get_last_name():
    return "Lastname"


@router.method("get_user")
async def get_user(
    request: GetUserRequest, last_name: str = Depends(get_last_name)
) -> GetUserResponse:
    return GetUserResponse(name="Dmitriy", user_id=request.user_id, last_name=last_name)


if __name__ == "__main__":
    server = JsonRpcServer(routes=[router], converter=AioHttpConverter())
    application = web.Application(debug=True)
    application.add_routes(
        [
            web.post("/jsonrpc", server.dispatch),
            web.get("/jsonrpc/schema", server.schema),
        ]
    )
    web.run_app(application)
