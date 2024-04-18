"启动选项"
import os
import signal
from .color_print import Print
from .starter import start_tool_delta
from .plugin_manager import plugin_manager
from .plugin_market import market
from .sys_args import sys_args_to_dict


def signal_handler(*_) -> None:
    """排除信号中断"""
    return Print.print_war("ToolDelta 已忽略信号中断")


signal.signal(signal.SIGINT, signal_handler)


def client_title() -> None:
    "选择启动模式"
    launch_mode = sys_args_to_dict()
    if launch_mode.get("l"):
        if not isinstance(launch_mode["l"], str):
            raise ValueError("启动模式参数不合法")
        r = launch_mode["l"]
    else:
        Print.clean_print("§b请选择启动模式(使用启动参数 -l <启动模式> 可以跳过该页面):")
        Print.clean_print("1 - 启动 ToolDelta")
        Print.clean_print("2 - 打开 ToolDelta 插件管理器")
        Print.clean_print("3 - 打开 ToolDelta 插件市场")
        r = input("请选择:").strip()
    match r:
        case "1":
            start_tool_delta()
        case "2":
            plugin_manager.manage_plugins()
        case "3":
            market.enter_plugin_market()
        case _:
            Print.clean_print("§c不合法的模式: " + r)
    os._exit(0)
