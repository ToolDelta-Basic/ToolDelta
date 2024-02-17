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
def start_tool_delta(exit_directly = False):
    # 初始化系统
    try:
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
    finally:
        frame.safe_close()
        Print.print_suc("ToolDelta 已退出.")
        if exit_directly:
            os._exit(0)
