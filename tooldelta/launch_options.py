"启动页面"

import signal
import os
import time
import traceback

from .color_print import Print
from .constants import TOOLDELTA_LOGO
from .frame import ToolDelta
from .plugin_manager import plugin_manager
from .plugin_market import market
from .starter import start_tool_delta
from .get_tool_delta_version import get_tool_delta_version
from .sys_args import print_help, sys_args_to_dict


def signal_handler(*_) -> None:
    """排除信号中断"""
    ...


signal.signal(signal.SIGINT, signal_handler)


def client_title() -> None:
    """选择启动模式"""
    try:
        if "h" in sys_args_to_dict() or "help" in sys_args_to_dict():
            print_help()
            return
        elif "v" in sys_args_to_dict() or "version" in sys_args_to_dict():
            print(".".join(str(i) for i in get_tool_delta_version()))
            return
        is_faststart = os.path.isfile("快速启动.sig")
        launch_mode = sys_args_to_dict()
        if launch_mode.get("l"):
            if not isinstance(launch_mode["l"], str):
                raise ValueError("启动模式参数不合法")
            r = launch_mode["l"]
        elif is_faststart:
            Print.clean_print("§a快速启动功能已打开, 将跳过选择界面")
            Print.clean_print("删除本地的 §f快速启动.sig§r 文件即可取消快速启动功能")
            time.sleep(1.5)
            start_tool_delta()
            return
        else:
            Print.clean_print(TOOLDELTA_LOGO)
            Print.clean_print(
                "§a请选择启动模式§6(使用启动参数 -l <启动模式> 可以跳过该页面):"
            )
            Print.clean_print("1 - §b启动 ToolDelta")
            Print.clean_print("2 - §d打开 ToolDelta 插件管理器")
            Print.clean_print("3 - §d打开 ToolDelta 插件市场")
            Print.clean_print("4 - §a修改 ToolDelta 启动配置")
            Print.clean_print("5 - §c开启 ToolDelta 直接启动模式")
            r = input("请选择：").strip()
        match r:
            case "1":
                start_tool_delta()
            case "2":
                plugin_manager.manage_plugins()
            case "3":
                market.enter_plugin_market()
            case "4":
                ToolDelta.change_config()
            case "5":
                open("快速启动.sig", "wb").close()
                Print.clean_print("§a快速启动模式已开启")
                Print.clean_print(
                    "§6删除本地的 §f快速启动.sig§6 文件即可取消快速启动功能"
                )
            case _:
                Print.clean_print("§c不合法的启动模式: " + r)
    except (EOFError, SystemExit):
        pass
    except Exception:
        Print.print_err("ToolDelta 运行过程中出现问题：" + traceback.format_exc())
        input(Print.fmt_info("按回车键退出..", "§c 报错 §r"))
