from typing import TYPE_CHECKING
from .basic import ExtendFunction

# ruff: noqa F401

if TYPE_CHECKING:
    from .. import ToolDelta

registered_function_clss: list[type[ExtendFunction]] = []
registered_functions: list[ExtendFunction] = []


def regist_extend_function(func: type[ExtendFunction]):
    registered_function_clss.append(func)


def load_functions(frame: "ToolDelta"):
    import_functions()
    for func_cls in registered_function_clss:
        func = func_cls(frame)
        registered_functions.append(func)


def activate_functions():
    for func in registered_functions:
        func.when_activate()


def import_functions():
    from . import gamerule_warnings

