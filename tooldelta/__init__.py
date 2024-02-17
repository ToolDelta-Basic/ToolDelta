from colorama import init

# 初始化 colorama 库
init(autoreset=True)
# for installing libs in debug mode
from .basic_mods import *
from .packets import Packet_CommandOutput
from .start_tool_delta import start_tool_delta
from .start_tool_delta import plugins
from .plugin_load.PluginGroup import Plugin, PluginAPI
from .color_print import Print
from .Frame import Config,Builtins,Frame,GameCtrl
