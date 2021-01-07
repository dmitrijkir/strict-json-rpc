import asyncio
import json
from copy import deepcopy
from inspect import signature
from typing import Optional, Any, List, Dict, Sequence, Tuple, Type, Callable, Awaitable

from .context import Context
from .converter import BaseConverter
from .dependencies import solve_dependencies, Depends
from .exceptions import BaseJsonRpcException
from .exceptions import MethodNotFoundError
from .middleware.base import BaseMiddleware
from .response import Response
from .router import Method
from .router import Router
from .serializers import BaseEncoder


class StartMiddleware(BaseMiddleware):
    """First middleware helps make chain"""

    async def dispatch(self, context: Context, call_next):
        if call_next:
            response = await call_next(context)
            return response


class EndMiddleware(BaseMiddleware):
    async def dispatch(self, context: Context, call_next):

        handler: Method = self.app.methods.get(context.method_name)

        if not handler:
            return Response(error=MethodNotFoundError())

        args = {}

        params = (context.request_data or {}).get("params", {})

        # FIXME: must check errors of validation
        if handler.strict and handler.request:
            request = handler.request(**params)

        _signature = signature(handler.f)
        for k, v in _signature.parameters.items():
            if isinstance(v.default, Depends):
                try:
                    result = solve_dependencies(
                        v.default.dependency, body=params, context=context
                    )
                except BaseJsonRpcException as error:
                    return Response(error=error)
                args.update({k: result})
            else:
                args.update({k: params.get(k)})

        if handler.strict and handler.request:
            args.update({list(_signature.parameters.keys())[0]: request})

        try:
            result = await handler.f(**args)
            return Response(body=result)
        except BaseJsonRpcException as e:
            return Response(error=e)
        except Exception as e:
            return Response(error=BaseJsonRpcException(message=str(e)))


class JsonRpcServer:
    def __init__(
        self,
        encoder: Type[json.JSONEncoder] = BaseEncoder,
        routes: Sequence[Router] = None,
        middlewares: List[Type[BaseMiddleware]] = None,
        converter: BaseConverter = BaseConverter(),
    ):
        self.methods: Dict[str, Method] = {}
        self.encoder = encoder
        self.converter = converter
        self.user_middleware: List[Type[BaseMiddleware]] = middlewares or []
        self.middleware_stack: BaseMiddleware = self.build_middleware_stack()
        self.build_route(routes or [])

    """
    Json-rpc server
    """

    def add_middleware(self, middleware):
        self.user_middleware.append(middleware)
        self.middleware_stack = self.build_middleware_stack()

    def build_middleware_stack(self) -> BaseMiddleware:
        middleware = [StartMiddleware] + self.user_middleware + [EndMiddleware]

        handler = None
        for item in reversed(middleware):
            handler = item(next_handler=handler, app=self)

        return handler

    def build_route(self, routes: Sequence[Router]):
        for route in routes:
            self.methods.update(route.methods)

    def _schema(self) -> List:
        """"""
        response = []
        for k, v in self.methods.items():
            if v.strict:
                response.append(
                    {
                        "method": k,
                        "description": v.description,
                        "request": v.request.schema() if v.request else None,
                        "response": v.response.schema(),
                    }
                )
        return response

    async def schema(self) -> object:
        """"""
        return await self.converter.pack_response((self._schema(), Context()))

    async def dispatch(self, *args, **kwargs) -> Any:
        """
        method for dispatch input request
         example:
             from aiohttp import web

             rpc_app = JsonRpcServer()

             @rpc_app.method("ping")
             async def ping(name: str):
                 return {"name": name}

             application = web.Application()
             application.add_routes([web.post("/jsonrpc", rpc_app.dispatch)])
         :param request: aiohttp Request
         :return: aiohttp Response
        """
        try:
            body, _context = await self.converter.unpack_request(*args, **kwargs)
        except:
            return

        response = None
        if type(_context.body) == list:
            response = await self.dispatch_batch(body, context=_context)
            return await self.converter.pack_batch_response(response)
        elif type(_context.body) == dict:
            response = await self.dispatch_or_notify(body, context=_context)
            return await self.converter.pack_response(response)
        if not response:
            return Response()

    async def dispatch_or_notify(
        self, jsonrpc_request: Dict[str, Any], context: Context
    ) -> Optional[Tuple[Optional[Dict], Optional[Context]]]:
        """
        The method checks, if the incoming
        rpc request or notification. If this request, handles it
        and returns the answer
        :param jsonrpc_request:
        :param context:
        :return:
        """
        # FIXME: check how depends context on bach query? maybe I shouldn't use deepcopy? just rewrite body?
        #       I think we can get problem with context and many concurrent workers
        _context = deepcopy(context)
        _context.request_data = jsonrpc_request
        _context.method_name = jsonrpc_request.get("method")

        if "id" not in jsonrpc_request:
            asyncio.create_task(
                self.middleware_stack(
                    _context,
                )
            )
            return None

        result: Response = await self.middleware_stack(
            _context
        )

        response = {"jsonrpc": "2.0", "id": jsonrpc_request.get("id")}

        if result.error:
            response["error"] = dict(result.error)
        elif result.body:
            response["result"] = result.body.dict()

        return response, _context

    async def dispatch_batch(self, body: List[dict], context: Context):
        """
        handles batch request
        :param body:
        :param context:
        :return:
        """
        results = await asyncio.gather(
            *[self.dispatch_or_notify(request, context) for request in body]
        )
        results = [x for x in results if x is not None]
        return results
