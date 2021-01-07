from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel

from .exceptions import BaseJsonRpcException


@dataclass
class Response:
    body: Optional[BaseModel] = None
    error: Optional[BaseJsonRpcException] = None
