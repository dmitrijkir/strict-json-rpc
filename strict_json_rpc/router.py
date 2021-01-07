from dataclasses import dataclass
from inspect import signature
from typing import Optional, Dict, Type, Callable

from pydantic import BaseModel

from .dependencies import Depends
from .exceptions import MustAnnotateReturnObject, NotValidArgument, MethodNameNotValid
from .logger import logger


@dataclass
class Method:
    name: str
    strict: bool
    f: Callable
    description: Optional[str] = None
    request: Optional[Type[BaseModel]] = None
    response: Optional[Type[BaseModel]] = None


class Router:
    methods: Dict[str, Method] = {}

    def __init__(self):
        self.methods: Dict[str, Method] = {}

    def method(self, name: str, strict: bool = True):
        """
        Wrap func for making json-rpc view
        :param name: json-rpc method
        :param strict: strict validation with pydantic models
        :return:
        """

        def decorator(f):
            nonlocal name
            nonlocal strict

            if not name:
                logger.error("method name not valid for json-rpc view")
                raise MethodNameNotValid()

            if name in self.methods:
                logger.warning(
                    f"Duplicate json-rpc method {name}, some view may work incorrectly"
                )
                raise MethodNameNotValid(message=f"Duplicate json-rpc method {name}")

            # if strict validation we must gen schema of data
            _annotation = Method(name=name, f=f, strict=strict)

            if strict:
                _signature = signature(f)

                if not issubclass(_signature.return_annotation, BaseModel):
                    raise MustAnnotateReturnObject()

                for ind, (k, v) in enumerate(_signature.parameters.items()):
                    if ind == 0 and not isinstance(v.default, Depends):
                        if not issubclass(v.annotation, BaseModel):
                            raise NotValidArgument(
                                message="First argument must be a subclass of pydantic model"
                            )
                        _annotation.request = v.annotation
                    else:
                        if not isinstance(v.default, Depends):
                            raise NotValidArgument(
                                message=f"{ind} argument must be a Depends"
                            )

                _annotation.response = _signature.return_annotation
                _annotation.description = f.__doc__

            self.methods[name] = _annotation

            return f

        return decorator
