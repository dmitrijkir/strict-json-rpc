from typing import Optional, Tuple, Dict, List, Union
from unittest import IsolatedAsyncioTestCase

from pydantic import BaseModel

from strict_json_rpc import BaseConverter
from strict_json_rpc import BaseJsonRpcException
from strict_json_rpc import Context
from strict_json_rpc import JsonRpcServer
from strict_json_rpc.router import Router


class ParamsConverter(BaseConverter):
    @classmethod
    async def unpack_request(cls, *args, **kwargs) -> Tuple[Union[Dict, List], Context]:
        return kwargs.get("body"), Context(body=kwargs.get("body"), header=kwargs.get("headers"))

    @classmethod
    async def pack_response(cls, response: Tuple[Dict, Context]):
        body, context = response
        return body

    @classmethod
    async def pack_batch_response(cls, response: List[Tuple[Dict, Context]]):
        return [item[0] for item in response]


class ResponseObj(BaseModel):
    name: str
    status: Optional[str]


class RequestObj(BaseModel):
    name: str


class TestError(BaseJsonRpcException):
    code: int = 2200
    message: str = "This error was rewrite by middleware"


router = Router()


class TestConverter(IsolatedAsyncioTestCase):
    async def test_converter(self):
        @router.method("test_method")
        async def method() -> ResponseObj:
            return ResponseObj(name="hi")

        request_body = {
            "id": "test1",
            "method": "test_method",
            "params": {"name": "test"},
        }
        server = JsonRpcServer(routes=[router], converter=ParamsConverter)
        resp = await server.dispatch(body=request_body, headers={})
        self.assertEqual(resp.get("result").get("name"), "hi")

    async def test_converter_batch(self):
        @router.method("test_method_2")
        async def method(request: RequestObj) -> ResponseObj:
            return ResponseObj(name=request.name)

        request_body = [
            {
                "id": "test1",
                "method": "test_method_2",
                "params": {"name": "test"},
            },
            {
                "id": "test1",
                "method": "test_method_2",
                "params": {"name": "test2"},
            },
        ]
        server = JsonRpcServer(routes=[router], converter=ParamsConverter)
        resp = await server.dispatch(body=request_body, headers={})
        self.assertEqual(resp[0].get("result", {}).get("name"), "test")
        self.assertEqual(resp[1].get("result", {}).get("name"), "test2")
