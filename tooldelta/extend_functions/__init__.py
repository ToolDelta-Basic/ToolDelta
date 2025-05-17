from typing import TYPE_CHECKING
from importlib import import_module
from .basic import ExtendFunction

if TYPE_CHECKING:
    from .. import ToolDelta

function_modules = [
    "gamerule_warnings",
]
registered_function_clss: list[type[ExtendFunction]] = []
registered_functions: list[ExtendFunction] = []


def regist_extend_function(func: type[ExtendFunction]):
    registered_function_clss.append(func)


def load_functions(frame: "ToolDelta"):
    for func_cls in registered_function_clss:
        func = func_cls(frame)
        registered_functions.append(func)


def activate_functions():
    for func in registered_functions:
        func.when_activate()


def import_functions():
    for function_module in function_modules:
        import_module(f".{function_module}", package=__package__)


import_functions()
