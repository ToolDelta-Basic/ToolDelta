import threading
from collections.abc import Callable

from ...constants import SysStatus, PacketIDS
from ...packets import Packet_CommandOutput
from ...mc_bytes_packet.base_bytes_packet import BaseBytesPacket
from ..packet_handler import PacketHandler
from ..types import UnreadyPlayer
from .neo_libs.blob_hash.blob_hash_holder import BlobHashHolder


class StandardFrame:
    """
    提供了标准的启动器框架，作为 ToolDelta 和游戏交互的接口
    新增的启动框架都应为此类的子类, 并实现和覆写所有 NotImplemented 的内容
    """

    # 启动器类型
    launch_type = "Original"

    def __init__(self) -> None:
        """实例化启动器框架"""
        self.dict_packet_handler = lambda pckType, pck: None
        self.bytes_packet_handler = lambda pckType, pck: None
        self.need_listen_packets: set[PacketIDS] = {
            PacketIDS.Text,
            PacketIDS.PlayerList,
            PacketIDS.UpdateAbilities,
            PacketIDS.CommandOutput,
        }
        self.exit_event = threading.Event()
        self.status: SysStatus = SysStatus.LOADING
        self._launcher_listeners: list[Callable[[], None]] = []

    def init(self):
        """初始化启动器框架"""

    def reload_listen_packets(self, listen_packets: set[PacketIDS]) -> None:
        """重载需要监听的数据包ID"""
        self.need_listen_packets = {
            PacketIDS.Text,
            PacketIDS.PlayerList,
            PacketIDS.UpdateAbilities,
            PacketIDS.CommandOutput,
        } | listen_packets

    def set_packet_listener(self, handler: PacketHandler):
        self.dict_packet_handler = handler.entrance_dict_packet
        self.bytes_packet_handler = handler.entrance_bytes_packet
        self.need_listen_packets |= handler.listen_packets

    def launch(self) -> None:
        """启动器启动

        Raises:
            SystemError: 无法启动此启动器
        """
        raise NotImplementedError

    def listen_launched(self, cbs: list[Callable[[], None]]) -> None:
        """设置监听启动器启动事件"""
        self._launcher_listeners.extend(cbs)

    def wait_crashed(self):
        self.exit_event.wait()

    def _exec_launched_listen_cbs(self):
        for cb in self._launcher_listeners:
            cb()

    def get_players_info(self) -> dict[str, UnreadyPlayer] | None:
        """
        获取启动器框架内存储的玩家信息
        如果框架无法存储, 则返回 None
        """
        raise NotImplementedError

    def get_bot_name(self) -> str:
        """获取机器人名字"""
        raise NotImplementedError

    def update_status(self, new_status: SysStatus) -> None:
        """更新启动器状态

        Args:
            new_status (int): 新的状态码
        """
        self.status = new_status
        if new_status in (SysStatus.NORMAL_EXIT, SysStatus.CRASHED_EXIT):
            self.exit_event.set()

    def sendcmd(
        self, cmd: str, waitForResp: bool = False, timeout: float = 30
    ) -> Packet_CommandOutput | None:
        """以玩家身份发送命令

        Args:
            cmd (str): 命令
            waitForResp (bool, optional): 是否等待结果
            timeout (int | float, optional): 超时时间

        Raises:
            NotImplementedError: 未实现此方法

        Returns:
            Optional[Packet_CommandOutput]: 返回命令结果
        """
        raise NotImplementedError

    def sendwscmd(
        self, cmd: str, waitForResp: bool = False, timeout: float = 30
    ) -> Packet_CommandOutput | None:
        """以 ws 身份发送命令

        Args:
            cmd (str): 命令
            waitForResp (bool, optional): 是否等待结果
            timeout (int | float, optional): 超时时间

        Raises:
            NotImplementedError: 未实现此方法

        Returns:
            Optional[Packet_CommandOutput]: 返回命令结果
        """
        raise NotImplementedError

    def sendwocmd(self, cmd: str) -> None:
        """以 wo 身份发送命令

        Args:
            cmd (str): 命令

        Raises:
            NotImplementedError: 未实现此方法
        """
        raise NotImplementedError

    def sendPacket(self, pckID: int, pck: dict | BaseBytesPacket) -> None:
        """发送数据包

        Args:
            pckID (int): 数据包 ID
            pck (dict | | BaseBytesPacket): 数据包内容

        Raises:
            NotImplementedError: 未实现此方法
        """
        raise NotImplementedError

    def blobHashHolder(self) -> BlobHashHolder:
        """blobHashHolder 返回 ToolDelta 的 Blob hash cache 缓存数据集的持有人

        Returns:
            BlobHashHolder: ToolDelta 的 Blob hash cache 缓存数据集的持有人

        Raises:
            NotImplementedError: 未实现此方法
        """
        raise NotImplementedError

    sendPacketJson = sendPacket
