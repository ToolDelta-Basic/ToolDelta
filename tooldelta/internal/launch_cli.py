"""
客户端启动器框架
提供与游戏进行交互的标准接口
"""

import os
import platform
import shlex
import subprocess
import threading
import time
from collections.abc import Callable

from .. import utils
from ..cfg import Cfg
from ..constants import SysStatus, PacketIDS
from ..eulogist_libs import core_conn as eulogist_conn
from ..internal.types import UnreadyPlayer, Abilities
from ..neo_libs import file_download as neo_fd, neo_conn
from ..packets import Packet_CommandOutput
from ..utils import fmts, sys_args, urlmethod

Config = Cfg()


class StandardFrame:
    """提供了标准的启动器框架，作为 ToolDelta 和游戏交互的接口"""

    # 启动器类型
    launch_type = "Original"

    def __init__(self) -> None:
        """实例化启动器框架

        Args:
            serverNumber (int): 服务器号
            password (str): 服务器密码
            fbToken (str): 验证服务器 Token
            auth_server_url (str): 验证服务器地址
        """
        self.packet_handler = lambda pckType, pck: None
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

    def add_listen_packets(self, *pcks: PacketIDS) -> None:
        """添加需要监听的数据包"""
        for i in pcks:
            self.need_listen_packets.add(i)

    def reload_listen_packets(self, listen_packets: set[PacketIDS]) -> None:
        """重载需要监听的数据包ID"""
        self.need_listen_packets = {
            PacketIDS.Text,
            PacketIDS.PlayerList,
            PacketIDS.UpdateAbilities,
            PacketIDS.CommandOutput,
        } | listen_packets

    def set_packet_listener(self, handler: Callable[[int, dict], None]):
        self.packet_handler = handler

    def launch(self) -> None:
        """启动器启动

        Raises:
            SystemError: 无法启动此启动器
        """
        raise NotImplementedError

    def listen_launched(self, cbs: list[Callable[[], None]]) -> None:
        """设置监听启动器启动事件"""
        self._launcher_listeners.extend(cbs)

    def _exec_launched_listen_cbs(self):
        for cb in self._launcher_listeners:
            cb()

    def get_players_info(self) -> dict[str, UnreadyPlayer] | None:
        """
        获取启动器框架内存储的玩家信息
        如果框架无法存储, 则返回 None
        """
        raise NotImplementedError

    def get_bot_info(self) -> str:
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

    def sendPacket(self, pckID: int, pck: dict) -> None:
        """发送数据包

        Args:
            pckID (int): 数据包 ID
            pck (dict): 数据包内容

        Raises:
            NotImplementedError: 未实现此方法
        """
        raise NotImplementedError

    sendPacketJson = sendPacket


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

    def set_omega_conn(self, openat_port: int) -> str:
        """设置 Omega 连接

        Args:
            openat_port (int): 端口号

        Raises:
            bool: 是否启动成功
        """
        retries = 1
        self.omega.address = f"tcp://localhost:{openat_port}"
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
        exe_file_path = os.path.join(
            os.getcwd(), "tooldelta", "neo_libs", access_point_file
        )
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

    def _msg_show_thread(self) -> None:
        """显示来自 NeOmega 的信息"""
        if self.neomg_proc is None or self.neomg_proc.stdout is None:
            raise ValueError("接入点进程未启动")
        while True:
            msg_orig = self.neomg_proc.stdout.readline().strip("\n")
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
        openat_port = self.start_neomega_proc()
        utils.createThread(
            self._msg_show_thread,
            usage="显示来自 NeOmega接入点 的信息",
            thread_level=utils.ToolDeltaThread.SYSTEM,
        )
        if self.status != SysStatus.LAUNCHING:
            return SystemError("接入点无法连接到服务器")
        if (err_str := self.set_omega_conn(openat_port)) == "":
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
        self.exit_event.wait()
        if self.status == SysStatus.NORMAL_EXIT:
            return SystemExit("正常退出")
        if self.status == SysStatus.CRASHED_EXIT:
            return Exception("接入点进程已崩溃")
        return SystemError("未知的退出状态")

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

    def packet_handler_parent(self, pkt_type: str, pkt: dict) -> None:
        """数据包处理器

        Args:
            pkt_type (str): 数据包类型
            pkt (dict): 数据包内容

        Raises:
            ValueError: 未连接到接入点
        """
        if self.omega is None or self.packet_handler is None:
            raise ValueError("未连接到接入点")
        packetType: int = self.omega.get_packet_name_to_id_mapping(pkt_type)  # type: ignore
        self.packet_handler(packetType, pkt)

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

    def sendPacket(self, pckID: int, pck: dict) -> None:
        """发送数据包

        Args:
            pckID (int): 数据包 ID
            pck (dict): 数据包内容dict
        """
        self.check_avaliable()
        self.omega.send_game_packet_in_json_as_is(pckID, pck)

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


class FrameNeOmgAccessPointRemote(FrameNeOmgAccessPoint):
    """远程启动器框架 (使用 NeOmega接入点 框架的 Remote 连接)

    Args:
        FrameNeOmgAccessPoint (FrameNeOmgAccessPoint): FrameNeOmgAccessPoint 框架
    """

    launch_type = "NeOmegaAccessPoint Remote"

    def launch(self) -> SystemExit | Exception | SystemError:
        """启动远程启动器框架

        Raises:
            AssertionError: 端口号错误

        Returns:
            SystemExit | Exception | SystemError: 退出状态
        """
        try:
            openat_port = int(sys_args.sys_args_to_dict().get("access-point-port") or "24020")
            if openat_port not in range(65536):
                raise AssertionError
        except (ValueError, AssertionError):
            fmts.print_err("启动参数 -access-point-port 错误：不是 1~65535 的整数")
            raise SystemExit("端口参数错误")
        if openat_port == 0:
            fmts.print_war(
                "未用启动参数指定链接 neOmega 接入点开放端口，尝试使用默认端口 24015"
            )
            fmts.print_inf("可使用启动参数 -access-point-port 端口 以指定接入点端口。")
            openat_port = 24015
            return SystemExit("未指定端口号")
        fmts.print_inf(f"将从端口[{openat_port}]连接至游戏网络接入点, 等待接入中...")
        if (err_str := self.set_omega_conn(openat_port)) == "":
            self.update_status(SysStatus.RUNNING)
            self.start_wait_omega_disconn_thread()
            fmts.print_suc("已与接入点进程建立通信网络")
            pcks = []
            for i in self.need_listen_packets:
                try:
                    pcks.append(self.omega.get_packet_id_to_name_mapping(i))
                except KeyError:
                    fmts.print_war(f"无法监听数据包: {i}")
            self.omega.listen_packets(pcks, self.packet_handler_parent)
            self._exec_launched_listen_cbs()
            fmts.print_suc("ToolDelta 待命中")
        else:
            return SystemError(err_str)
        self.exit_event.wait()
        if self.status == SysStatus.NORMAL_EXIT:
            return SystemExit("正常退出。")
        if self.status == SysStatus.CRASHED_EXIT:
            return Exception(f"接入点已崩溃: {self.exit_reason}")
        return SystemError("未知的退出状态")


class FrameNeOmegaLauncher(FrameNeOmgAccessPoint):
    """混合使用ToolDelta和NeOmega启动器启动"""

    launch_type = "NeOmegaLauncher"

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
        self.launch_event = threading.Event()
        self.neomg_proc = None
        self.serverNumber = None
        self.neomega_account_opt = None
        self.bot_name = ""
        self.omega = neo_conn.ThreadOmega(
            connect_type=neo_conn.ConnectType.Remote,
            address="tcp://localhost:24013",
            accountOption=None,
        )
        self.serverNumber: int | None = None
        self.serverPassword: str | None = None
        self.fbToken: str | None = None
        self.auth_server: str | None = None

    def init(self):
        os.makedirs("NeOmega数据", exist_ok=True)
        if "no-download-neomega" not in sys_args.sys_args_to_dict().keys():
            fmts.print_inf("检测依赖库和NeOmega的最新版本..", end="\r")
            try:
                neo_fd.download_neomg()
            except Exception as err:
                raise SystemExit(f"ToolDelta 因下载库异常而退出: {err}") from err
            fmts.print_inf("检测依赖库和NeOmega的最新版本..完成")
        else:
            fmts.print_war("将不会自动检测依赖库和NeOmega的最新版本")
        neo_conn.load_lib()
        self.status = SysStatus.LAUNCHING

    def start_neomega_proc(self) -> int:
        """启动 NeOmega 进程

        Returns:
            int: 端口号
        """
        fmts.print_inf("正在获取空闲端口用于通信..", end="\n")
        free_port = urlmethod.get_free_port(24013)
        sys_machine = platform.uname().machine
        if sys_machine == "x86_64":
            sys_machine = "amd64"
        elif sys_machine == "aarch64":
            sys_machine = "arm64"
        access_point_file = (
            f"omega_launcher_{platform.uname().system.lower()}_{sys_machine}"
        )
        if "TERMUX_VERSION" in os.environ:
            access_point_file = f"omega_launcher_android_{sys_machine}"
        if platform.system() == "Windows":
            access_point_file += ".exe"
        exe_file_path = os.path.join(
            os.getcwd(), "tooldelta", "neo_libs", access_point_file
        )
        if platform.uname().system.lower() == "linux":
            os.system(f"chmod +x {shlex.quote(exe_file_path)}")
        # 只需要+x 即可
        if (
            isinstance(self.serverNumber, type(None))
            or isinstance(self.serverPassword, type(None))
            or isinstance(self.fbToken, type(None))
            or isinstance(self.auth_server, type(None))
        ):
            raise ValueError("未设置服务器号、密码、Token 或验证服务器地址")
        fmts.print_suc(f"将使用空闲端口 §f{free_port}§a 与接入点进行网络通信")
        fmts.print_suc(f"NeOmega 可执行文件路径: {exe_file_path}")
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
                "-storage-root",
                os.path.join(os.getcwd(), "NeOmega数据"),
            ],
            encoding="utf-8",
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
        )
        return free_port

    def _msg_handle_thread(self) -> None:
        """处理来自 NeOmega启动器 的信息"""
        if self.neomg_proc is None or self.neomg_proc.stdout is None:
            raise ValueError("NeOmega进程未启动")
        assert self.neomg_proc.stdin, "标准输入流不可用"
        buffer = ""
        auto_pass = False
        while True:
            char = self.neomg_proc.stdout.read(1)
            if self.neomg_proc.stderr is not None:
                err = self.neomg_proc.stderr.readlines()
                fmts.print_err("\n".join(err))
            if char == "":
                fmts.print_with_info("接入点进程已结束", "§b NOMG ")
                if self.status == SysStatus.LAUNCHING:
                    self.update_status(SysStatus.CRASHED_EXIT)
                break
            if char == "\n":
                msg_orig = buffer
                buffer = ""
                if msg_orig == "SIGNAL: exit":
                    fmts.print_with_info("接入点进程已结束", "§b NOMG ")
                    if self.status == SysStatus.LAUNCHING:
                        self.update_status(SysStatus.CRASHED_EXIT)
                    break
                if "[neOmega 接入点]: 就绪" in msg_orig:
                    self.launch_event.set()
                if msg_orig.startswith(tm_fmt := time.strftime("%H:%M ")):
                    msg_orig = msg_orig.removeprefix(tm_fmt)
                if any(
                    info_type in msg_orig
                    for info_type in [
                        "INFO",
                        "WARNING",
                        "ERROR",
                        "SUCCESS",
                        "\x1b[30;46m\x1b[30;46m      \x1b[0m\x1b[0m",
                    ]
                ):
                    msg_orig = (
                        msg_orig.replace("SUCCESS", "成功")
                        .replace("  ERROR  ", " 错误 ")
                        .replace(" WARNING ", " 警告 ")
                        .replace("  INFO  ", " 消息 ")
                        .strip(" ")
                    )
                    fmts.print_with_info("\b" + msg_orig, "")
                else:
                    fmts.print_with_info(msg_orig, "§b OMGL ")
            else:
                buffer += char
                # 自动通过相同配置文件启动
                if "要使用和上次完全相同的配置启动吗?" in buffer:
                    if not auto_pass:
                        auto_pass = True
                        self.input_to_neomega("")
                        fmts.print_inf(f"{buffer}, 已自动选择为 y")
                # 其他处理, 先独占输入通道, 等待用户输入
                elif (
                    "请输入 y" in buffer and "请输入 n:" in buffer and char != "\n"
                ) or ("请输入" in buffer and ":" in buffer and char != "\n"):
                    msg_orig = buffer.strip()
                    self.input_to_neomega(
                        input(fmts.fmt_info("\b" + msg_orig, "§6 输入 §r"))
                    )
                    buffer = ""

    def input_to_neomega(self, inputter: str) -> None:
        """写入文本到neomega进程"""
        if self.neomg_proc is None or self.neomg_proc.stdout is None:
            raise ValueError("NeOmega进程未启动")
        assert self.neomg_proc.stdin, "标准输入流不可用"
        self.neomg_proc.stdin.write(inputter + "\n")
        self.neomg_proc.stdin.flush()

    def launch(self) -> SystemExit | Exception | SystemError:
        """启动 NeOmega 进程

        returns:
            SystemExit: 正常退出
            Exception: 异常退出
            SystemError: 未知的退出状态
        """
        self.status = SysStatus.LAUNCHING
        openat_port = self.start_neomega_proc()
        fmts.print_load(
            f"NeOmega 数据存放位置: {os.path.join(os.getcwd(), 'tooldelta', 'NeOmega数据')}"
        )
        utils.createThread(
            self._msg_handle_thread,
            usage="处理来自 NeOmega启动器 的信息",
            thread_level=utils.ToolDeltaThread.SYSTEM,
        )
        self.launch_event.wait()
        self.set_omega_conn(openat_port)
        self.update_status(SysStatus.RUNNING)
        self.start_wait_omega_disconn_thread()
        fmts.print_suc("已获取游戏网络接入点最高权限")
        pcks = [
            self.omega.get_packet_id_to_name_mapping(i)
            for i in self.need_listen_packets
        ]
        self.omega.listen_packets(pcks, self.packet_handler_parent)
        self._exec_launched_listen_cbs()
        fmts.print_suc("接入点注入已就绪")
        self.exit_event.wait()  # 等待事件的触发
        if self.status == SysStatus.NORMAL_EXIT:
            return SystemExit("正常退出")
        if self.status == SysStatus.CRASHED_EXIT:
            return Exception("接入点进程已崩溃")
        return SystemError("未知的退出状态")


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
        self.eulogist = eulogist_conn.Eulogist()
        self.need_listen_packets: set[int] = {9, 63, 79}
        self._launch_listeners: list[Callable[[], None]]
        self.exit_event = threading.Event()
        self.status: int = SysStatus.LOADING
        self.bot_name: str = ""

    def init(self):
        """初始化启动器框架"""

    def add_listen_packets(self, *pcks: int) -> None:
        """添加需要监听的数据包"""
        for i in pcks:
            self.need_listen_packets.add(i)

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
            k: UnreadyPlayer(v.uuid, v.uniqueID, v.name, v.xuid, "", 0)
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
        self.packet_handler(pkt_type, pkt)

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

    def sendPacket(self, pckID: int, pck: dict) -> None:
        """发送数据包

        Args:
            pckID (int): 数据包 ID
            pck (str): 数据包内容

        """
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


FrameNeOmg = FrameNeOmgAccessPoint
FrameNeOmgRemote = FrameNeOmgAccessPointRemote
FrameEulogist = FrameEulogistLauncher

FB_LIKE_LAUNCHERS = (
    FrameNeOmegaLauncher
    | FrameNeOmgAccessPoint
    | FrameNeOmgAccessPointRemote
    | FrameEulogistLauncher
)

"类FastBuilder启动器框架"
LAUNCHERS = FB_LIKE_LAUNCHERS
"所有类型的启动器"
