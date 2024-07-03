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

from .color_print import Print  # noqa: F401
from .frame import Config, GameCtrl, ToolDelta, Utils  # noqa: F401
from .launch_options import client_title  # noqa: F401
from typing import TYPE_CHECKING  # noqa: F401
from .plugin_load.PluginGroup import Plugin  # noqa: F401
from .starter import plugin_group as plugins  # noqa: F401
from .starter import safe_jump, start_tool_delta, tooldelta  # noqa: F401

# 重定向
Builtins = Utils
Frame = ToolDelta
