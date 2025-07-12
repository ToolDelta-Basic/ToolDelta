import os
import subprocess
from collections.abc import Callable
import time
from grpc import RpcError
import grpc

from ... import utils
from ...constants import SysStatus, PacketIDS
from ...packets import Packet_CommandOutput
from ...mc_bytes_packet import base_bytes_packet, pool
from ...utils import fmts, urlmethod, sys_args
from .standard_launcher import StandardFrame
from .fateark_libs import core_conn as fateark_core, utils as fateark_utils


class FrameFateArk(StandardFrame):
    launch_type = "FateArk"

    def __init__(self) -> None:
        super().__init__()
        self.bot_name = ""
        self.command_output_cbs: dict[str, Callable] = {}

    def init(self) -> None:
        super().init()
        if "no-download-libs" not in sys_args.sys_args_to_dict().keys():
            fateark_utils.check_update(urlmethod.get_global_github_src_url())

    def set_launch_data(
        self, serverNumber: int, password: str, fbToken: str, auth_server_url: str
    ):
        self.serverNumber = serverNumber
        self.serverPassword = password
        self.fbToken = fbToken
        self.auth_server = auth_server_url

    def launch(self):
        self.update_status(SysStatus.LAUNCHING)
        free_port = urlmethod.get_free_port(19200)
        self.start_fateark_proc(free_port)
        self._proc_message_show_thread()
        self._proc_stderr_show_thread()
        fmts.print_suc(f"将在 {free_port} 端口启动 FateArk 接入点")
        time.sleep(3)
        fateark_core.connect(f"localhost:{free_port}")
        fmts.print_suc("FateArk 接入点进程已启动")
        self._message_show_thread()
        try:
            status, _, err_msg = fateark_core.login(
                self.auth_server,
                self.fbToken,
                str(self.serverNumber),
                self.serverPassword,
            )
        except grpc.RpcError as err:
            self.update_status(SysStatus.CRASHED_EXIT)
            self._safe_exit()
            return SystemError(f"FateArk 与 ToolDelta 断开连接: {err.details()}")
        if status != 0:
            self.update_status(SysStatus.CRASHED_EXIT)
            return SystemError(f"FateArk 登录失败: {err_msg}")
        self.update_status(SysStatus.RUNNING)
        fateark_core.set_listen_packets(set(self.need_listen_packets))
        self._packets_handler_thread()
        self._bytes_packets_handler_thread()
        self._exec_launched_listen_cbs()
        self.wait_crashed()
        self._safe_exit()
        if self.status == SysStatus.NORMAL_EXIT:
            return SystemExit("正常退出")
        if self.status == SysStatus.CRASHED_EXIT:
            return Exception("接入点进程已崩溃")
        return SystemError("未知的退出状态")

    def start_fateark_proc(self, port: int):
        path = fateark_utils.get_bin_path()
        if not os.path.isfile(path):
            fmts.print_err(f"FateArk 接入点不存在: {path}")
            raise SystemExit
        if not path.endswith(".exe"):
            # Maybe is linux and so on
            os.system("chmod +x " + path)
        self.proc = subprocess.Popen(
            [path, "-p", str(port)], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

    @utils.thread_func("FateArk 主输出线程", thread_level=utils.ToolDeltaThread.SYSTEM)
    def _message_show_thread(self):
        try:
            for msg_prefix, msg, err_msg in fateark_core.read_output():
                fmts.print_with_info(f"§b[{msg_prefix}]§r {msg}", "§b FARK ")
                if err_msg:
                    fmts.print_err("FateArk: " + err_msg)
                    self.update_status(SysStatus.CRASHED_EXIT)
                if msg_prefix == "Crash":
                    self.update_status(SysStatus.CRASHED_EXIT)
        except RpcError:
            fmts.print_inf("FateArk 输出通道已断开连接")

    @utils.thread_func(
        "FateArk 报错输出线程", thread_level=utils.ToolDeltaThread.SYSTEM
    )
    def _proc_stderr_show_thread(self):
        assert self.proc.stderr
        while 1:
            msg = self.proc.stderr.readline().decode("utf-8").strip()
            if msg == "":
                break
            fmts.print_with_info(msg, "§c FARK ")
        # fmts.print_inf("FateArk 进程已退出")

    @utils.thread_func(
        "FateArk 进程输出线程", thread_level=utils.ToolDeltaThread.SYSTEM
    )
    def _proc_message_show_thread(self):
        assert self.proc.stdout
        while 1:
            msg = self.proc.stdout.readline().decode("utf-8").strip()
            if msg == "":
                break
            fmts.print_with_info(msg, "§6 FARK ")
        fmts.print_inf("FateArk 进程已退出")

    @utils.thread_func(
        "FateArk 数据包处理线程", thread_level=utils.ToolDeltaThread.SYSTEM
    )
    def _packets_handler_thread(self):
        try:
            for id, packet in fateark_core.read_packet():
                self._packets_handler(id, packet)
        except RpcError:
            fmts.print_inf("FateArk 数据包处理通道已断开连接")
            self.update_status(SysStatus.CRASHED_EXIT)

    @utils.thread_func(
        "FateArk 字节流数据包处理线程", thread_level=utils.ToolDeltaThread.SYSTEM
    )
    def _bytes_packets_handler_thread(self):
        try:
            for pkID, packet_bytes in fateark_core.read_bytes_packet():
                packet = pool.bytes_packet_by_id(pkID)
                packet.decode(packet_bytes)
                self._packets_handler(pkID, packet)
        except RpcError:
            fmts.print_inf("FateArk 数据包处理通道已断开连接")
            self.update_status(SysStatus.CRASHED_EXIT)

    @utils.thread_func("单数据包处理线程")
    def _packets_handler(self, pkID: int, pk: dict | base_bytes_packet.BaseBytesPacket):
        if isinstance(pk, base_bytes_packet.BaseBytesPacket):
            self.bytes_packet_handler(pkID, pk)
        else:
            if pkID == PacketIDS.CommandOutput:
                self._command_output_handler(pk)
            self.dict_packet_handler(pkID, pk)

    def _command_output_handler(self, pk: dict):
        pkUUID = utils.basic.validate_uuid(pk["CommandOrigin"]["UUID"])
        if pkUUID in self.command_output_cbs:
            self.command_output_cbs[pkUUID](pk)
        # else:
        #     fmts.print_war(f"命令没有对应回调: {pkUUID}")

    def _safe_exit(self):
        self.proc.kill()

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
            ud = fateark_core.sendcmd_and_get_uuid(cmd)
            getter, setter = utils.create_result_cb(dict)
            self.command_output_cbs[ud] = setter
            res = getter(timeout)
            if res is None:
                raise TimeoutError("指令超时", ud)
            return Packet_CommandOutput(res)
        return None

    def sendwscmd(
        self, cmd: str, waitForResp: bool = False, timeout: float = 30
    ) -> Packet_CommandOutput | None:
        self.check_avaliable()
        if waitForResp:
            ud = fateark_core.sendwscmd_and_get_uuid(cmd)
            getter, setter = utils.create_result_cb(dict)
            self.command_output_cbs[ud] = setter
            res = getter(timeout)
            if res is None:
                raise TimeoutError("指令超时", ud)
            return Packet_CommandOutput(res)

    def sendwocmd(self, cmd: str):
        """以控制台身份发送命令

        Args:
            cmd (str): 命令

        """
        self.check_avaliable()
        fateark_core.sendwocmd(cmd)

    def sendPacket(self, pckID: int, pck: dict | base_bytes_packet.BaseBytesPacket) -> None:
        """发送数据包

        Args:
            pckID (int): 数据包 ID
            pck (str | BaseBytesPacket): 数据包内容

        """
        if type(pck) is not dict:
            raise Exception("sendPacket: Bytes packet is not supported")
        fateark_core.sendPacket(pckID, pck)

    def get_players_info(self):
        uuids = fateark_core.get_online_player_uuids()
        return {
            fateark_core.get_unready_player(uuid).name: fateark_core.get_unready_player(
                uuid
            )
            for uuid in uuids
        }

    def get_bot_name(self) -> str:
        """获取机器人名字

        Returns:
            str: 机器人名字
        """
        self.check_avaliable()
        if not self.bot_name:
            self.bot_name = fateark_core.get_bot_name()
        return self.bot_name
