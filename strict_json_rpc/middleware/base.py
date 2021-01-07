from ..context import Context
from ..response import Response
from typing import Callable, Coroutine, Awaitable, Type, Optional

# CallNextType = Coroutine[[Context, Callable], Response]
CallNextType = Callable[[Context, Callable], Awaitable[Response]]


class BaseMiddleware:
    def __init__(self, next_handler: "BaseMiddleware" = None, app=None):
        self.next_handler: Optional[BaseMiddleware] = next_handler
        self.app = app

    async def dispatch(self, context: Context, call_next: "BaseMiddleware") -> Response:
        raise NotImplementedError()

    async def __call__(self, context: Context) -> Response:
        if self.next_handler:
            response = await self.next_handler.dispatch(context, self.next_handler)
        return response
        # return
