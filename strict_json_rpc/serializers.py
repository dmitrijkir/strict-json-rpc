import json
from datetime import datetime

from .exceptions import BaseJsonRpcException


class BaseEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        elif isinstance(o, BaseJsonRpcException):
            return dict(code=o.code, message=o.message, data=o.data)
