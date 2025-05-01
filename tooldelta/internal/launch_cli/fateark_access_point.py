import os
import subprocess
from collections.abc import Callable
from grpc import RpcError

from ... import utils
from ...constants import SysStatus, PacketIDS
from ...packets import Packet_CommandOutput
from ...mc_bytes_packet.base_bytes_packet import BaseBytesPacket
from ...utils import fmts, urlmethod
from .standard_launcher import StandardFrame
from .fateark_libs import core_conn as fateark_core, utils as fateark_utils


class FrameFateArk(StandardFrame):
    launch_type = "FateArk"
    proc: subprocess.Popen

    def __init__(self) -> None:
        super().__init__()
        self.bot_name = ""
        self.command_output_cbs: dict[str, Callable] = {}

    def init(self) -> None:
        super().init()

    def set_launch_data(
        self, serverNumber: int, password: str, fbToken: str, auth_server_url: str
    ):
        self.serverNumber = serverNumber
        self.serverPassword = password
        self.fbToken = fbToken
        self.auth_server = auth_server_url

    def launch(self):
        self.update_status(SysStatus.LAUNCHING)
        free_port = urlmethod.get_free_port(19000)
        self.start_fateark_proc(free_port)
        self._proc_message_show_thread()
        fmts.print_suc(f"将在 {free_port} 端口启动 FateArk 接入点")
        fateark_core.connect(f"localhost:{free_port}")
        fmts.print_suc("FateArk 接入点进程已启动")
        self._message_show_thread()
        status, _, err_msg = fateark_core.login(
            self.auth_server, self.fbToken, str(self.serverNumber), self.serverPassword
        )
        if status != 0:
            self.update_status(SysStatus.CRASHED_EXIT)
            return SystemError(f"FateArk 登录失败: {err_msg}")
        self.update_status(SysStatus.RUNNING)
        fateark_core.set_listen_packets(set(self.need_listen_packets))
        self._packets_handler_thread()
        self._exec_launched_listen_cbs()
        self.wait_crashed()
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
        except RpcError as err:
            fmts.print_inf(f"FateArk 数据包处理通道已断开连接: {err}")
            self.update_status(SysStatus.CRASHED_EXIT)

    def _packets_handler(self, pkID: int, pk: dict):
        if pkID == PacketIDS.CommandOutput:
            self._command_output_handler(pk)
        self.dict_packet_handler(pkID, pk)

    def _command_output_handler(self, pk: dict):
        pkUUID = pk["CommandOrigin"]["UUID"]
        if pkUUID in self.command_output_cbs:
            self.command_output_cbs[pkUUID](pk)
        # else:
        #     fmts.print_war(f"命令没有对应回调: {pkUUID}")

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
                raise TimeoutError("指令超时")
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
                raise TimeoutError("指令超时")
            return Packet_CommandOutput(res)

    def sendwocmd(self, cmd: str):
        """以控制台身份发送命令

        Args:
            cmd (str): 命令

        """
        self.check_avaliable()
        fateark_core.sendwocmd(cmd)

    def sendPacket(self, pckID: int, pck: dict | BaseBytesPacket) -> None:
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
