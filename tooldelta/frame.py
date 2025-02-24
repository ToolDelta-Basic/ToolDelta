"""
ToolDelta 基本框架

整个系统由三个部分组成
    Frame: 负责整个 ToolDelta 的基本框架运行
    GameCtrl: 负责对接游戏
        - Launchers: 负责将不同启动器的游戏接口统一成固定的接口，供插件在多平台游戏接口运行 (FastBuilder External, NeOmega, (BEWS, etc.))
    PluginGroup: 负责对插件进行统一管理
"""

import asyncio
import os
import signal
import sys
import traceback
import json
from . import constants, game_utils, utils
from .cfg import Config
from .color_print import fmts
from .constants import SysStatus
from .game_texts import GameTextsHandle, GameTextsLoader
from .game_utils import getPosXYZ
from .get_tool_delta_version import get_tool_delta_version
from .logger import publicLogger
from .packets import Packet_CommandOutput
from .plugin_load import injected_plugin
from .utils import Utils
from .sys_args import sys_args_to_dict

from .plugin_load.plugins import PluginGroup
from .internal.config_loader import ConfigLoader
from .internal.packet_handler import PacketHandler
from .internal.cmd_executor import ConsoleCmdManager
from .internal.maintainer import PlayerInfoMaintainer
from .internal.types import FrameExit
from .internal.launch_cli import (
    FrameNeOmgAccessPoint,
    FrameNeOmegaLauncher,
    FB_LIKE_LAUNCHERS,
)




###### CONSTANT DEFINE

sys_args_dict = sys_args_to_dict(sys.argv)
VERSION = get_tool_delta_version()

###### FRAME DEFINE


class ToolDelta:
    """ToolDelta 主框架"""

    class FrameBasic:
        """系统基本信息"""

        system_version = VERSION
        data_path = "插件数据文件/"

    def __init__(self) -> None:
        """初始化"""
        self.sys_data = self.FrameBasic()
        self.launchMode: int = 0
        self.on_plugin_err = staticmethod(
            lambda name, err: fmts.print_err(f"插件 <{name}> 出现问题：\n{err}")
        )

    def bootstrap(self):
        self.cfg_loader = ConfigLoader(self)
        # 监听数据包
        # 向下兼容
        self.welcome()
        self.init_dirs()
        self.packet_handler = PacketHandler(self)
        self.cmd_manager = ConsoleCmdManager(self)
        self.players_maintainer = PlayerInfoMaintainer(self)
        self.plugin_group = PluginGroup(self)
        self.add_console_cmd_trigger = self.cmd_manager.add_console_cmd_trigger
        self.launcher = self.cfg_loader.load_tooldelta_cfg_and_get_launcher()
        self.launcher.set_packet_listener(self.packet_handler.entrance)
        self.plugin_group.hook_packet_handler(self.packet_handler)

    @staticmethod
    def welcome() -> None:
        """欢迎提示"""
        fmts.print_load("§dToolDelta Panel Embed By SuperScript")
        fmts.print_load("§dToolDelta Wiki: https://td-wiki.dqyt.online/")
        fmts.print_load("§dToolDelta 交流群: 1030755163")
        fmts.print_load("§dToolDelta 项目地址: https://github.com/ToolDelta-Basic")
        fmts.print_load(f"§dToolDelta v {'.'.join([str(i) for i in VERSION])}")
        fmts.print_load("§dToolDelta Panel 已启动")

    def init_dirs(self):
        """初始化文件夹等"""
        os.makedirs(
            os.path.join("插件文件", constants.TOOLDELTA_CLASSIC_PLUGIN), exist_ok=True
        )
        os.makedirs(
            os.path.join("插件文件", constants.TOOLDELTA_INJECTED_PLUGIN), exist_ok=True
        )
        os.makedirs("插件配置文件", exist_ok=True)
        os.makedirs(os.path.join("tooldelta", "neo_libs"), exist_ok=True)
        os.makedirs(os.path.join("插件数据文件", "game_texts"), exist_ok=True)
        if sys.platform == "win32":
            self.win_create_batch_file()

    @staticmethod
    def win_create_batch_file():
        if not os.path.isfile("点我启动.bat"):
            argv = sys.argv.copy()
            if argv[0].endswith(".py"):
                argv.insert(0, "python")
            exec_cmd = " ".join(argv)
            with open("点我启动.bat", "w") as f:
                f.write(f"@echo off\n{exec_cmd}\npause")

    def system_exit(self, reason: str) -> None:
        """ToolDelta 系统退出"""
        # 启动器框架是否被载入
        has_launcher = hasattr(self, "launcher")
        if has_launcher:
            if self.launcher.status == SysStatus.RUNNING:
                self.launcher.update_status(SysStatus.NORMAL_EXIT)
        self.plugin_group.execute_frame_exit(
            FrameExit(self.launcher.status, reason), self.on_plugin_err
        )
        asyncio.run(injected_plugin.safe_jump_repeat_tasks())
        # 先将启动框架 (进程) 关闭了
        if has_launcher:
            if self.launcher.status == SysStatus.NORMAL_EXIT:
                # 运行中退出
                if isinstance(
                    self.launcher, FrameNeOmgAccessPoint | FrameNeOmegaLauncher
                ):
                    try:
                        self.link_game_ctrl.sendwocmd(
                            f'/kick "{self.link_game_ctrl.bot_name}" ToolDelta 退出中。'
                        )
                    except Exception:
                        pass
                    if not isinstance(self.launcher.neomg_proc, type(None)):
                        if os.name == "nt":
                            self.launcher.neomg_proc.send_signal(
                                signal.CTRL_BREAK_EVENT
                            )
                        else:
                            self.launcher.neomg_proc.send_signal(signal.SIGTERM)
            else:
                # 其他情况下退出 (例如启动失败)
                pass
            # 然后使得启动框架联络进程也退出
            if isinstance(self.launcher, FB_LIKE_LAUNCHERS):
                self.launcher.exit_event.set()
        # 最后做善后工作
        self.actions_before_exited()
        # 到这里就基本上是退出完成了

    def set_game_control(self, game_ctrl: "GameCtrl") -> None:
        """使用外源 GameControl

        Args:help
            game_ctrl (_type_): GameControl 对象
        """
        self.link_game_ctrl = game_ctrl

    def get_game_control(self) -> "GameCtrl":
        """获取 GameControl 对象

        Returns:
            GameCtrl: GameControl 对象
        """
        gcl: "GameCtrl" = self.link_game_ctrl
        return gcl

    @staticmethod
    def actions_before_exited() -> None:
        """安全退出"""
        utils.safe_close()
        publicLogger.exit()
        fmts.print_inf("已保存数据与日志等信息。")

    def reload(self):
        """重载所有插件"""
        try:
            fmts.print_inf("重载插件: 正在保存数据缓存文件..")
            utils.safe_close()
            self.cmd_manager.reset_cmds()
            fmts.print_inf("重载插件: 正在重新载入插件..")
            self.plugin_group.reload()
            self.launcher.reload_listen_packets(
                self.link_game_ctrl.require_listen_packets
            )
            fmts.print_suc("重载插件: 全部插件重载成功！")
        except Config.ConfigError as err:
            fmts.print_err(f"重载插件时发现插件配置文件有误: {err}")
        except SystemExit:
            fmts.print_err("重载插件遇到问题")
        except BaseException:
            fmts.print_err("重载插件遇到问题 (报错如下):")
            fmts.print_err(traceback.format_exc())
        finally:
            utils.timer_event_boostrap()


class GameCtrl:
    """游戏连接和交互部分"""

    def __init__(self, frame: "ToolDelta"):
        """初始化

        Args:
            frame (Frame): 继承 Frame 的对象
        """
        try:
            self.game_texts_data = GameTextsLoader().game_texts_data
            self.game_data_handler = GameTextsHandle(self.game_texts_data)
        except Exception as err:
            fmts.print_war(f"游戏文本翻译器不可用: {err}")
            self.game_texts_data = None
            self.game_data_handler = None
        self.linked_frame = frame
        self.players_uuid: dict[str, str] = {}
        self.allplayers: list[str] = []
        self.all_players_data = {}
        self.require_listen_packets = {9, 79, 63}
        self.launcher = self.linked_frame.launcher
        # 初始化基本函数
        self.sendcmd = self.launcher.sendcmd
        self.sendwscmd = self.launcher.sendwscmd
        self.sendwocmd = self.launcher.sendwocmd
        self.sendPacket = self.launcher.sendPacket
        if isinstance(self.linked_frame.launcher, FrameNeOmgAccessPoint):
            self.requireUUIDPacket = False
        else:
            self.requireUUIDPacket = True

    def hook(self, hdl: "PacketHandler"):
        hdl.add_packet_listener(
            constants.PacketIDS.IDPlayerList, self.process_player_list
        )
        hdl.add_packet_listener(constants.PacketIDS.Text, self.process_text_packet)

    def set_listen_packets_to_launcher(self) -> None:
        """
        向启动器初始化监听的游戏数据包
        仅限启动模块调用
        """
        self.launcher.add_listen_packets(*self.require_listen_packets)

    def add_listen_packet(self, pkt: int) -> None:
        """
        添加监听的数据包
        仅限内部与插件加载器调用

        Args:
            pkt (int): 数据包 ID
        """
        self.require_listen_packets.add(pkt)

    def process_player_list(self, pkt: dict):
        """处理玩家列表等数据包

        Args:
            pkt (dict): 数据包内容
            plugin_group (PluginGroup): 插件组对象
        """
        # 处理玩家进出事件
        res = self.launcher.get_players_and_uuids()
        if res:
            self.allplayers = list(res.keys())
            self.players_uuid.update(res)
        for player in pkt["Entries"]:
            isJoining = bool(player["Skin"]["SkinData"])
            playername = player["Username"]
            if isJoining:
                if isinstance(self.launcher, FrameNeOmgAccessPoint):
                    self.all_players_data = self.launcher.omega.get_all_online_players()
                if playername not in self.allplayers and not res:
                    self.allplayers.append(playername)
            else:
                playername = next(
                    (k for k, v in self.players_uuid.items() if v == player["UUID"]),
                    None,
                )
                if playername is None:
                    fmts.print_war("无法获取 PlayerList 中玩家名字")
                    continue
                if playername != "???" and not res:
                    self.allplayers.remove(playername)
                if isinstance(self.launcher, FrameNeOmgAccessPoint):
                    self.all_players_data = self.launcher.omega.get_all_online_players()
                if self.players_uuid.get(playername):
                    del self.players_uuid[playername]
        return False

    def process_text_packet(self, pkt: dict):
        """处理 9 号数据包的消息

        Args:
            pkt (dict): 数据包内容
            plugin_grp (PluginGroup): 插件组对象
        """
        match pkt["TextType"]:
            case 2:
                if pkt["Message"] == "§e%multiplayer.player.joined":
                    playername = pkt["Parameters"][0]
                    fmts.print_inf(f"§e{playername} 退出了游戏")
                elif pkt["Message"] == "§e%multiplayer.player.left":
                    playername = pkt["Parameters"][0]
                    fmts.print_inf(f"§e{playername} 退出了游戏")
                else:
                    # TODO: another type of message
                    if self.game_data_handler is not None:
                        jon = self.game_data_handler.Handle_Text_Class1(pkt)
                        fmts.print_inf("§1" + " ".join(jon).strip('"'))
                    else:
                        fmts.print_inf(pkt["Message"])
                    if pkt["Message"].startswith("death."):
                        if len(pkt["Parameters"]) >= 2:
                            killer = pkt["Parameters"][1]
                        else:
                            killer = None
            case 1 | 7:
                src_name = pkt["SourceName"]
                msg = pkt["Message"]
                playername = Utils.to_plain_name(src_name)
                if src_name == "":
                    # /me 消息
                    msg_list = msg.split(" ")
                    if len(msg_list) >= 3:
                        src_name = msg_list[1]
                        msg = " ".join(msg_list[2:])
                    else:
                        return False
                # game_utils.waitMsg 需要监听玩家信息
                # 监听后, 消息仍被处理
                if playername in game_utils.player_waitmsg_cb.keys():
                    game_utils.player_waitmsg_cb[playername](msg)
                fmts.print_inf(f"<{playername}> {msg}")
            case 8:
                # /say 消息
                src_name = pkt["SourceName"]
                msg = pkt["Message"].removeprefix(f"[{src_name}] ")
                uuid = "00000000-0000-4000-8000-0000" + pkt["XUID"]
                if uuid in self.players_uuid.values():
                    cmd_executor = {v: k for k, v in self.players_uuid.items()}[uuid]
                    fmts.print_inf(f"{src_name}({cmd_executor}) 使用 say 说：{msg}")
                else:
                    fmts.print_inf(
                        f"{src_name} 使用 say 说：{msg.removeprefix(f'[{src_name}] ')}"
                    )
                    print(self.players_uuid)
            case 9:
                # /tellraw 消息
                msg = pkt["Message"]
                try:
                    msg_text = json.loads(msg)["rawtext"]
                    if len(msg_text) > 0 and msg_text[0].get("translate") == "***":
                        fmts.print_with_info("(该 tellraw 内容为敏感词)", "§f 消息 ")
                        return False
                    msg_text = "".join([i["text"] for i in msg_text])
                    fmts.print_with_info(msg_text, "§f 消息 ")
                except Exception:
                    pass
        return False

    def system_inject(self) -> None:
        """载入游戏时的初始化"""
        # if hasattr(self.launcher, "bot_name"):
        #    self.tmp_tp_all_players()
        res = self.launcher.get_players_and_uuids()
        if isinstance(self.launcher, FrameNeOmgAccessPoint):
            self.all_players_data = self.launcher.omega.get_all_online_players()
        self.give_bot_effect_invisibility()
        if res:
            self.allplayers = list(res.keys())
            self.players_uuid.update(res)
        else:
            while 1:
                try:
                    cmd_result = self.sendcmd_with_resp("/list")
                    if (
                        cmd_result.OutputMessages is None
                        or len(cmd_result.OutputMessages) < 2
                    ):
                        raise ValueError
                    if (
                        cmd_result.OutputMessages[1].Parameters is None
                        or len(cmd_result.OutputMessages[1].Parameters) < 1
                    ):
                        raise ValueError
                    self.allplayers = (
                        cmd_result.OutputMessages[1].Parameters[0].split(", ")
                    )
                    break
                except (TimeoutError, ValueError):
                    fmts.print_war("获取全局玩家失败..重试")
        self.linked_frame.plugin_group.execute_init(
            self.linked_frame.on_plugin_err
        )
        self.inject_welcome()

    def inject_welcome(self) -> None:
        """初始化欢迎信息"""
        fmts.print_suc(
            "成功连接到游戏网络并初始化, 在线玩家: "
            + ", ".join(self.allplayers)
            + ", 机器人 ID: "
            + self.bot_name
        )
        self.sendcmd("/tag @s add robot")
        fmts.print_inf(
            "在控制台输入 §b插件市场§r 以§a一键获取§rToolDelta官方和第三方的插件"
        )
        fmts.print_suc("在控制台输入 §fhelp / ?§r§a 可查看控制台命令")
        if isinstance(self.launcher, FrameNeOmegaLauncher):
            fmts.print_suc("在控制台输入 o <neomega指令> 可执行NeOmega的控制台指令")

    @property
    def bot_name(self) -> str:
        if hasattr(self.launcher, "bot_name"):
            return self.launcher.get_bot_name()
        raise ValueError("此启动器框架无法产生机器人名")

    def sendcmd_with_resp(self, cmd: str, timeout: float = 30) -> Packet_CommandOutput:
        resp: Packet_CommandOutput = self.sendwscmd(cmd, True, timeout)  # type: ignore
        return resp

    def sendwscmd_with_resp(
        self, cmd: str, timeout: float = 30
    ) -> Packet_CommandOutput:
        resp: Packet_CommandOutput = self.sendwscmd(cmd, True, timeout)  # type: ignore
        return resp

    def say_to(self, target: str, text: str) -> None:
        """向玩家发送消息

        Args:
            target (str): 玩家名/目标选择器
            msg (str): 消息
        """
        text_json = json.dumps({"rawtext": [{"text": text}]}, ensure_ascii=False)
        self.sendwocmd(f"tellraw {Utils.to_player_selector(target)} {text_json}")

    def player_title(self, target: str, text: str) -> None:
        """向玩家展示标题文本

        Args:
            target (str): 玩家名/目标选择器
            text (str): 文本
        """
        text_json = json.dumps({"rawtext": [{"text": text}]}, ensure_ascii=False)
        self.sendwocmd(f"titleraw {Utils.to_player_selector(target)} title {text_json}")

    def player_subtitle(self, target: str, text: str) -> None:
        """向玩家展示副标题文本

        Args:
            target (str): 玩家名/目标选择器
            text (str): 文本
        """
        text_json = json.dumps({"rawtext": [{"text": text}]}, ensure_ascii=False)
        self.sendwocmd(
            f"titleraw {Utils.to_player_selector(target)} subtitle {text_json}"
        )

    def player_actionbar(self, target: str, text: str) -> None:
        """向玩家展示动作栏文本

        Args:
            target (str): 玩家名/目标选择器
            text (str): 文本
        """
        text_json = json.dumps({"rawtext": [{"text": text}]}, ensure_ascii=False)
        self.sendwocmd(
            f"titleraw {Utils.to_player_selector(target)} actionbar {text_json}"
        )

    def get_game_data(self) -> dict:
        """获取游戏常见字符串数据

        Returns:
            dict: 游戏常见字符串数据
        """
        if self.game_texts_data is None:
            raise ValueError("游戏翻译器字符串数据不可用")
        return self.game_texts_data

    @Utils.timer_event(6400, "给予机器人隐身效果", Utils.ToolDeltaThread.SYSTEM)
    def give_bot_effect_invisibility(self) -> None:
        """给机器人添加隐身效果"""
        self.sendwocmd(f"/effect {self.bot_name} invisibility 99999 255 true")

    def tmp_tp_all_players(self) -> None:
        """
        内部调用：在 ToolDelta 连接到 NeOmega 后先 tp 所有玩家（防止玩家 entityruntimeid 为空）
        外部调用：临时传送至所有玩家后回到原位
        """
        BotPos: tuple[float, float, float] = getPosXYZ(self.bot_name)
        for player in self.allplayers:
            if player == self.bot_name:
                continue
            self.sendwocmd(f"tp {self.bot_name} {player}")
        self.sendwocmd(
            f"tp {self.bot_name} {str(int(BotPos[0])) + ' ' + str(int(BotPos[1])) + ' ' + str(int(BotPos[2]))}"
        )

    def get_player_name_from_entity_runtime(self, runtimeid: int) -> str | None:
        """根据实体 runtimeid 获取玩家名

        Args:
            runtimeid (int): 实体 RuntimeID

        Returns:
            str | None: 玩家名
        """
        if not self.all_players_data:
            return None
        for player in self.all_players_data:
            if player.entity_runtime_id == runtimeid:
                return player.name
        return None

    def get_player_entity_runtime_id_from_name(self, player_name: str) -> int | None:
        """
        根据玩家名获取实体 runtimeid

        Args:
            player_name (str): 玩家名

        Returns:
            int | None: 实体 runtimeid
        """
        if not self.all_players_data:
            return None
        for player in self.all_players_data:
            if player.name == player_name:
                return player.entity_runtime_id
