from colorama import init

# 初始化 colorama 库
init(autoreset=True)
from .basic_mods import *
from .packets import Packet_CommandOutput
from .start_tool_delta import start_tool_delta
from .start_tool_delta import plugins
from .plugin_load.PluginGroup import Plugin, PluginAPI
from .color_print import Print
from .Frame import Config, Builtins, Frame, GameCtrl
