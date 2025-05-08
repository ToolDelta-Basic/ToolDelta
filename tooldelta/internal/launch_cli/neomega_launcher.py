import os
import platform
import shlex
import subprocess
import threading
import time

from ... import utils
from ...constants import SysStatus
from ...utils import fmts, sys_args, urlmethod
from .neo_libs import file_download as neo_fd, neo_conn
from .neomega_access_point import FrameNeOmgAccessPoint


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
            os.getcwd(), "tooldelta", "bin", access_point_file
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
        while not self.launch_event.wait(timeout = 1):
            if self.exit_event.is_set():
                self.update_status(SysStatus.CRASHED_EXIT)
                return SystemError("NeOmage 启动出现问题")
        self.set_omega_conn(f"tcp://127.0.0.1:{openat_port}")
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
        self.wait_crashed()
        if self.status == SysStatus.NORMAL_EXIT:
            return SystemExit("正常退出")
        if self.status == SysStatus.CRASHED_EXIT:
            return Exception("接入点进程已崩溃")
        return SystemError("未知的退出状态")
