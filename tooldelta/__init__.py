"""
## ToolDelta: NEMC Rental Server R-Plugin Loader ##
ToolDelta: 网易我的世界手机版 租赁服机器人式插件加载器
- 进入 ToolDelta 界面:\n
   ```python
   from tooldelta import client_title\n
   client_title()
   ```
- 快速启动 ToolDelta:\n
   ```python
   from tooldelta import start_tool_delta\n
   start_tool_delta()
   ```
- 快速创建插件所需库环境\n
   ```python
   from tooldelta import *
   ```
"""

from .color_print import Print
from .frame import Config, GameCtrl, ToolDelta, Utils
from .launch_options import client_title
from .plugin_load import TYPE_CHECKING
from .plugin_load.PluginGroup import Plugin
from .starter import plugin_group as plugins
from .starter import safe_jump, start_tool_delta, tooldelta

# 重定向
Builtins = Utils
Frame = ToolDelta
