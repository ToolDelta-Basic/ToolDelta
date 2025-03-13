r"""
# ToolDelta: NEMC Rental Server R-Plugin Loader

网易我的世界手机版 租赁服机器人式插件加载器

- 进入 ToolDelta 界面:

    ```python
    from tooldelta import client_title

    client_title()
    ```
- 快速启动 ToolDelta:

    ```python
    from tooldelta import start_tool_delta

    start_tool_delta()
    ```
- 快速创建插件所需库环境

    ```python
    from tooldelta import *
    ```
"""

__all__ = [
    "TYPE_CHECKING",
    "Builtins",
    "Config",
    "Frame",
    "GameCtrl",
    "Plugin",
    "Print",
    "ToolDelta",
    "ToolDelta",
    "client_title",
    "start_tool_delta",
    "tooldelta",
]

from typing import TYPE_CHECKING

from . import utils
from .frame import GameCtrl, ToolDelta
from .internal.types import Player, Chat, FrameExit, InternalBroadcast
from .launch_options import client_title
from .plugin_load.classic_plugin import Plugin, plugin_entry
from .starter import start_tool_delta, tooldelta
from .utils import cfg, fmts, Utils
from .version import get_tool_delta_version, check_tooldelta_version

# 重定向
Builtins = Utils
Config = cfg
Frame = ToolDelta
Print = fmts

__all__ = [
    "TYPE_CHECKING",
    "Builtins",
    "Chat",
    "Config",
    "Frame",
    "FrameExit",
    "GameCtrl",
    "InternalBroadcast",
    "Player",
    "Plugin",
    "Print",
    "ToolDelta",
    "ToolDelta",
    "check_tooldelta_version",
    "client_title",
    "fmts",
    "get_tool_delta_version",
    "plugin_entry",
    "start_tool_delta",
    "tooldelta",
    "utils"
]
