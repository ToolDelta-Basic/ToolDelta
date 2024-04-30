"启动页面"
import os
import signal
import traceback
from .color_print import Print
from .starter import start_tool_delta
from .frame import Frame
from .plugin_manager import plugin_manager
from .plugin_market import market
from .sys_args import sys_args_to_dict, print_help


def signal_handler(*_) -> None:
    """排除信号中断"""
    return Print.print_war("ToolDelta 已忽略信号中断")


signal.signal(signal.SIGINT, signal_handler)


def client_title() -> None:
    "选择启动模式"
    try:
        if "h" in sys_args_to_dict() or "help" in sys_args_to_dict():
            print_help()
            os._exit(0)
        launch_mode = sys_args_to_dict()
        if launch_mode.get("l"):
            if not isinstance(launch_mode["l"], str):
                raise ValueError("启动模式参数不合法")
            r = launch_mode["l"]
        else:
            Print.clean_print("§a请选择启动模式§6(使用启动参数 -l <启动模式> 可以跳过该页面):")
            Print.clean_print("1 - §b启动 ToolDelta")
            Print.clean_print("2 - §d打开 ToolDelta 插件管理器")
            Print.clean_print("3 - §d打开 ToolDelta 插件市场")
            Print.clean_print("4 - §a修改 ToolDelta 启动配置")
            r = input("请选择:").strip()
        match r:
            case "1":
                start_tool_delta()
            case "2":
                plugin_manager.manage_plugins()
            case "3":
                market.enter_plugin_market()
            case "4":
                Frame.change_config()
            case _:
                Print.clean_print("§c不合法的模式: " + r)
        os._exit(0)
    except EOFError:
        pass
    except Exception:
        Print.print_err("ToolDelta 运行过程中出现问题: " + traceback.format_exc())
