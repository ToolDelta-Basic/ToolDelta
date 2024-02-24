from .Frame import Config, Builtins, Frame, GameCtrl
from .color_print import Print
from .plugin_load.PluginGroup import Plugin, PluginAPI
from .start_tool_delta import plugins
from .start_tool_delta import start_tool_delta
from .packets import Packet_CommandOutput
from .basic_mods import *
from colorama import init

# 初始化 colorama 库
init(autoreset=True)
