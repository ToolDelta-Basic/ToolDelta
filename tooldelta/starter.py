"""ToolDelta 启动器"""

import traceback

from .utils import fmts
from .utils.internal import init_dirs
from .frame import GameCtrl, ToolDelta

from .plugin_load.plugins import PluginGroup
from .internal.config_loader import ConfigLoader
from .internal.cmd_executor import ConsoleCmdManager
from .internal.maintainers.players import PlayerInfoMaintainer
from .internal.packet_handler import PacketHandler


tooldelta = ToolDelta()


def start_tool_delta() -> None:
    """启动 ToolDelta"""
    tooldelta.bootstrap()


def init_cfg_only() -> None:
    fmts.print_load("ToolDelta 正在以仅初始插件模式启动")
    try:
        tooldelta.cfg_loader = ConfigLoader(tooldelta)
        tooldelta.welcome()
        init_dirs()
        tooldelta.packet_handler = PacketHandler(tooldelta)
        tooldelta.cmd_manager = ConsoleCmdManager(tooldelta)
        tooldelta.players_maintainer = PlayerInfoMaintainer(tooldelta)
        tooldelta.plugin_group = PluginGroup(tooldelta)
        tooldelta.game_ctrl = GameCtrl(tooldelta)
        tooldelta.add_console_cmd_trigger = tooldelta.cmd_manager.add_console_cmd_trigger
        tooldelta.launcher = tooldelta.cfg_loader.load_tooldelta_cfg_and_get_launcher()
        tooldelta.launcher.set_packet_listener(tooldelta.packet_handler)
        tooldelta.game_ctrl.hook_launcher(tooldelta.launcher)
        tooldelta.game_ctrl.hook_packet_handler(tooldelta.packet_handler)
        tooldelta.plugin_group.hook_packet_handler(tooldelta.packet_handler)
        tooldelta.plugin_group.load_plugins()
        fmts.print_suc("ToolDelta 已初始化所有配置文件。")
    except (KeyboardInterrupt, SystemExit, EOFError) as err:
        if str(err):
            fmts.print_inf(f"ToolDelta 已关闭，退出原因：{err}")
        else:
            fmts.print_inf("ToolDelta 已关闭")
    except Exception:
        fmts.print_err(f"ToolDelta 运行过程中出现问题：{traceback.format_exc()}")


