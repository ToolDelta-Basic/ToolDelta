"""ToolDelta 启动器"""

import os
import time
import traceback

from .color_print import Print
from .frame import GameCtrl, ToolDelta
from .plugin_load.PluginGroup import plugin_group
from .sys_args import sys_args_to_dict
from .urlmethod import check_update
from .utils import timer_event_boostrap, tmpjson_save

tooldelta = ToolDelta()


def start_tool_delta() -> None:
    """启动 ToolDelta"""
    try:
        tooldelta.welcome()
        if "no-update-check" not in sys_args_to_dict():
            check_update()
        else:
            Print.print_war("将不会进行自动更新。")
        tooldelta.basic_operation()
        tooldelta.loadConfiguration()
        tooldelta.launcher.init()
        game_control = GameCtrl(tooldelta)
        tooldelta.set_game_control(game_control)
        tooldelta.set_plugin_group(plugin_group)
        plugin_group.set_frame(tooldelta)
        plugin_group.read_all_plugins()
        timer_event_boostrap()
        tmpjson_save()
        tooldelta.launcher.listen_launched(game_control.system_inject)
        game_control.set_listen_packets_to_launcher()
        tooldelta.comsole_cmd_active()
        while 1:
            err = tooldelta.launcher.launch()
            if isinstance(err, SystemExit):
                break
            else:
                # not achieved?
                Print.print_err(f"启动器框架崩溃, 原因: {err}")
                break
                RETRY_TIME = 1
                Print.print_war(f"将在 {RETRY_TIME}s 后进行重启")
                time.sleep(RETRY_TIME)
                tooldelta.reload()
    except (KeyboardInterrupt, SystemExit, EOFError) as err:
        Print.print_inf(f"ToolDelta 已关闭，退出原因：{err}")
        time.sleep(3)
    except Exception:
        Print.print_err(f"ToolDelta 运行过程中出现问题：{traceback.format_exc()}")
        input(Print.clean_fmt("§c按回车键退出..."))


# /kick FSkyBlueBot


def safe_jump(out_task: bool = True, exit_directly: bool = False) -> None:
    """安全退出

    Args:
        out_task (bool, optional): frame 框架系统是否退出
        exit_directly (bool, optional): 是否三秒强制直接退出
    """
    if out_task:
        tooldelta.system_exit()
    tooldelta.safelyExit()
    if exit_directly:
        for counter in range(3, -1, -1):
            Print.print_war(f"{counter}秒后强制退出...", end="\r")
            time.sleep(1)
        Print.print_suc("ToolDelta 已退出。")
        os._exit(0)
    Print.print_suc("ToolDelta 已退出。")
