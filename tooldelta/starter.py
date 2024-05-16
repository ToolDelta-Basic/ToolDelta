"""ToolDelta 启动器"""
import os
import time
import traceback
from .utils import tmpjson_save_thread
from .urlmethod import check_update
from .sys_args import sys_args_to_dict
from .frame import Frame, GameCtrl
from .color_print import Print
from .plugin_load.PluginGroup import plugin_group
from .plugin_load.injected_plugin import movent

frame = Frame()

def start_tool_delta() -> None:
    """启动ToolDelta"""
    try:
        frame.welcome()
        if "no-update-check" not in sys_args_to_dict().keys():
            check_update()
        else:
            Print.print_war("将不会进行自动更新.")
        frame.basic_operation()
        frame.loadConfiguration()
        game_control = GameCtrl(frame)
        frame.set_game_control(game_control)
        frame.set_plugin_group(plugin_group)
        plugin_group.set_frame(frame)
        plugin_group.read_all_plugins()
        frame.plugin_load_finished(plugin_group)
        tmpjson_save_thread()
        frame.launcher.listen_launched(game_control.Inject)
        game_control.set_listen_packets()
        raise frame.launcher.launch()
    except (KeyboardInterrupt, SystemExit, EOFError):
        pass
    except Exception:
        Print.print_err("ToolDelta 运行过程中出现问题: " + traceback.format_exc())


def safe_jump(*, out_task: bool = True, exit_directly: bool = True) -> None:
    """安全退出

    Args:
        out_task (bool, optional): frame框架系统是否退出
        exit_directly (bool, optional): 是否三秒强制直接退出
    """
    if out_task:
        frame.system_exit()
    frame.safelyExit()
    if exit_directly:
        for _ in range(2, 0, -1):
            with Print.lock:Print.print_war(f"{_}秒后强制退出...", end="\r")
            time.sleep(1)
        with Print.lock:Print.print_war("0秒后强制退出...", end="\r")
        with Print.lock:Print.print_suc("ToolDelta 已退出.")
        os._exit(0)
    with Print.lock:Print.print_suc("ToolDelta 已退出.")
