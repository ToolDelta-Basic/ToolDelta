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
    "plugins",
    "start_tool_delta",
    "tooldelta",
]

from typing import TYPE_CHECKING

from .color_print import Print
from .frame import Config, GameCtrl, ToolDelta, Utils
from .launch_options import client_title
from .plugin_load.PluginGroup import Plugin
from .starter import plugin_group as plugins
from .starter import start_tool_delta, tooldelta

# 重定向
Builtins = Utils
Frame = ToolDelta
