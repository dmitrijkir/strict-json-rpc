from unittest import TestCase

from pydantic import BaseModel

from strict_json_rpc.exceptions import (
    MustAnnotateReturnObject,
    NotValidArgument,
    MethodNameNotValid,
)
from strict_json_rpc.router import Router, Method


class ResponseObj(BaseModel):
    name: str


class RequestObj(BaseModel):
    user_id: int


class TestRouter(TestCase):
    def test_add_valid_method(self):

        router = Router()

        @router.method("test_method")
        def method() -> ResponseObj:
            return ResponseObj(name="hi")

        method_obj = Method(
            description=None,
            name="test_method",
            request=None,
            response=ResponseObj,
            strict=True,
            f=method,
        )

        self.assertEqual(router.methods["test_method"], method_obj)

    def test_add_method_without_name(self):

        router = Router()

        try:

            @router.method("")
            def method() -> ResponseObj:
                return ResponseObj(name="hi")

        except MethodNameNotValid as error:
            self.assertEqual(error.code, MethodNameNotValid.code)

    def test_add_method_without_response_annotation(self):

        router = Router()

        try:

            @router.method("test_method")
            def method():
                return ResponseObj(name="hi")

        except MustAnnotateReturnObject as error:
            self.assertEqual(error.code, MustAnnotateReturnObject.code)

    def test_add_method_incorrect_input_param(self):
        """First argument must be a subclass of pydantic model"""

        router = Router()

        try:

            @router.method("test_method")
            def method(name: str) -> ResponseObj:
                return ResponseObj(name=name)

        except NotValidArgument as error:
            self.assertEqual(error.code, NotValidArgument.code)

    def test_add_method_incorrect_input_param_second_arg_not_depends(self):
        """after first argument must be a Depends"""

        router = Router()

        try:

            @router.method("test_method")
            def method(request: RequestObj, name: str) -> ResponseObj:
                return ResponseObj(name=name)

        except NotValidArgument as error:
            self.assertEqual(error.code, NotValidArgument.code)
            self.assertEqual(error.message, "1 argument must be a Depends")
