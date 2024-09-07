"""客户端启动器框架"""

import hashlib
import os
import platform
import queue
import shlex
import subprocess
import sys
import threading
import time
from collections.abc import Callable

import tooldelta

from .cfg import Cfg
from .color_print import Print
from .neo_libs import file_download as neo_fd
from .neo_libs import neo_conn
from .packets import Packet_CommandOutput
from .sys_args import sys_args_to_dict
from .urlmethod import get_free_port
from .utils import Utils

Config = Cfg()


class SysStatus:
    """系统状态码

    LOADING: 启动器正在加载
    LAUNCHING: 启动器正在启动
    RUNNING: 启动器正在运行
    NORMAL_EXIT: 正常退出
    FB_LAUNCH_EXC: FastBuilder 启动异常
    CRASHED_EXIT: 启动器崩溃退出
    NEED_RESTART: 需要重启
    """

    LOADING = 100
    LAUNCHING = 101
    RUNNING = 102
    NORMAL_EXIT = 103
    FB_LAUNCH_EXC = 104
    CRASHED_EXIT = 105
    NEED_RESTART = 106
    launch_type = "None"


class StandardFrame:
    """提供了标准的启动器框架，作为 ToolDelta 和游戏交互的接口"""

    launch_type = "Original"

    def __init__(self) -> None:
        """实例化启动器框架

        Args:
            serverNumber (int): 服务器号
            password (str): 服务器密码
            fbToken (str): 验证服务器 Token
            auth_server_url (str): 验证服务器地址
        """
        self.system_type = platform.uname().system
        self.inject_events: list = []
        self.packet_handler: Callable = lambda pckType, pck: None
        self.need_listen_packets: set[int] = {9, 63, 79}
        self._launcher_listener: Callable
        self.exit_event = threading.Event()
        self.status: int = SysStatus.LOADING

    def init(self):
        """初始化启动器框架"""

    def add_listen_packets(self, *pcks: int) -> None:
        """添加需要监听的数据包"""
        for i in pcks:
            self.need_listen_packets.add(i)

    def reload_listen_packets(self, listen_packets: set[int]) -> None:
        """重载"""
        self.need_listen_packets = {9, 79, 63} | listen_packets

    def launch(self) -> None:
        """启动器启动

        Raises:
            SystemError: 无法启动此启动器
        """
        raise NotImplementedError

    def listen_launched(self, cb: Callable) -> None:
        """设置监听启动器启动事件"""
        self._launcher_listener = cb

    def get_players_and_uuids(self) -> None:
        """获取玩家名和 UUID"""
        raise NotImplementedError

    def get_bot_name(self) -> str:
        """获取机器人名字"""
        raise NotImplementedError

    def update_status(self, new_status: int) -> None:
        """更新启动器状态

        Args:
            new_status (int): 新的状态码
        """
        self.status = new_status
        if new_status == SysStatus.NORMAL_EXIT:
            self.exit_event.set()
            tooldelta.safe_jump()
        if new_status == SysStatus.CRASHED_EXIT:
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

    def sendPacket(self, pckID: int, pck: str) -> None:
        """发送数据包

        Args:
            pckID (int): 数据包 ID
            pck (str): 数据包内容

        Raises:
            NotImplementedError: 未实现此方法
        """
        raise NotImplementedError

    sendPacketJson = sendPacket

    def is_op(self, player: str) -> bool:
        """检查玩家是否为 OP

        Args:
            player (str): 玩家名

        Raises:
            NotImplementedError: 未实现此方法

        Returns:
            bool: 是否为 OP
        """
        raise NotImplementedError

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
        raise NotImplementedError


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

    def init(self):
        if "no-download-libs" not in sys_args_to_dict().keys():
            Print.print_inf("检测接入点和依赖库的最新版本..", end="\r")
            try:
                neo_fd.download_libs()
            except Exception as err:
                raise SystemExit(f"ToolDelta 因下载库异常而退出: {err}") from err
            Print.print_inf("检测接入点和依赖库的最新版本..完成")
        else:
            Print.print_war("将不会自动检测接入点依赖库的最新版本")
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

    def set_omega_conn(self, openat_port: int) -> None:
        """设置 Omega 连接

        Args:
            openat_port (int): 端口号

        Raises:
            SystemExit: 系统退出
        """
        retries = 1
        self.omega.address = f"tcp://localhost:{openat_port}"
        MAX_RETRIES = 5  # 最大重试次数

        while retries <= MAX_RETRIES:
            try:
                self.omega.connect()
                retries = 1
                return
            except Exception as err:
                Print.print_war(f"OMEGA 连接失败第 {err} (第{retries}次)")
                time.sleep(5)
                retries += 1
        Print.print_err("最大重试次数已超过")
        self.update_status(SysStatus.CRASHED_EXIT)

    def start_neomega_proc(self) -> int:
        """启动 NeOmega 进程

        Returns:
            int: 端口号
        """
        free_port = get_free_port(24013)
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
        Print.print_suc(f"将使用空闲端口 §f{free_port}§a 与接入点进行网络通信")
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
                Print.print_with_info("接入点进程已结束", "§b NOMG ")
                if self.status == SysStatus.LAUNCHING:
                    self.update_status(SysStatus.CRASHED_EXIT)
                break
            if "[neOmega 接入点]: 就绪" in msg_orig:
                self.launch_event.set()
            Print.print_with_info(msg_orig, "§b NOMG ")

    def launch(self) -> SystemExit | Exception | SystemError:
        """启动 NeOmega 进程

        returns:
            SystemExit: 正常退出
            Exception: 异常退出
            SystemError: 未知的退出状态
        """
        self.status = SysStatus.LAUNCHING
        self.launch_event = threading.Event()
        self.exit_event = threading.Event()
        self.omega = neo_conn.ThreadOmega(
            connect_type=neo_conn.ConnectType.Remote,
            address="tcp://localhost:24013",
            accountOption=self.neomega_account_opt,
        )
        openat_port = self.start_neomega_proc()
        Utils.createThread(
            self._msg_show_thread,
            usage="显示来自 NeOmega接入点 的信息",
            thread_level=Utils.ToolDeltaThread.SYSTEM,
        )
        self.omega.reset_omega_status()
        self.launch_event.wait()
        self.set_omega_conn(openat_port)
        self.update_status(SysStatus.RUNNING)
        self.wait_omega_disconn_thread()
        Print.print_suc("已获取游戏网络接入点最高权限")
        pcks = [
            self.omega.get_packet_id_to_name_mapping(i)
            for i in self.need_listen_packets
        ]
        self.omega.listen_packets(pcks, self.packet_handler_parent)
        self._launcher_listener()
        Print.print_suc("接入点注入已就绪")
        self.exit_event.wait()
        if self.status == SysStatus.NORMAL_EXIT:
            return SystemExit("正常退出")
        if self.status == SysStatus.CRASHED_EXIT:
            return Exception("接入点进程已崩溃")
        return SystemError("未知的退出状态")

    def get_players_and_uuids(self):
        players_uuid = {}
        if self.status != SysStatus.RUNNING:
            raise ValueError("未连接到接入点")
        for i in self.omega.get_all_online_players():
            if i is not None:
                players_uuid[i.name] = i.uuid
            else:
                raise ValueError("未能获取玩家名和 UUID")
        return players_uuid

    def get_bot_name(self) -> str:
        """获取机器人名字

        Returns:
            str: 机器人名字
        """
        self.check_avaliable()
        if not self.bot_name:
            self.bot_name = self.omega.get_bot_name()
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
        packetType = self.omega.get_packet_name_to_id_mapping(pkt_type)
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

        Raises:
            NotImplementedError: 未实现此方法

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

        Raises:
            NotImplementedError: 未实现此方法

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

    def is_op(self, player: str) -> bool:
        """检查玩家是否为 OP

        Args:
            player (str): 玩家名

        Raises:
            NotImplementedError: 未实现此方法

        Returns:
            bool: 是否为 OP
        """
        self.check_avaliable()
        if player not in (allplayers := [i.name for i in self.omega.get_all_online_players()]):
            raise ValueError(f"玩家 '{player}' 不处于全局玩家中 (全局玩家: " + ", ".join(allplayers) + ")")
        player_obj = self.omega.get_player_by_name(player)
        if isinstance(player_obj, type(None)) or isinstance(player_obj.op, type(None)):
            raise ValueError("未能获取玩家对象")
        return player_obj.op

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

    @Utils.thread_func("检测 Omega 断开连接线程", Utils.ToolDeltaThread.SYSTEM)
    def wait_omega_disconn_thread(self):
        self.omega.wait_disconnect()
        if self.status == SysStatus.RUNNING:
            self.update_status(SysStatus.CRASHED_EXIT)

    def reload_listen_packets(self, listen_packets: set[int]) -> None:
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
            openat_port = int(sys_args_to_dict().get("access-point-port") or "24020")
            if openat_port not in range(65536):
                raise AssertionError
        except (ValueError, AssertionError):
            Print.print_err("启动参数 -access-point-port 错误：不是 1~65535 的整数")
            raise SystemExit("端口参数错误")
        if openat_port == 0:
            Print.print_war(
                "未用启动参数指定链接 neOmega 接入点开放端口，尝试使用默认端口 24015"
            )
            Print.print_inf("可使用启动参数 -access-point-port 端口 以指定接入点端口。")
            openat_port = 24015
            return SystemExit("未指定端口号")
        Print.print_inf(f"将从端口[{openat_port}]连接至游戏网络接入点, 等待接入中...")
        self.set_omega_conn(openat_port)
        self.update_status(SysStatus.RUNNING)
        self.wait_omega_disconn_thread()
        Print.print_suc("已与接入点进程建立通信网络")
        pcks = [
            self.omega.get_packet_id_to_name_mapping(i)
            for i in self.need_listen_packets
        ]
        self.omega.listen_packets(pcks, self.packet_handler_parent)
        self._launcher_listener()
        Print.print_suc("ToolDelta 待命中")
        self.exit_event.wait()
        if self.status == SysStatus.NORMAL_EXIT:
            return SystemExit("正常退出。")
        if self.status == SysStatus.CRASHED_EXIT:
            return Exception("接入点已崩溃")
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
        self.neomega_msg_queue = queue.Queue()
        self.neomega_input_queue = queue.Queue()
        self.input_msg: list = []
        self.out_speed: float = 0.002

    def init(self):
        os.makedirs("NeOmega数据", exist_ok=True)
        if "no-download-neomega" not in sys_args_to_dict().keys():
            Print.print_inf("检测依赖库和NeOmega的最新版本..", end="\r")
            try:
                neo_fd.download_neomg()
            except Exception as err:
                raise SystemExit(f"ToolDelta 因下载库异常而退出: {err}") from err
            Print.print_inf("检测依赖库和NeOmega的最新版本..完成")
        else:
            Print.print_war("将不会自动检测依赖库和NeOmega的最新版本")
        neo_conn.load_lib()
        self.status = SysStatus.LAUNCHING

    def start_neomega_proc(self) -> int:
        """启动 NeOmega 进程

        Returns:
            int: 端口号
        """
        free_port = get_free_port(24013)
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
        Print.print_suc(f"将使用空闲端口 §f{free_port}§a 与接入点进行网络通信")
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

    def get_text_md5(self, text: str) -> str:
        """计算字符串的MD5值"""
        md5 = hashlib.md5()
        md5.update(text.encode("utf-8"))
        unique_md5 = md5.hexdigest()
        return unique_md5

    def put_msg_to_queue(self, msg: str, out_type: bool = True) -> str:
        """将元组放入消息队列"""
        self.neomega_msg_queue.put_nowait(
            ("out" if out_type else "in", self.get_text_md5(msg), msg)
        )
        return self.get_text_md5(msg)

    def get_input(self, md5: str) -> str:
        while True:
            if not self.input_msg:
                continue
            for in_tuple in self.input_msg:
                if in_tuple[0] == md5:
                    return in_tuple[1]

    def _msg_handle_thread(self) -> None:
        """处理来自 NeOmega 的信息"""
        if self.neomg_proc is None or self.neomg_proc.stdout is None:
            raise ValueError("NeOmega进程未启动")
        assert self.neomg_proc.stdin
        Print.print_load(
            f"NeOmega 进程输出速度限制: {int(1.0 / self.out_speed)!s} 条/秒"
        )
        buffer = ""
        while True:
            char = self.neomg_proc.stdout.read(1)
            if self.neomg_proc.stderr is not None:
                err = self.neomg_proc.stderr.readlines()
                Print.print_err("\n".join(err))
            if char == "":
                Print.print_with_info("接入点进程已结束", "§b NOMG ")
                if self.status == SysStatus.LAUNCHING:
                    self.update_status(SysStatus.CRASHED_EXIT)
                break
            if char == "\n":
                msg_orig = buffer.strip()
                buffer = ""
                if msg_orig == "SIGNAL: exit":
                    Print.print_with_info("接入点进程已结束", "§b NOMG ")
                    if self.status == SysStatus.LAUNCHING:
                        self.update_status(SysStatus.CRASHED_EXIT)
                    break
                if "[neOmega 接入点]: 就绪" in msg_orig:
                    self.launch_event.set()
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
                        .replace("  ERROR  ", "错误")
                        .replace("WARNING", "警告")
                        .replace("  INFO  ", "消息")
                        .strip(" ")
                    )
                    self.put_msg_to_queue(Print.fmt_info("\b" + msg_orig, ""))
                else:
                    self.put_msg_to_queue(Print.fmt_info(msg_orig, "§b NOMG "))
            else:
                buffer += char
                if (
                    "请输入 y" in buffer
                    and "请输入 n:" in buffer
                    and char != "\n"
                    or ("请输入" in buffer and ":" in buffer and char != "\n")
                ):
                    msg_orig = buffer.strip()
                    md5 = self.put_msg_to_queue(
                        Print.fmt_info("\b" + msg_orig, ""), False
                    )
                    self.neomg_proc.stdin.write(f"{self.get_input(md5).lower()}\n")
                    self.neomg_proc.stdin.flush()
                    buffer = ""

    def _msg_show_thread(self) -> None:
        """显示来自 NeOmega 的信息"""
        while True:
            if not self.neomega_msg_queue.empty():
                time.sleep(self.out_speed)
                Message: tuple = self.neomega_msg_queue.get_nowait()
                if Message[0] == "out":
                    with Print.lock:
                        sys.stdout.write(Message[-1] + "\n")
                        sys.stdout.flush()
                elif Message[0] == "in":
                    val: str = input(Message[-1])
                    self.neomega_input_queue.put_nowait((Message[1], val))

    def _handle_input_thread(self) -> None:
        """处理将要写入到 NeOmega 进程中的信息"""
        while True:
            if not self.neomega_input_queue.empty():
                InputMessage: tuple = self.neomega_input_queue.get_nowait()
                self.input_msg.append(InputMessage)

    def launch(self) -> SystemExit | Exception | SystemError:
        """启动 NeOmega 进程

        returns:
            SystemExit: 正常退出
            Exception: 异常退出
            SystemError: 未知的退出状态
        """
        self.status = SysStatus.LAUNCHING
        openat_port = self.start_neomega_proc()
        Print.print_load(
            f'NeOmega 数据存放位置: {os.path.join(os.getcwd(), "tooldelta", "NeOmega数据")}'
        )
        Utils.createThread(
            self._msg_handle_thread,
            usage="处理来自 NeOmega接入点 的信息",
            thread_level=Utils.ToolDeltaThread.SYSTEM,
        )
        Utils.createThread(
            self._msg_show_thread,
            usage="显示来自 NeOmega接入点 的信息",
            thread_level=Utils.ToolDeltaThread.SYSTEM,
        )
        Utils.createThread(
            self._handle_input_thread,
            usage="处理将要写入到 NeOmega 进程中的信息",
            thread_level=Utils.ToolDeltaThread.SYSTEM,
        )
        self.omega.reset_omega_status()
        self.launch_event.wait()
        self.set_omega_conn(openat_port)
        self.update_status(SysStatus.RUNNING)
        self.wait_omega_disconn_thread()
        Print.print_suc("已获取游戏网络接入点最高权限")
        pcks = [
            self.omega.get_packet_id_to_name_mapping(i)
            for i in self.need_listen_packets
        ]
        self.omega.listen_packets(pcks, self.packet_handler_parent)
        self._launcher_listener()
        Print.print_suc("接入点注入已就绪")
        self.exit_event.wait()  # 等待事件的触发
        if self.status == SysStatus.NORMAL_EXIT:
            return SystemExit("正常退出")
        if self.status == SysStatus.CRASHED_EXIT:
            return Exception("接入点进程已崩溃")
        return SystemError("未知的退出状态")


FrameNeOmg = FrameNeOmgAccessPoint
FrameNeOmgRemote = FrameNeOmgAccessPointRemote
