"""
客户端启动器框架
提供与游戏进行交互的标准接口
"""

import threading
from collections.abc import Callable

from ... import utils
from ...constants import SysStatus
from ...packets import Packet_CommandOutput
from ...mc_bytes_packet.base_bytes_packet import BaseBytesPacket
from ...utils import fmts
from ..types import UnreadyPlayer, Abilities
from .eulogist_libs import core_conn as eulogist_conn
from .standard_launcher import StandardFrame


class FrameEulogistLauncher(StandardFrame):
    # 启动器类型
    launch_type = "Eulogist"

    def __init__(self) -> None:
        """实例化启动器框架

        Args:
            serverNumber (int): 服务器号
            password (str): 服务器密码
            fbToken (str): 验证服务器 Token
            auth_server_url (str): 验证服务器地址
        """
        super().__init__()
        self.eulogist = eulogist_conn.Eulogist()
        self.need_listen_packets: set[int] = {9, 63, 79}
        self._launch_listeners: list[Callable[[], None]]
        self.exit_event = threading.Event()
        self.status: int = SysStatus.LOADING
        self.bot_name: str = ""

    def init(self):
        """初始化启动器框架"""

    def launch(self) -> SystemExit:
        """启动器启动

        Raises:
            SystemError: 无法启动此启动器
        """
        self.update_status(SysStatus.LAUNCHING)
        fmts.print_inf("正在从 10132 端口连接到赞颂者...")
        utils.createThread(
            self.eulogist.start, thread_level=utils.ToolDeltaThread.SYSTEM
        )
        self.eulogist.launch_event.wait()
        self.update_status(SysStatus.RUNNING)
        self.eulogist.packet_listener = self.packet_handler_parent
        self.eulogist.set_listen_server_packets(list(self.need_listen_packets))
        self._exec_launched_listen_cbs()
        self.eulogist.exit_event.wait()
        self.update_status(SysStatus.NORMAL_EXIT)
        return SystemExit("赞颂者和 ToolDelta 断开连接")

    def get_players_info(self) -> dict[str, UnreadyPlayer]:
        # TODO: Can't get PlatformChatID and BuildPlatformID
        return {
            k: UnreadyPlayer(
                uuid=v.uuid,
                unique_id=v.uniqueID,
                name=v.name,
                xuid=v.xuid,
                platform_chat_id="",
                device_id=None,
                build_platform=0,
                # NOTE: this is dangerous
                abilities=Abilities.unmarshal(
                    v.abilities["Layers"][0]["Abilities"],
                    v.abilities["PlayerPermissions"],
                    v.abilities["CommandPermissions"],
                ),
            )
            for k, v in self.eulogist.uqs.items()
        }

    def get_bot_name(self) -> str:
        """获取机器人名字"""
        if self.bot_name == "":
            self.bot_name = self.eulogist.bot_name
        return self.bot_name

    def update_status(self, new_status: int) -> None:
        """更新启动器状态

        Args:
            new_status (int): 新的状态码
        """
        self.status = new_status
        if new_status in (SysStatus.NORMAL_EXIT, SysStatus.CRASHED_EXIT):
            self.exit_event.set()

    def packet_handler_parent(self, pkt_type: int, pkt: dict) -> None:
        """数据包处理器

        Args:
            pkt_type (str): 数据包类型
            pkt (dict): 数据包内容

        Raises:
            ValueError: 还未连接到游戏
        """
        if not self.eulogist.connected:
            raise ValueError("还未连接到游戏")
        self.dict_packet_handler(pkt_type, pkt)

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
            self.eulogist.sendcmd(cmd)
        else:
            if res := self.eulogist.sendcmd_with_resp(cmd, timeout):
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
            self.eulogist.sendwscmd(cmd)
        else:
            if res := self.eulogist.sendwscmd_with_resp(cmd, timeout):
                return res
            else:
                raise TimeoutError("获取命令返回超时")

    def sendwocmd(self, cmd: str) -> None:
        """以 wo 身份发送命令

        Args:
            cmd (str): 命令

        """
        self.eulogist.sendwocmd(cmd)

    def sendPacket(self, pckID: int, pck: dict | BaseBytesPacket) -> None:
        """发送数据包

        Args:
            pckID (int): 数据包 ID
            pck (dict | BaseBytesPacket): 数据包内容

        """
        if type(pck) is not dict:
            raise Exception("sendPacket: Bytes packet is not supported")
        self.eulogist.sendPacket(pckID, pck)

    sendPacketJson = sendPacket

    def is_op(self, player: str) -> bool:
        """检查玩家是否为 OP

        Args:
            player (str): 玩家名

        Returns:
            bool: 是否为 OP
        """
        if player not in self.eulogist.uqs.keys():
            raise ValueError(f"玩家不存在: {player}")
        return self.eulogist.uqs[player].abilities["CommandPermissions"] >= 3
