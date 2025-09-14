"""
客户端启动器框架
提供与游戏进行交互的标准接口
"""

import threading
import os
import subprocess
from collections.abc import Callable

from ... import utils
from ...constants import SysStatus
from ...packets import Packet_CommandOutput
from ...mc_bytes_packet.base_bytes_packet import BaseBytesPacket
from ...utils import fmts, urlmethod
from ..types import UnreadyPlayer, Abilities
from .langame_libs import core_conn as lamgame_conn
from .langame_libs import utils as langame_utils
from .standard_launcher import StandardFrame


class FrameLanGameAccessPoint(StandardFrame):
    # 启动器类型
    launch_type = "LamGameACP"

    def __init__(self) -> None:
        """实例化启动器框架

        Args:
            serverNumber (int): 服务器号
            password (str): 服务器密码
            fbToken (str): 验证服务器 Token
            auth_server_url (str): 验证服务器地址
        """
        super().__init__()
        self.conn = lamgame_conn.LanGame()
        self.need_listen_packets: set[int] = {9, 63, 79}
        self._launch_listeners: list[Callable[[], None]]
        self.exit_event = threading.Event()
        self.status: SysStatus = SysStatus.LOADING
        self.bot_name: str = ""
        self.ws_service_opened = False

    def init(self):
        """初始化启动器框架"""

    def set_launch_data(
        self, roomID: int, password: str, fbToken: str, auth_server_url: str
    ):
        self.roomID = roomID
        self.roomPasswd = password
        self.fbToken = fbToken
        self.auth_server = auth_server_url

    def launch(self) -> SystemExit:
        self.update_status(SysStatus.LAUNCHING)
        free_port = urlmethod.get_free_port(24010)
        self.openat_port = free_port
        fmts.print_inf(f"正在从 {free_port} 端口启动本地联机接入点...")
        self.start_langame_acp_proc(free_port)
        self._start_proc_message_show_thread()
        self._start_proc_stderr_show_thread()
        self.conn.set_server_packet_listener(
            self.dict_packet_handler_parent, self.bytes_packet_handler_parent
        )
        self.conn.launch_event.wait()
        self.update_status(SysStatus.RUNNING)
        self.conn.set_listen_server_packets(list(self.need_listen_packets))
        self._exec_launched_listen_cbs()
        self.conn.exit_event.wait()
        self.update_status(SysStatus.NORMAL_EXIT)
        return SystemExit("NEMCLanGame 和 ToolDelta 断开连接")

    def start_langame_acp_proc(self, port: int):
        path = langame_utils.get_bin_path()
        if not path.is_file():
            fmts.print_err(f"NEMCLanGame 接入点不存在: {path!s}")
            raise SystemExit
        if not path.name.endswith(".exe"):
            # Maybe is linux and so on
            os.system("chmod +x " + str(path))
        args = [
            str(path),
            "-port",
            str(port),
            "-A",
            self.auth_server,
            "-T",
            self.fbToken,
            "-R",
            str(self.roomID),
            "-P",
            self.roomPasswd,
        ]
        self.proc = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @utils.thread_func(
        "NEMCLanGame 进程输出线程", thread_level=utils.ToolDeltaThread.SYSTEM
    )
    def _start_proc_message_show_thread(self):
        assert self.proc.stdout
        while True:
            msg = self.proc.stdout.readline().decode("utf-8").strip()
            if msg == "":
                break
            elif "WebSocket" in msg and not self.ws_service_opened:
                utils.createThread(
                    self.conn.start_connection,
                    (self.openat_port,),
                    thread_level=utils.ToolDeltaThread.SYSTEM,
                )
                self.ws_service_opened = True
            fmts.print_inf(msg)
        fmts.print_inf("NEMCLanGame 进程已退出")

    @utils.thread_func(
        "NEMCLanGame 报错输出线程", thread_level=utils.ToolDeltaThread.SYSTEM
    )
    def _start_proc_stderr_show_thread(self):
        if self.proc.stderr is None:
            fmts.print_war("NEMCLanGame 错误输出通道不可用")
            return
        while True:
            msg = self.proc.stderr.readline().decode("utf-8")
            if msg == "":
                break
            fmts.print_err(msg.removesuffix("\n"))

    # ====== api ======

    def get_players_info(self) -> dict[str, UnreadyPlayer]:
        # TODO: Can't get PlatformChatID and BuildPlatformID
        return {
            k: UnreadyPlayer(
                uuid=v.uuid,
                unique_id=v.uniqueID,
                name=v.name,
                xuid=v.xuid,
                platform_chat_id="",
                runtime_id=v.runtimeID,
                device_id=None,
                build_platform=0,
                # NOTE: this is dangerous
                abilities=Abilities.unmarshal(
                    v.abilities["Layers"][0]["Abilities"],
                    v.abilities["PlayerPermissions"],
                    v.abilities["CommandPermissions"],
                ),
            )
            for k, v in self.conn.uqs.items()
        }

    def get_bot_name(self) -> str:
        """获取机器人名字"""
        if self.bot_name == "":
            self.bot_name = self.conn.bot_name
        return self.bot_name

    def dict_packet_handler_parent(self, pkt_type: int, pkt: dict) -> None:
        """数据包处理器

        Args:
            pkt_type (str): 数据包类型
            pkt (dict): 数据包内容

        Raises:
            ValueError: 还未连接到游戏
        """
        if not self.conn.connected:
            raise ValueError("还未连接到游戏")
        self.dict_packet_handler(pkt_type, pkt)

    def bytes_packet_handler_parent(self, pkt_type: int, pkt: BaseBytesPacket) -> None:
        """数据包处理器

        Args:
            pkt_type (str): 数据包类型
            pkt (dict): 数据包内容

        Raises:
            ValueError: 还未连接到游戏
        """
        if not self.conn.connected:
            raise ValueError("还未连接到游戏")
        self.bytes_packet_handler(pkt_type, pkt)

    def sendcmd(
        self, cmd: str, waitForResp: bool = False, timeout: float = 30
    ) -> Packet_CommandOutput | None:
        """以玩家身份发送命令

        Args:
            cmd (str): 命令
            waitForResp (bool, optional): 是否等待结果
            timeout (int | float, optional): 超时时间

        Raises:
            TimeoutError: 获取命令返回超时

        Returns:
            Packet_CommandOutput: 返回命令结果
        """
        if not waitForResp:
            self.conn.sendcmd(cmd)
        else:
            if res := self.conn.sendcmd_with_resp(cmd, timeout):
                return res
            else:
                raise TimeoutError("获取命令返回超时")

    def sendwscmd(
        self, cmd: str, waitForResp: bool = False, timeout: float = 30
    ) -> Packet_CommandOutput | None:
        """以 ws 身份发送命令

        Args:
            cmd (str): 命令
            waitForResp (bool, optional): 是否等待结果
            timeout (int | float, optional): 超时时间

        Raises:
            TimeoutError: 获取命令返回超时

        Returns:
            Packet_CommandOutput: 返回命令结果
        """
        if not waitForResp:
            self.conn.sendwscmd(cmd)
        else:
            if res := self.conn.sendwscmd_with_resp(cmd, timeout):
                return res
            else:
                raise TimeoutError("获取命令返回超时")

    def sendwocmd(self, cmd: str) -> None:
        """以 wo 身份发送命令

        Args:
            cmd (str): 命令

        """
        self.conn.sendwocmd(cmd)

    def sendPacket(self, pckID: int, pk: dict | BaseBytesPacket) -> None:
        """发送数据包

        Args:
            pkID (int): 数据包 ID
            pk (dict | BaseBytesPacket): 数据包内容

        """
        if type(pk) is not dict:
            raise Exception("sendPacket: 目前只支持传入 dict 作为数据包")
        self.conn.sendPacket(pckID, pk)

    def is_op(self, player: str) -> bool:
        """检查玩家是否为 OP

        Args:
            player (str): 玩家名

        Returns:
            bool: 是否为 OP
        """
        if player not in self.conn.uqs.keys():
            raise ValueError(f"玩家不存在: {player}")
        return self.conn.uqs[player].abilities["CommandPermissions"] >= 3
