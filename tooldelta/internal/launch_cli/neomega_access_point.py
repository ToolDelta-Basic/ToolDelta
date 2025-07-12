import os
import platform
import shlex
import subprocess
import threading
import time

from ...mc_bytes_packet.pool import bytes_packet_by_id
from ... import utils
from ...constants import SysStatus, PacketIDS
from ...packets import Packet_CommandOutput
from ...mc_bytes_packet.base_bytes_packet import BaseBytesPacket
from ...utils import fmts, sys_args, urlmethod
from ..types import UnreadyPlayer, Abilities
from .standard_launcher import StandardFrame
from .neo_libs import file_download as neo_fd, neo_conn
from .neo_libs.neo_conn import LIB as _Library
from .neo_libs.blob_hash.blob_hash_holder import (
    BlobHashHolder,
)


class FrameNeOmgAccessPoint(StandardFrame):
    """使用 NeOmega接入点 框架连接到游戏"""

    launch_type = "NeOmegaAccessPoint"

    def __init__(self) -> None:
        """初始化 NeOmega 框架

        Args:
            serverNumber (int): 服务器号
            password (str): 服务器密码
            fbToken (str): 验证服务器 Token
            auth_server (str): 验证服务器地址
        """
        super().__init__()
        self.status = SysStatus.LOADING
        self.neomg_proc = None
        self.serverNumber = None
        self.neomega_account_opt = None
        self.bot_name = ""
        self.omega = neo_conn.ThreadOmega(
            connect_type=neo_conn.ConnectType.Remote,
            address="tcp://localhost:24013",
            accountOption=None,
        )
        self.blob_hash_holder = BlobHashHolder(self.omega)
        self.serverNumber: int | None = None
        self.serverPassword: str | None = None
        self.fbToken: str | None = None
        self.auth_server: str | None = None
        self.exit_reason = ""

    def init(self):
        if "no-download-libs" not in sys_args.sys_args_to_dict().keys():
            fmts.print_inf("检测接入点和依赖库的最新版本..", end="\r")
            try:
                neo_fd.download_libs()
            except Exception as err:
                raise SystemExit(f"ToolDelta 因下载库异常而退出: {err}") from err
            fmts.print_inf("检测接入点和依赖库的最新版本..完成")
        else:
            fmts.print_war("将不会自动检测接入点依赖库的最新版本")
        neo_conn.load_lib()
        self.status = SysStatus.LAUNCHING

    def set_launch_data(
        self, serverNumber: int, password: str, fbToken: str, auth_server_url: str
    ):
        self.serverNumber = serverNumber
        self.serverPassword = password
        self.fbToken = fbToken
        self.auth_server = auth_server_url
        if self.serverNumber is None:
            self.neomega_account_opt = None
        else:
            self.neomega_account_opt = neo_conn.AccountOptions(
                AuthServer=self.auth_server,
                UserToken=self.fbToken,
                ServerCode=str(self.serverNumber),
                ServerPassword=self.serverPassword,
            )

    def set_omega_conn(self, addr: str) -> str:
        """设置 Omega 连接

        Args:
            openat_port (int): 端口号

        Raises:
            bool: 是否启动成功
        """
        retries = 1
        self.omega.address = addr
        MAX_RETRIES = 5  # 最大重试次数

        while retries <= MAX_RETRIES:
            try:
                self.omega.connect()
                retries = 1
                return ""
            except Exception as err:
                if self.status != SysStatus.LAUNCHING:
                    self.update_status(SysStatus.CRASHED_EXIT)
                    return "接入点无法连接"
                if "api not exist" in str(err):
                    fmts.print_inf("等待接入点连接中..", end="\r")
                    time.sleep(5)
                else:
                    fmts.print_war(f"OMEGA 连接失败: {err} (第{retries}次)")
                    time.sleep(5)
                    retries += 1
        fmts.print_err("最大重试次数已超过")
        self.update_status(SysStatus.CRASHED_EXIT)
        return "连接超时"

    def start_neomega_proc(self) -> int:
        """启动 NeOmega 进程

        Returns:
            int: 端口号
        """
        free_port = urlmethod.get_free_port(24013)
        sys_machine = platform.uname().machine
        if sys_machine == "x86_64":
            sys_machine = "amd64"
        elif sys_machine == "aarch64":
            sys_machine = "arm64"
        access_point_file = (
            f"neomega_{platform.uname().system.lower()}_access_point_{sys_machine}"
        )
        if "TERMUX_VERSION" in os.environ:
            access_point_file = f"neomega_android_access_point_{sys_machine}"
        if platform.system() == "Windows":
            access_point_file += ".exe"
        exe_file_path = os.path.join(os.getcwd(), "tooldelta", "bin", access_point_file)
        if platform.uname().system.lower() == "linux":
            os.system(f"chmod +x {shlex.quote(exe_file_path)}")
        # 只需要+x 即可
        if (
            self.serverNumber is None
            or self.serverPassword is None
            or self.fbToken is None
            or self.auth_server is None
        ):
            raise ValueError("未设置服务器号、密码、Token 或验证服务器地址")
        fmts.print_suc(f"将使用空闲端口 §f{free_port}§a 与接入点进行网络通信")
        self.neomg_proc = subprocess.Popen(
            [
                exe_file_path,
                "-server",
                str(self.serverNumber),
                "-T",
                self.fbToken,
                "-access-point-addr",
                f"tcp://localhost:{free_port}",
                "-server-password",
                str(self.serverPassword),
                "-auth-server",
                self.auth_server,
            ],
            encoding="utf-8",
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        return free_port

    @utils.thread_func(
        "NeOmega 信息显示线程", thread_level=utils.ToolDeltaThread.SYSTEM
    )
    def _msg_show_thread(self, launch_event: threading.Event) -> None:
        """显示来自 NeOmega 的信息"""
        if self.neomg_proc is None or self.neomg_proc.stdout is None:
            raise ValueError("接入点进程未启动")
        while True:
            msg_orig = self.neomg_proc.stdout.readline().strip("\n")
            if "机器人已获得操作员权限" in msg_orig:
                launch_event.set()
            if msg_orig in ("", "SIGNAL: exit"):
                fmts.print_with_info("接入点进程已结束", "§b NOMG ")
                if self.status == SysStatus.LAUNCHING:
                    self.update_status(SysStatus.CRASHED_EXIT)
                break
            fmts.print_with_info(msg_orig, "§b NOMG ")

    def launch(self) -> SystemExit | Exception | SystemError:
        """启动 NeOmega 进程

        returns:
            SystemExit: 正常退出
            Exception: 异常退出
            SystemError: 未知的退出状态
        """
        self.status = SysStatus.LAUNCHING
        self.exit_event = threading.Event()
        self.omega = neo_conn.ThreadOmega(
            connect_type=neo_conn.ConnectType.Remote,
            address="tcp://localhost:24013",
            accountOption=self.neomega_account_opt,
        )
        self.blob_hash_holder = BlobHashHolder(self.omega)
        openat_port = self.start_neomega_proc()
        launch_event = threading.Event()
        self._msg_show_thread(launch_event)
        if self.status != SysStatus.LAUNCHING:
            return SystemError("接入点无法连接到服务器")
        fmts.print_inf("等待接入点就绪..")
        while not launch_event.wait(timeout=1):
            if self.exit_event.is_set():
                return SystemError("NeOmage 启动出现问题.")
            pass
        fmts.print_suc("接入点已就绪")
        if (err_str := self.set_omega_conn(f"tcp://127.0.0.1:{openat_port}")) == "":
            self.update_status(SysStatus.RUNNING)
            self.start_wait_omega_disconn_thread()
            fmts.print_suc("接入点框架通信网络连接成功")
            pcks = [
                self.omega.get_packet_id_to_name_mapping(i)
                for i in self.need_listen_packets
            ]
            self.omega.listen_packets(pcks, self.packet_handler_parent)
            self._exec_launched_listen_cbs()
        else:
            return SystemError(err_str)
        self.update_status(SysStatus.RUNNING)
        self.wait_crashed()
        if self.status == SysStatus.NORMAL_EXIT:
            return SystemExit("正常退出")
        if self.status == SysStatus.CRASHED_EXIT:
            return Exception("接入点进程已崩溃")
        return SystemError("未知的退出状态")

    def get_neomega_library(self):
        return _Library

    def get_players_info(self):
        players_data: dict[str, UnreadyPlayer] = {}
        if self.status != SysStatus.RUNNING:
            raise ValueError("未连接到接入点")
        for i in self.omega.get_all_online_players():
            if i is not None:
                ab = Abilities(
                    i.can_build,
                    i.can_mine,
                    i.can_doors_and_switches,
                    i.can_open_containers,
                    i.can_attack_players,
                    i.can_attack_mobs,
                    i.can_operator_commands,
                    i.can_teleport,
                    0,  # TODO: player_permission 现在固定为 0
                    3 if i.op else 1,  # TODO: 除非玩家为 OP, 否则命令等级恒为 1
                )
                players_data[i.name] = UnreadyPlayer(
                    i.uuid,
                    i.entity_unique_id,
                    i.name,
                    i.uuid[-8:],
                    i.platform_chat_id,
                    i.device_id,
                    i.build_platform,
                    abilities=ab,
                )
            else:
                raise ValueError("未能获取玩家名和 UUID")
        return players_data

    def get_bot_name(self) -> str:
        """获取机器人名字

        Returns:
            str: 机器人名字
        """
        self.check_avaliable()
        if not self.bot_name:
            self.bot_name = self.omega.get_bot_basic_info().BotName
        return self.bot_name

    def packet_handler_parent(self, pkt_type: str, pkt: dict | bytes) -> None:
        """数据包处理器

        Args:
            pkt_type (str): 数据包类型
            pkt (dict): 数据包内容

        Raises:
            ValueError: 未连接到接入点
        """
        if (
            self.omega is None
            or self.dict_packet_handler is None
            or self.bytes_packet_handler is None
        ):
            raise ValueError("未连接到接入点")

        pkID: int = self.omega.get_packet_name_to_id_mapping(pkt_type)  # type: ignore
        if type(pkt) is dict:
            self.dict_packet_handler(pkID, pkt)
        elif type(pkt) is bytes:
            real_pkt = bytes_packet_by_id(pkID)
            real_pkt.decode(pkt)
            self.bytes_packet_handler(pkID, real_pkt)

    def check_avaliable(self):
        if self.status != SysStatus.RUNNING:
            raise ValueError("未连接到游戏")

    def sendcmd(
        self, cmd: str, waitForResp: bool = False, timeout: float = 30
    ) -> Packet_CommandOutput | None:
        """以玩家身份发送命令

        Args:
            cmd (str): 命令
            waitForResp (bool, optional): 是否等待结果
            timeout (int | float, optional): 超时时间

        Returns:
            Optional[Packet_CommandOutput]: 返回命令结果
        """
        self.check_avaliable()
        if waitForResp:
            res = self.omega.send_player_command_need_response(cmd, timeout)
            if res is None:
                raise TimeoutError("指令超时")
            return res
        self.omega.send_player_command_omit_response(cmd)
        return None

    def sendwscmd(
        self, cmd: str, waitForResp: bool = False, timeout: float = 30
    ) -> Packet_CommandOutput | None:
        """以玩家身份发送命令

        Args:
            cmd (str): 命令
            waitForResp (bool, optional): 是否等待结果
            timeout (int | float, optional): 超时时间

        Returns:
            Optional[Packet_CommandOutput]: 返回命令结果
        """
        self.check_avaliable()
        if waitForResp:
            res = self.omega.send_websocket_command_need_response(cmd, timeout)
            if res is None:
                raise TimeoutError(f"指令超时: {cmd}")
            return res
        self.omega.send_websocket_command_omit_response(cmd)
        return None

    def sendwocmd(self, cmd: str) -> None:
        """以 wo 身份发送命令

        Args:
            cmd (str): 命令

        Raises:
            NotImplementedError: 未实现此方法
        """
        self.check_avaliable()
        self.omega.send_settings_command(cmd)

    def sendPacket(self, pckID: int, pck: dict | BaseBytesPacket) -> None:
        """发送数据包

        Args:
            pckID (int): 数据包 ID
            pck (dict | BaseBytesPacket): 数据包内容dict
        """
        self.check_avaliable()
        if isinstance(pck, BaseBytesPacket):
            self.omega.send_game_packet_in_bytes(pckID, pck.encode())
        else:
            self.omega.send_game_packet_in_json_as_is(pckID, pck)

    def blobHashHolder(self) -> BlobHashHolder:
        """blobHashHolder 返回当前结点的 Blob hash cache 缓存数据集的持有人

        Returns:
            BlobHashHolder: 当前结点的 Blob hash cache 缓存数据集的持有人
        """
        return self.blob_hash_holder

    def place_command_block_with_nbt_data(
        self,
        block_name: str,
        block_states: str,
        position: tuple[int, int, int],
        nbt_data: neo_conn.CommandBlockNBTData,
    ):
        """在 position 放置方块名为 block_name 且方块状态为 block_states 的命令块，
        同时向该方块写入 nbt_data 所指代的 NBT 数据

        Args:
            block_name (str): 命令块的方块名，如 chain_command_block
            block_states (str): 命令块的方块状态，如 朝向南方 的命令方块表示为 ["facing_direction":3]
            position (tuple[int, int, int]): 命令块应当被放置的位置。三元整数元组从左到右依次对应世界坐标的 X, Y, Z 轴坐标
            nbt_data (neo_conn.CommandBlockNBTData): 该命令块的原始 NBT 数据

        Raises:
            NotImplementedError: 未实现此方法
        """
        self.check_avaliable()
        self.omega.place_command_block(
            neo_conn.CommandBlockPlaceOption(
                X=position[0],
                Y=position[1],
                Z=position[2],
                BlockName=block_name,
                BockState=block_states,
                NeedRedStone=(not nbt_data.ConditionalMode),
                Conditional=nbt_data.ConditionalMode,
                Command=nbt_data.Command,
                Name=nbt_data.CustomName,
                TickDelay=nbt_data.TickDelay,
                ShouldTrackOutput=nbt_data.TrackOutput,
                ExecuteOnFirstTick=nbt_data.ExecuteOnFirstTick,
            )
        )

    @utils.thread_func("检测 Omega 断开连接线程", utils.ToolDeltaThread.SYSTEM)
    def start_wait_omega_disconn_thread(self):
        self.exit_reason = self.omega.wait_disconnect()
        if self.status == SysStatus.RUNNING:
            self.update_status(SysStatus.CRASHED_EXIT)

    def reload_listen_packets(self, listen_packets: set[PacketIDS]) -> None:
        super().reload_listen_packets(listen_packets)
        pcks = [
            self.omega.get_packet_id_to_name_mapping(i)
            for i in self.need_listen_packets
        ]
        self.omega.listen_packets(pcks, self.packet_handler_parent)

    sendPacketJson = sendPacket
