import grpc

from ...constants import tooldelta_cfg
from ...utils.cfg import get_cfg
from ...constants import SysStatus
from ...utils import fmts, sys_args
from .fateark_libs import core_conn as fateark_core
from .fateark_access_point import FrameFateArk


class FrameFateArkIndirect(FrameFateArk):
    launch_type = "FateArk"
    proc = None

    def __init__(self) -> None:
        super().__init__()


    def launch(self):
        cfgs = get_cfg("ToolDelta基本配置.json", tooldelta_cfg.LAUNCH_CFG_STD)
        openat_addr = (
            sys_args.sys_args_to_dict().get("access-point-port")
            or cfgs.get("FateArk远程接入点模式", {}).get(
                "远程连接端口", "tcp://127.0.0.1:24020"
            )
        ).removeprefix("tcp://")
        self.update_status(SysStatus.LAUNCHING)
        fmts.print_suc(f"将在 {openat_addr} 端口启动 FateArk 接入点")
        fateark_core.connect(openat_addr)
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
            return SystemError(f"FateArk 与 ToolDelta 断开连接: {err.details()}")
        if status != 0:
            self.update_status(SysStatus.CRASHED_EXIT)
            return SystemError(f"FateArk 登录失败: {err_msg}")
        fmts.print_suc("FateArk 已连接")
        self.update_status(SysStatus.RUNNING)
        fateark_core.set_listen_packets(set(self.need_listen_packets))
        self._packets_handler_thread()
        self._bytes_packets_handler_thread()
        self._exec_launched_listen_cbs()
        self.wait_crashed()
        if self.status == SysStatus.NORMAL_EXIT:
            return SystemExit("正常退出")
        if self.status == SysStatus.CRASHED_EXIT:
            return Exception("接入点进程已崩溃")
        return SystemError("未知的退出状态")
