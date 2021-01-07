from typing import Union, Tuple, Dict, List
from .context import Context


class BaseConverter:
    @classmethod
    async def unpack_request(cls, *args, **kwargs) -> Tuple[Union[Dict, List], Context]:
        raise NotImplementedError()

    @classmethod
    async def pack_response(cls, response: Tuple[Union[Dict, List], Context]):
        raise NotImplementedError()

    @classmethod
    async def pack_batch_response(cls, response: List[Tuple[Union[Dict, List], Context]]):
        raise NotImplementedError()
