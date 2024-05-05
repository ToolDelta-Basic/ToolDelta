"""
## ToolDelta: NEMC Rental Server R-Plugin Loader ##
ToolDelta: 网易我的世界手机版 租赁服机器人式插件加载器
 - 进入ToolDelta界面:\n
    from tooldelta import client_title\n
    client_title()
 - 快速启动ToolDelta:\n
    from tooldelta import start_tool_delta\n
    start_tool_delta()
"""
from .color_print import Print
from .plugin_load.PluginGroup import Plugin
from .starter import plugin_group as plugins
from .starter import start_tool_delta, safe_jump
from .frame import Config, Utils, Frame, GameCtrl
from .launch_options import client_title

# 重定向 Builtins
Builtins = Utils