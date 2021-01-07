from unittest import TestCase

from strict_json_rpc.dependencies import solve_dependencies, Depends, Context


def get_last_name():
    return "Testov"


def get_name():
    return "Dmitriy"


def get_full_name(
    name: str = Depends(get_name), last_name: str = Depends(get_last_name)
):
    return f"{name} {last_name}"


def get_method_name(context: Context):
    return context.method_name


class TestDependencies(TestCase):
    def test_dep(self):
        dep = Depends(dependency=get_last_name)
        result = solve_dependencies(dep.dependency)
        self.assertEqual(result, "Testov")

    def test_dep_nested(self):
        dep = Depends(get_full_name)
        result = solve_dependencies(dep.dependency)
        self.assertEqual(result, "Dmitriy Testov")

    def test_dep_get_context(self):
        context = Context(method_name="test_method")
        dep = Depends(get_method_name)
        result = solve_dependencies(dep.dependency, context=context)
        self.assertEqual(result, context.method_name)
