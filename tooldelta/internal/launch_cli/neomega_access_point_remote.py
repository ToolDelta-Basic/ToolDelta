from ...constants import SysStatus, tooldelta_cfg
from ...utils import cfg, fmts, sys_args
from .neomega_access_point import FrameNeOmgAccessPoint


class FrameNeOmgAccessPointRemote(FrameNeOmgAccessPoint):
    """远程启动器框架 (使用 NeOmega接入点 框架的 Remote 连接)"""

    launch_type = "NeOmegaAccessPoint Remote"

    def launch(self) -> SystemExit | Exception | SystemError:
        """启动远程启动器框架

        Raises:
            AssertionError: 端口号错误

        Returns:
            SystemExit | Exception | SystemError: 退出状态
        """
        cfgs = cfg.get_cfg("ToolDelta基本配置.json", tooldelta_cfg.LAUNCH_CFG_STD)
        openat_addr = sys_args.sys_args_to_dict().get("access-point-port") or cfgs.get(
            "NeOmega远程接入点模式", {}
        ).get("远程连接地址", "tcp://127.0.0.1:24020")
        fmts.print_inf(f"将从[{openat_addr}]连接至游戏网络接入点, 等待接入中...")
        if (err_str := self.set_omega_conn(openat_addr)) == "":
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
        self.wait_crashed()
        if self.status == SysStatus.NORMAL_EXIT:
            return SystemExit("正常退出。")
        if self.status == SysStatus.CRASHED_EXIT:
            return Exception(f"接入点已崩溃: {self.exit_reason}")
        return SystemError("未知的退出状态")
