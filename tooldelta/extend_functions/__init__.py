"""
内置扩展功能。

在本文件夹下编写扩展功能后需要在 __init__.py 中的 `import_functions()` 函数下添加导入。
"""

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


def restore_console_cmds():
    """恢复内置扩展提供的控制台命令。"""
    for func in registered_functions:
        func.when_console_cmd_reset()


def import_functions():
    from . import gamerule_warnings, fast_plugin_download, plugin_config
