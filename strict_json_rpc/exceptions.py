class BaseJsonRpcException(Exception, object):
    code: int = 0
    message: str = ""
    data: dict = {}

    def __init__(self, code: int = None, message: str = None, data: dict = None):
        if code:
            self.code = code
        if message:
            self.message = message
        if data:
            self.data = data

    def __iter__(self):
        for k, v in self.__class__.__dict__.items():
            if not str(k).startswith("__"):
                yield k, v


class MethodNotFoundError(BaseJsonRpcException):
    code: int = -32601
    message: str = "Method not found"


class InvalidParamsError(BaseJsonRpcException):
    code: int = -32602
    message: str = "Invalid params"


class RPCClientNotFoundError(BaseJsonRpcException):
    code: int = -33000
    message: str = "Client settings not found"


class WrongRpcUrlError(BaseJsonRpcException):
    code: int = -33001
    message: str = "Server url is incorrect"


class MustAnnotateReturnObject(BaseJsonRpcException):
    code: int = 20201
    message: str = "return object must be a subclass of pydantic model"


class NotValidArgument(BaseJsonRpcException):
    code: int = 20202
    message: str = "Argument not valid"


class MethodNameNotValid(BaseJsonRpcException):
    code: int = 20203
    message: str = "method name not valid"
