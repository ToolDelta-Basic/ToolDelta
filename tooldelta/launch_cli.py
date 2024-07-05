"""客户端启动器框架"""

import os
import platform
import shlex
import subprocess
import threading
import time
from typing import Callable, Optional

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
        self.packet_handler: Optional[Callable] = lambda pckType, pck: None
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
            tooldelta.safe_jump(out_task=True)
            self.exit_event.set()  # 设置事件，触发等待结束
        if new_status == SysStatus.CRASHED_EXIT:
            tooldelta.safe_jump(out_task=False)
            self.exit_event.set()

    def sendcmd(
        self, cmd: str, waitForResp: bool = False, timeout: int | float = 30
    ) -> Optional[Packet_CommandOutput]:
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
        self, cmd: str, waitForResp: bool = False, timeout: int | float = 30
    ) -> Optional[Packet_CommandOutput]:
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


class FrameNeOmg(StandardFrame):
    """使用 NeOmega 框架连接到游戏"""

    launch_type = "NeOmega"

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
        self.serverNumber: Optional[int] = None
        self.serverPassword: Optional[str] = None
        self.fbToken: Optional[str] = None
        self.auth_server: Optional[str] = None

    def init(self):
        res = neo_fd.download_libs()
        if not res:
            raise SystemExit("ToolDelta 因下载库异常而退出")
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
        self.omega = neo_conn.ThreadOmega(
            connect_type=neo_conn.ConnectType.Remote,
            address="tcp://localhost:24013",
            accountOption=self.neomega_account_opt,
        )

    def set_omega(self, openat_port: int) -> None:
        """设置 Omega 连接

        Args:
            openat_port (int): 端口号

        Raises:
            SystemExit: 系统退出
        """
        retries = 0
        self.omega.address = f"tcp://localhost:{openat_port}"
        while retries <= 10:
            try:
                self.omega.connect()
                retries = 0
                break
            except Exception as err:
                Print.print_war(f"OMEGA 连接失败，重连：第 {retries} 次：{err}")
                time.sleep(5)
                retries += 1
                if retries > 5:
                    Print.print_err("最大重试次数已超过")
                    raise SystemExit from err

    def start_neomega_proc(self) -> int:
        """启动 NeOmega 进程

        Returns:
            int: 端口号
        """
        free_port = get_free_port(24016)
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
            isinstance(self.serverNumber, type(None))
            or isinstance(self.serverPassword, type(None))
            or isinstance(self.fbToken, type(None))
            or isinstance(self.auth_server, type(None))
        ):
            raise ValueError("未设置服务器号、密码、Token 或验证服务器地址")
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
            text=True,
        )
        return free_port

    def _msg_show_thread(self) -> None:
        """显示来自 NeOmega 的信息"""
        if self.neomg_proc is None or self.neomg_proc.stdout is None:
            raise ValueError("NEOMG 进程未启动")
        while True:
            msg_orig = self.neomg_proc.stdout.readline().strip("\n")
            if msg_orig in ("", "SIGNAL: exit"):
                Print.print_with_info("ToolDelta: NEOMG 进程已结束", "§b NOMG ")
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
        openat_port = self.start_neomega_proc()
        Utils.createThread(self._msg_show_thread, usage="显示来自 NeOmega 的信息")
        self.launch_event.wait()
        self.set_omega(openat_port)
        self.update_status(SysStatus.RUNNING)
        self.wait_omega_disconn_thread()
        Print.print_suc("已开启接入点进程")
        pcks = [
            self.omega.get_packet_id_to_name_mapping(i)
            for i in self.need_listen_packets
        ]
        self.omega.listen_packets(pcks, self.packet_handler_parent)
        self._launcher_listener()
        Print.print_suc("接入点已就绪！")
        self.exit_event.wait()  # 等待事件的触发
        if self.status == SysStatus.NORMAL_EXIT:
            return SystemExit("正常退出。")
        if self.status == SysStatus.CRASHED_EXIT:
            return Exception("NeOmega 已崩溃")
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
    ) -> Optional[Packet_CommandOutput]:
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
    ) -> Optional[Packet_CommandOutput]:
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
                raise TimeoutError("指令超时")
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

    def sendPacket(self, pckID: int, pck: str) -> None:
        """发送数据包

        Args:
            pckID (int): 数据包 ID
            pck (str): 数据包内容

        Raises:
            NotImplementedError: 未实现此方法
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
        player_obj = self.omega.get_player_by_name(player)
        if isinstance(player_obj, type(None)) or isinstance(
            player_obj.can_operator_commands, type(None)
        ):
            raise ValueError("未能获取玩家对象")
        return bool(player_obj.can_operator_commands)

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

    @Utils.thread_func("检测 Omega 断开连接线程")
    def wait_omega_disconn_thread(self):
        self.omega.wait_disconnect()
        if self.status == SysStatus.RUNNING:
            self.update_status(SysStatus.CRASHED_EXIT)

    sendPacketJson = sendPacket


class FrameNeOmgRemote(FrameNeOmg):
    """远程启动器框架 (使用 NeOmega 框架的 Remote 连接)

    Args:
        FrameNeOmg (FrameNeOmg): FrameNeOmg 框架
    """

    launch_type = "NeOmega Remote"

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
        Print.print_inf(f"将从端口 {openat_port} 连接至接入点 (等待接入中).")
        self.set_omega(openat_port)
        self.update_status(SysStatus.RUNNING)
        self.wait_omega_disconn_thread()
        Print.print_suc("已连接上接入点进程。")
        pcks = [
            self.omega.get_packet_id_to_name_mapping(i)
            for i in self.need_listen_packets
        ]
        self.omega.listen_packets(pcks, self.packet_handler_parent)
        self._launcher_listener()
        Print.print_suc("接入点已就绪")
        self.exit_event.wait()
        if self.status == SysStatus.NORMAL_EXIT:
            return SystemExit("正常退出。")
        if self.status == SysStatus.CRASHED_EXIT:
            return Exception("接入点已崩溃")
        return SystemError("未知的退出状态")


class FrameBEConnect(StandardFrame):
    "WIP: Minecraft Bedrock '/connect' 指令所连接的服务端"

    def __init__(self) -> None:
        super().__init__()
        self.cmd_resp: dict = {}

    def init(self):
        self.cmd_resp = {}

    def prepare_apis(self):
        raise NotImplementedError()

    def handler(self, data):
        message_purpose = data["header"]["messagePurpose"]
        if message_purpose == "commandResponse":
            request_id = data["header"]["requestId"]
            if request_id in self.cmd_resp:
                self.cmd_resp[request_id] = Packet_CommandOutput(
                    {
                        "CommandOrigin": [],
                        "OutputType": 1,
                    }
                )
