import time
from tooldelta import builtins
from tooldelta.Frame import PRG_NAME, Frame
from tooldelta.Frame import GameCtrl
from tooldelta.basic_mods import os, traceback
from tooldelta.color_print import Print
from tooldelta.plugin_load.PluginGroup import PluginGroup
from tooldelta.plugin_load.injected_plugin import movent

frame = Frame()
plugins = PluginGroup(frame, PRG_NAME)
game_control = GameCtrl(frame)


def start_tool_delta(exit_directly=True):
    global frame
    # 初始化系统
    try:
        frame.auto_update()
        frame.welcome()
        frame.basic_operation()
        frame.set_game_control(game_control)
        frame.set_plugin_group(plugins)
        movent.set_frame(frame)
        frame.read_cfg()
        game_control.init_funcs()
        plugins.read_all_plugins()
        frame.plugin_load_finished(plugins)
        plugins.execute_def(frame.on_plugin_err)
        builtins.tmpjson_save_thread()
        frame.launcher.listen_launched(game_control.Inject)
        game_control.set_listen_packets()
        raise frame.launcher.launch()
    except (KeyboardInterrupt, SystemExit):
        pass
    except:
        Print.print_err("ToolDelta 运行过程中出现问题: " + traceback.format_exc())


def safe_jump(exit_directly=True):
    frame.safe_close()
    if exit_directly:
        for _ in range(3, 0, -1):
            Print.print_war(f"{_}秒后强制退出...", end="\r")
            time.sleep(1)
        Print.print_war(f"0秒后强制退出...", end="\r")
        Print.print_suc("ToolDelta 已退出.")
        os._exit(0)
    Print.print_suc("ToolDelta 已退出.")
