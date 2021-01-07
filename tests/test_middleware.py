from typing import Optional
from unittest import IsolatedAsyncioTestCase

from pydantic import BaseModel

from strict_json_rpc import BaseJsonRpcException
from strict_json_rpc import Context
from strict_json_rpc import JsonRpcServer
from strict_json_rpc.middleware import BaseMiddleware
from strict_json_rpc.router import Router


class ResponseObj(BaseModel):
    name: str
    status: Optional[str]


class RequestObj(BaseModel):
    name: str


class TestError(BaseJsonRpcException):
    code: int = 2200
    message: str = "This error was rewrite by middleware"


router = Router()


class ResponseMutation(BaseMiddleware):
    async def dispatch(self, context: Context, call_next):
        result = await call_next(context)
        if result.error:
            result.error = TestError()
        return result


class TestMiddleware(IsolatedAsyncioTestCase):
    async def test_middleware(self):
        @router.method("test_method")
        async def method() -> ResponseObj:
            return ResponseObj(name="hi")

        request_body = {
            "id": "test1",
            "method": "test_method",
            "params": {"name": "test"},
        }
        context = Context(body=request_body)
        server = JsonRpcServer(routes=[router], middlewares=[ResponseMutation])
        resp, _context = await server.dispatch_or_notify(request_body, context)
        self.assertEqual(resp.get("result").get("name"), "hi")

    async def test_middleware_batch(self):
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
        context = Context(body=request_body)
        server = JsonRpcServer(routes=[router], middlewares=[ResponseMutation])
        resp = await server.dispatch_batch(request_body, context)
        self.assertEqual(resp[0][0].get("result", {}).get("name"), "test")
        self.assertEqual(resp[1][0].get("result", {}).get("name"), "test2")

    async def test_middleware_with_error(self):
        @router.method("test_method_with_error")
        async def method(request: RequestObj) -> ResponseObj:
            k = str(55 / 0)
            return ResponseObj(name=k)

        request_body = {
            "id": "test1",
            "method": "test_method_with_error",
            "params": {"name": "test"},
        }
        context = Context(body=request_body)
        server = JsonRpcServer(routes=[router], middlewares=[ResponseMutation])
        resp, _ = await server.dispatch_or_notify(request_body, context)
        self.assertEqual(
            resp.get("error").get("message"), "This error was rewrite by middleware"
        )
