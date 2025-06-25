"""
ToolDelta 基本框架

整个系统由三个部分组成
    Frame: 负责整个 ToolDelta 的基本框架运行
    GameCtrl: 负责对接游戏
        - Launchers: 负责将不同启动器的游戏接口统一成固定的接口，供插件在多平台游戏接口运行 (FastBuilder External, NeOmega, (BEWS, etc.))
    PluginGroup: 负责对插件进行统一管理
"""

import os
import signal
import traceback
import json

from . import constants, extend_functions, game_utils, utils
from .constants import SysStatus, TextType
from .internal.config_loader import ConfigLoader
from .internal.packet_handler import PacketHandler
from .internal.cmd_executor import ConsoleCmdManager
from .internal.maintainers.players import PlayerInfoMaintainer
from .internal.types import FrameExit
from .internal.launch_cli.neo_libs.blob_hash.blob_hash_holder import (
    BlobHashHolder,
)
from .internal.launch_cli import (
    FrameNeOmgAccessPoint,
    FrameNeOmegaLauncher,
    FB_LIKE_LAUNCHERS,
    LAUNCHERS,
)
from .game_texts import GameTextsHandle, GameTextsLoader
from .packets import Packet_CommandOutput
from .utils import internal as utils_internal, cfg, fmts
from .version import get_tool_delta_version
from .plugin_load.plugins import PluginGroup



VERSION = get_tool_delta_version()



class ToolDelta:
    """ToolDelta 主框架"""

    class FrameBasic:
        """系统基本信息"""

        system_version = VERSION
        data_path = "插件数据文件/"

    def __init__(self) -> None:
        """初始化"""
        self.initialized = False
        self.ready = False
        self.sys_data = self.FrameBasic()
        self.launchMode: int = 0
        self.on_plugin_err = staticmethod(
            lambda name, err: fmts.print_err(
                f"插件 <{name}> 出现问题: {err}\n§c{traceback.format_exc()}"
            )
        )
        def signal_handler(_, pyframe) -> None:
            fmts.clean_print("§6ToolDelta 已被手动终止")
            self.system_exit("用户退出程序")
            os._exit(1)


        signal.signal(signal.SIGINT, signal_handler)

    def bootstrap(self):
        try:
            self.cfg_loader = ConfigLoader(self)
            self.welcome()
            utils_internal.init_dirs()
            self.packet_handler = PacketHandler(self)
            self.cmd_manager = ConsoleCmdManager(self)
            self.players_maintainer = PlayerInfoMaintainer(self)
            self.plugin_group = PluginGroup(self)
            self.game_ctrl = GameCtrl(self)
            self.add_console_cmd_trigger = self.cmd_manager.add_console_cmd_trigger
            self.launcher = self.cfg_loader.load_tooldelta_cfg_and_get_launcher()
            self.game_ctrl.hook_launcher(self.launcher)
            self.game_ctrl.hook_packet_handler(self.packet_handler)
            self.players_maintainer.hook_packet_handler(self.packet_handler)
            self.plugin_group.load_plugins()
            self.plugin_group.hook_packet_handler(self.packet_handler)
            self.launcher.set_packet_listener(self.packet_handler)
            self.initialized = True
            utils.timer_event_boostrap()
            utils.tempjson.jsonfile_auto_save()
            game_utils.hook_packet_handler(self.packet_handler)
            extend_functions.load_functions(self)
            self.launcher.init()
            self.launcher.listen_launched(
                [
                    self.game_ctrl.system_inject,
                    self.cmd_manager.start_proc_thread,
                    extend_functions.activate_functions,
                ]
            )
            fmts.print_inf("正在唤醒游戏框架, 等待中...", end="\r")
            self.ready = True
            err = self.wait_closed()
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
        fmts.print_load("§dToolDelta Wiki: https://wiki.tooldelta.top/")
        fmts.print_load("§dToolDelta 交流群: 1030755163")
        fmts.print_load("§dToolDelta 项目地址: https://github.com/ToolDelta-Basic")
        fmts.print_load(f"§dToolDelta v {'.'.join([str(i) for i in VERSION])}")
        fmts.print_load("§dToolDelta Panel 已启动")

    def get_game_control(self) -> "GameCtrl":
        """获取 GameControl 对象

        Returns:
            GameCtrl: GameControl 对象
        """
        return self.game_ctrl

    def get_players(self) -> "PlayerInfoMaintainer":
        """获取 GameControl 对象

        Returns:
            GameCtrl: GameControl 对象
        """
        return self.players_maintainer

    def reload(self):
        """
        重载系统插件。

        如果需要在插件内调用, 请为执行这个方法的函数分配系统级的 ToolDeltaThread。
        """
        self.plugin_group.pre_reload()
        while 1:
            try:
                fmts.print_inf("重载: 正在让插件自行退出..")
                fmts.print_inf("重载: 正在保存数据缓存文件..")
                utils.safe_close()
                self.cmd_manager.reset_cmds()
                fmts.print_inf("重载: 正在重新载入插件..")
                self.plugin_group.reload()
                fmts.print_suc("重载插件: 全部插件重载成功！")
                utils.timer_event_boostrap()
                return
            except cfg.ConfigError as err:
                fmts.print_err(f"重载插件时发现插件配置文件有误: {err}")
            except SystemExit:
                fmts.print_err("重载插件遇到问题")
            except BaseException:
                fmts.print_err("重载插件遇到问题 (报错如下):")
                fmts.print_err(traceback.format_exc())
            self.plugin_group.pre_reload()
            input(fmts.fmt_info("在修好插件后, 按回车键重新重载插件"))
            continue

    def system_exit(self, reason: str) -> None:
        """ToolDelta 系统退出"""
        # 启动器框架是否被载入
        if self.ready:
            if self.launcher.status == SysStatus.RUNNING:
                self.launcher.update_status(SysStatus.NORMAL_EXIT)
        if self.initialized:
            self.plugin_group.execute_frame_exit(
                FrameExit(self.launcher.status, reason), self.on_plugin_err
            )
        # 先将启动框架 (进程) 关闭了
        if self.ready:
            if self.launcher.status == SysStatus.NORMAL_EXIT:
                # 运行中退出
                if isinstance(
                    self.launcher, FrameNeOmgAccessPoint | FrameNeOmegaLauncher
                ):
                    try:
                        self.game_ctrl.sendwocmd(
                            f'/kick "{self.game_ctrl.bot_name}" ToolDelta 退出中。'
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
        # 到这里就基本上退出完成了

    @staticmethod
    def actions_before_exited() -> None:
        """安全退出"""
        utils.safe_close()
        fmts.print_inf("已保存数据与日志等信息。")


class GameCtrl:
    """游戏连接和交互部分"""

    def __init__(self, frame: "ToolDelta"):
        """初始化

        Args:
            frame (ToolDelta): 继承 Frame 的对象
        """
        try:
            self.game_texts_data = GameTextsLoader().game_texts_data
            self.game_data_handler = GameTextsHandle(self.game_texts_data)
        except Exception as err:
            fmts.print_war(f"游戏文本翻译器不可用: {err}")
            self.game_texts_data = None
            self.game_data_handler = None
        self.linked_frame = frame

    def hook_packet_handler(self, hdl: "PacketHandler"):
        hdl.add_dict_packet_listener(
            constants.PacketIDS.Text, self.handle_text_packet, -1
        )

    def hook_launcher(self, launcher: "LAUNCHERS"):
        self.launcher = launcher
        self.sendcmd = launcher.sendcmd
        self.sendwscmd = launcher.sendwscmd
        self.sendwocmd = launcher.sendwocmd
        self.sendPacket = launcher.sendPacket
        # TODO: pretty this code because it is not a good interface
        if hasattr(launcher, "blobHashHolder"):
            self.blobHashHolder = launcher.blobHashHolder

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
                    fmts.print_inf(f"§e{playername} 加入了游戏")
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
            case (
                TextType.TextTypeChat
                | TextType.TextTypeWhisper
                | TextType.TextTypeAnnouncement
            ):
                playername, message, ensurePlayer = (
                    utils.get_playername_and_msg_from_text_packet(
                        self.linked_frame, pkt
                    )
                )
                if playername is None or msg is None:
                    return False
                if ensurePlayer:
                    fmts.print_inf(f"<{playername}> {message}")
                else:
                    fmts.print_inf(f"<{playername}(伪造)> {message}")
            case TextType.TextTypeObjectWhisper:
                # /tellraw 消息
                msg = pkt["Message"]
                msg_text = json.loads(msg).get("rawtext")
                if msg_text is not None:
                    if len(msg_text) > 0 and msg_text[0].get("translate") == "***":
                        fmts.print_with_info("(该 tellraw 内容为敏感词)", "§f 消息 ")
                        return False
                    msg_text = "".join(
                        [(i.get("text") or i.get("translate", "???")) for i in msg_text]
                    )
                fmts.print_with_info(msg_text, "§f 消息 ")
        return False

    def system_inject(self):
        self.linked_frame.players_maintainer.block_init()
        self.linked_frame.plugin_group.execute_init(self.linked_frame.on_plugin_err)
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

    # 向下兼容
    @property
    def players_uuid(self):
        """
        Deprecated: 请使用 `game_ctrl.players.uuid_to_player`

        Returns:
            dict[str, str]: uuid -> 玩家名 的映射
        """
        return {
            v.name: k
            for k, v in self.linked_frame.players_maintainer.uuid_to_player.items()
        }

    # 向下兼容
    @property
    def allplayers(self):
        """
        Deprecated: 使用 `game_ctrl.players` 获取所有在线玩家。
        Returns:
            _type_: _description_
        """
        return [i.name for i in self.linked_frame.players_maintainer.getAllPlayers()]

    # 向下兼容
    @property
    def bot_name(self) -> str:
        """
        Deprecated: 使用 `game_ctrl.players.getBotInfo()` 获取更详细的机器人信息。

        Raises:
            ValueError: _description_

        Returns:
            str: _description_
        """
        if hasattr(self.launcher, "bot_name"):
            return self.launcher.get_bot_name()
        raise ValueError(
            f"此启动器 ({self.launcher.__class__.__name__}) 框架无法产生机器人名"
        )

    def sendcmd_with_resp(self, cmd: str, timeout: float = 30) -> Packet_CommandOutput:
        """
        发送普通指令并获取返回。

        Args:
            cmd (str): Minecraft 指令
            timeout (float, optional): 超时时间, 超时则引发 TimeoutError

        Returns:
            Packet_CommandOutput: 指令返回类
        """
        resp: Packet_CommandOutput = self.sendcmd(cmd, True, timeout)  # type: ignore
        return resp

    def sendwscmd_with_resp(
        self, cmd: str, timeout: float = 30
    ) -> Packet_CommandOutput:
        """
        发送 WebSocket 指令并获取返回。

        Args:
            cmd (str): MC WebSocket 指令
            timeout (float, optional): 超时时间, 超时则引发 TimeoutError

        Returns:
            Packet_CommandOutput: 指令返回类
        """
        resp: Packet_CommandOutput = self.sendwscmd(cmd, True, timeout)  # type: ignore
        return resp

    def say_to(self, target: str, text: str) -> None:
        """向玩家发送消息

        Args:
            target (str): 玩家名/目标选择器
            msg (str): 消息
        """
        text_json = json.dumps({"rawtext": [{"text": text}]}, ensure_ascii=False)
        self.sendwocmd(f"tellraw {utils.to_player_selector(target)} {text_json}")

    def player_title(self, target: str, text: str) -> None:
        """向玩家展示标题文本

        Args:
            target (str): 玩家名/目标选择器
            text (str): 文本
        """
        text_json = json.dumps({"rawtext": [{"text": text}]}, ensure_ascii=False)
        self.sendwocmd(f"titleraw {utils.to_player_selector(target)} title {text_json}")

    def player_subtitle(self, target: str, text: str) -> None:
        """向玩家展示副标题文本

        Args:
            target (str): 玩家名/目标选择器
            text (str): 文本
        """
        text_json = json.dumps({"rawtext": [{"text": text}]}, ensure_ascii=False)
        self.sendwocmd(
            f"titleraw {utils.to_player_selector(target)} subtitle {text_json}"
        )

    def player_actionbar(self, target: str, text: str) -> None:
        """向玩家展示动作栏文本

        Args:
            target (str): 玩家名/目标选择器
            text (str): 文本
        """
        text_json = json.dumps({"rawtext": [{"text": text}]}, ensure_ascii=False)
        self.sendwocmd(
            f"titleraw {utils.to_player_selector(target)} actionbar {text_json}"
        )

    def get_game_data(self) -> dict:
        """获取游戏常见字符串数据

        Returns:
            dict: 游戏常见字符串数据
        """
        if self.game_texts_data is None:
            raise ValueError("游戏翻译器字符串数据不可用")
        return self.game_texts_data

    @property
    def players(self):
        """
        获取玩家信息存储 (PlayerInfoMaintainer)
        """
        return self.linked_frame.get_players()

    # TODO: pretty this code because it is not a good interface
    # 这个方法需要得到修改, 因为它不是一个通用接口
    def blob_hash_holder(self) -> BlobHashHolder:
        """
        blobHashHolder 返回 ToolDelta 的 Blob hash cache 缓存数据集的持有人。
        请确保当前的启动模式为 NeOmega 系启动器。

        Returns:
            BlobHashHolder: ToolDelta 的 Blob hash cache 缓存数据集的持有人
        """
        blobHashHolder: BlobHashHolder | None = getattr(self, "blobHashHolder", None)
        if blobHashHolder is None:
            raise ValueError("仅 NeOmega 系框架可使用 BlobHashHolder 功能")
        return self.blobHashHolder()
