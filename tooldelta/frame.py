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
from .constants import SysStatus, TextType
from .game_texts import GameTextsHandle, GameTextsLoader
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
from .internal.maintainers import PlayerInfoMaintainer
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
        try:
            self.cfg_loader = ConfigLoader(self)
            self.welcome()
            self.init_dirs()
            self.packet_handler = PacketHandler(self)
            self.cmd_manager = ConsoleCmdManager(self)
            self.players_maintainer = PlayerInfoMaintainer(self)
            self.plugin_group = PluginGroup(self)
            self.game_ctrl = GameCtrl(self)
            self.add_console_cmd_trigger = self.cmd_manager.add_console_cmd_trigger
            self.launcher = self.cfg_loader.load_tooldelta_cfg_and_get_launcher()
            self.launcher.set_packet_listener(self.packet_handler.entrance)
            self.game_ctrl.hook_packet_handler(self.packet_handler)
            self.plugin_group.hook_packet_handler(self.packet_handler)
            self.plugin_group.load_plugins()
            utils.timer_event_boostrap()
            utils.tmpjson_save()
            self.launcher.listen_launched(self.game_ctrl.system_inject)
            self.game_ctrl.set_listen_packets_to_launcher()
            fmts.print_inf("正在唤醒游戏框架, 等待中...", end="\r")
            # 主进程
            err = self.wait_closed()
            # 主进程结束
            if not isinstance(err, SystemExit):
                fmts.print_err(f"启动器框架崩溃, 原因: {err}")
                return -1
            else:
                return 0
        except (KeyboardInterrupt, SystemExit, EOFError) as err:
            if str(err):
                fmts.print_inf(f"ToolDelta 已关闭，退出原因：{err}")
            else:
                fmts.print_inf("ToolDelta 已关闭")
        except Exception:
            fmts.print_err(f"ToolDelta 运行过程中出现问题：{traceback.format_exc()}")
        finally:
            self.system_exit("normal")

    def wait_closed(self):
        return self.launcher.launch()

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

    def hook_packet_handler(self, hdl: "PacketHandler"):
        hdl.add_packet_listener(
            constants.PacketIDS.IDPlayerList, self.process_player_list
        )
        hdl.add_packet_listener(constants.PacketIDS.Text, self.handle_text_packet)

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
                if self.players_uuid.get(playername):
                    del self.players_uuid[playername]
        return False

    def handle_text_packet(self, pkt: dict):
        """处理 文本 数据包

        Args:
            pkt (dict): 数据包内容
            plugin_grp (PluginGroup): 插件组对象
        """
        msg: str = pkt["Message"]
        match pkt["TextType"]:
            case TextType.TextTypeTranslation:
                if msg == "§e%multiplayer.player.joined":
                    playername = pkt["Parameters"][0]
                    fmts.print_inf(f"§e{playername} 退出了游戏")
                elif msg == "§e%multiplayer.player.left":
                    playername = pkt["Parameters"][0]
                    fmts.print_inf(f"§e{playername} 退出了游戏")
                else:
                    # TODO: another type of message
                    if self.game_data_handler is not None:
                        jon = self.game_data_handler.Handle_Text_Class1(pkt)
                        fmts.print_inf("§1" + " ".join(jon).strip('"'))
                    else:
                        fmts.print_inf(msg)
                    if msg.startswith("death."):
                        args = pkt["Parameters"]
                        Utils.fill_list_index(args, ["", "", ""])
                        who_died, killer, weapon_name = args
                        if weapon_name:
                            fmts.print_inf(
                                f"§e{who_died} 被 {killer} 用 {weapon_name} §r杀死了"
                            )
                        elif killer:
                            fmts.print_inf(f"§e{who_died} 被 {killer} 击败了")
                        else:
                            fmts.print_inf(f"§e{who_died} 死亡了")
            case TextType.TextTypeChat | TextType.TextTypeWhisper:
                src_name = pkt["SourceName"]
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
            case TextType.TextTypeAnnouncement:
                # /say 消息
                src_name = pkt["SourceName"]
                msg = msg.removeprefix(f"[{src_name}] ")
                uuid = "00000000-0000-4000-8000-0000" + pkt["XUID"]
                if uuid in self.players_uuid.values():
                    cmd_executor = {v: k for k, v in self.players_uuid.items()}[uuid]
                    fmts.print_inf(f"{src_name}({cmd_executor}) 使用 say 说：{msg}")
                else:
                    fmts.print_inf(
                        f"{src_name} 使用 say 说：{msg.removeprefix(f'[{src_name}] ')}"
                    )
                    print(self.players_uuid)
            case TextType.TextTypeObjectWhisper:
                # /tellraw 消息
                msg = pkt["Message"]
                msg_text = json.loads(msg)["rawtext"]
                if len(msg_text) > 0 and msg_text[0].get("translate") == "***":
                    fmts.print_with_info("(该 tellraw 内容为敏感词)", "§f 消息 ")
                    return False
                msg_text = "".join([i["text"] for i in msg_text])
                fmts.print_with_info(msg_text, "§f 消息 ")
            case default:
                fmts.print_inf(f"[Text] [{default}] {msg}")
        return False

    def system_inject(self) -> None:
        """载入游戏时的初始化"""
        res = self.launcher.get_players_and_uuids()
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

