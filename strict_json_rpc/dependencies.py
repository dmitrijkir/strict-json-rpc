from inspect import signature
from typing import Optional, Callable

from .context import Context


class Depends:
    def __init__(self, dependency: Callable, *, use_cache: bool = True):
        self.dependency = dependency
        self.use_cache = use_cache


def solve_dependencies(dependant: Callable, body: Optional[dict] = None, context: Context = None):
    args = {}
    _signature = signature(dependant)
    for k, v in _signature.parameters.items():
        if isinstance(v.default, Depends):
            sub_result = solve_dependencies(v.default.dependency, body=body, context=context)
            args.update({k: sub_result})
        else:
            if issubclass(v.annotation, Context):
                args.update({k: context})
    result = dependant(**args)
    return result
