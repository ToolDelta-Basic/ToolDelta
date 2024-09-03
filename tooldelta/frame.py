"""
ToolDelta 基本框架

整个系统由三个部分组成
    Frame: 负责整个 ToolDelta 的基本框架运行
    GameCtrl: 负责对接游戏
        - Launchers: 负责将不同启动器的游戏接口统一成固定的接口，供插件在多平台游戏接口运行 (FastBuilder External, NeOmega, (BEWS, etc.))
    PluginGroup: 负责对插件进行统一管理
"""

import asyncio
import contextlib
import getpass
import os
import signal
import sys
import traceback
from collections.abc import Callable
from typing import TYPE_CHECKING

import requests
import json

from tooldelta import auths, constants, plugin_market, game_utils, utils

from .cfg import Config
from .color_print import Print
from .constants import PacketIDS
from .game_texts import GameTextsHandle, GameTextsLoader
from .game_utils import getPosXYZ
from .get_tool_delta_version import get_tool_delta_version
from .launch_cli import (
    FrameNeOmgAccessPoint,
    FrameNeOmgAccessPointRemote,
    FrameNeOmegaLauncher,
    SysStatus,
)
from .logger import publicLogger
from .packets import Packet_CommandOutput
from .plugin_load.injected_plugin import safe_jump
from .sys_args import sys_args_to_dict
from .utils import Utils, fbtokenFix, if_token

if TYPE_CHECKING:
    from .plugin_load.PluginGroup import PluginGroup

###### CONSTANT DEFINE

sys_args_dict = sys_args_to_dict(sys.argv)
VERSION = get_tool_delta_version()
FB_LIKE_LAUNCHERS = (
    FrameNeOmegaLauncher | FrameNeOmgAccessPoint | FrameNeOmgAccessPointRemote
)
"类FastBuilder启动器框架"
LAUNCHERS = FB_LIKE_LAUNCHERS
"所有启动器框架类型"
LAUNCHERS_SHOWN: list[tuple[str, type[LAUNCHERS]]] = [
    ("NeOmega 框架 (NeOmega 模式，租赁服适应性强，推荐)", FrameNeOmgAccessPoint),
    (
        "NeOmega 框架 (NeOmega 连接模式，需要先启动对应的 neOmega 接入点)",
        FrameNeOmgAccessPointRemote,
    ),
    (
        "NeOmega 框架 (NeOmega 并行模式，同时运行NeOmega和ToolDelta)",
        FrameNeOmegaLauncher,
    ),
]

###### FRAME DEFINE


class ToolDelta:
    """ToolDelta 主框架"""

    class FrameBasic:
        """系统基本信息"""

        system_version = VERSION
        data_path = "插件数据文件/"

    class SystemVersionException(SystemError):
        """系统版本异常"""

        msg: str

    def __init__(self) -> None:
        """初始化"""
        self.createThread = Utils.createThread
        self.sys_data = self.FrameBasic()
        self.launchMode: int = 0
        self.consoleMenu = []
        self.is_docker: bool = os.path.exists("/.dockerenv")
        self.on_plugin_err = staticmethod(
            lambda name, _, err: Print.print_err(f"插件 <{name}> 出现问题：\n{err}")
        )
        self.launcher: LAUNCHERS
        self.is_mir: bool
        self.plugin_market_url: str
        self.link_game_ctrl: "GameCtrl"
        self.link_plugin_group: "PluginGroup"

    def loadConfiguration(self) -> None:
        """加载配置文件"""
        Config.default_cfg("ToolDelta基本配置.json", constants.LAUNCH_CFG)
        try:
            # 读取配置文件
            cfgs = Config.get_cfg("ToolDelta基本配置.json", constants.LAUNCH_CFG_STD)
            self.launchMode = cfgs["启动器启动模式(请不要手动更改此项, 改为0可重置)"]
            self.is_mir = cfgs["是否使用github镜像"]
            self.plugin_market_url = cfgs["插件市场源"]
            publicLogger.switch_logger(cfgs["是否记录日志"])
            if self.launchMode != 0 and self.launchMode not in range(
                1, len(LAUNCHERS_SHOWN) + 1
            ):
                raise Config.ConfigError(
                    "你不该随意修改启动器模式，现在赶紧把它改回 0 吧"
                )
        except Config.ConfigError as err:
            # 配置文件有误
            r = self.upgrade_cfg()
            if r:
                Print.print_war("配置文件未升级，已自动升级，请重启 ToolDelta")
            else:
                Print.print_err(f"ToolDelta 基本配置有误，需要更正：{err}")
            raise SystemExit from err
        # 每个启动器框架的单独启动配置之前
        if self.launchMode == 0:
            Print.print_inf("请选择启动器启动模式 (之后可在 ToolDelta 启动配置更改):")
            for i, (launcher_name, _) in enumerate(LAUNCHERS_SHOWN):
                Print.print_inf(f" {i + 1} - {launcher_name}")
            while 1:
                try:
                    ch = int(input(Print.fmt_info("请选择：", "§f 输入 ")))
                    if ch not in range(1, len(LAUNCHERS_SHOWN) + 1):
                        raise ValueError
                    cfgs["启动器启动模式(请不要手动更改此项, 改为0可重置)"] = ch
                    break
                except ValueError:
                    Print.print_err("输入不合法，或者是不在范围内，请重新输入")
            Config.default_cfg("ToolDelta基本配置.json", cfgs, True)
        self.launcher = LAUNCHERS_SHOWN[
            cfgs["启动器启动模式(请不要手动更改此项, 改为0可重置)"] - 1
        ][1]()
        # 每个启动器框架的单独启动配置
        if type(self.launcher) is FrameNeOmgAccessPoint:
            launch_data = cfgs.get(
                "NeOmega接入点启动模式", constants.LAUNCHER_NEOMEGA_DEFAULT
            )
            try:
                Config.check_auto(constants.LAUNCHER_NEOMEGA_STD, launch_data)
            except Config.ConfigError as err:
                r = self.upgrade_cfg()
                if r:
                    Print.print_war("配置文件未升级，已自动升级，请重启 ToolDelta")
                else:
                    Print.print_err(
                        f"ToolDelta 基本配置-NeOmega 启动配置有误，需要更正：{err}"
                    )
                raise SystemExit from err
            serverNumber = launch_data["服务器号"]
            serverPasswd: str = launch_data["密码"]
            auth_server = launch_data.get("验证服务器地址(更换时记得更改fbtoken)", "")
            if serverNumber == 0:
                while 1:
                    try:
                        serverNumber = int(
                            input(Print.fmt_info("请输入租赁服号：", "§b 输入 "))
                        )
                        serverPasswd = (
                            getpass.getpass(
                                Print.fmt_info(
                                    "请输入租赁服密码 (不会回显，没有请直接回车): ",
                                    "§b 输入 ",
                                )
                            )
                            or ""
                        )
                        launch_data["服务器号"] = int(serverNumber)
                        launch_data["密码"] = serverPasswd
                        cfgs["NeOmega接入点启动模式"] = launch_data
                        Config.default_cfg("ToolDelta基本配置.json", cfgs, True)
                        Print.print_suc("登录配置设置成功")
                        break
                    except Exception:
                        Print.print_err("输入有误，租赁服号和密码应当是纯数字")
            auth_servers = constants.AUTH_SERVERS
            if auth_server == "":
                Print.print_inf("选择 ToolDelta 机器人账号 使用的验证服务器：")
                for i, (auth_server_name, _) in enumerate(auth_servers):
                    Print.print_inf(f" {i + 1} - {auth_server_name}")
                Print.print_inf(
                    "§cNOTE: 使用的机器人账号是在哪里获取的就选择哪一个验证服务器，不能混用"
                )
                while 1:
                    try:
                        ch = int(input(Print.fmt_info("请选择：", "§f 输入 ")))
                        if ch not in range(1, len(auth_servers) + 1):
                            raise ValueError
                        auth_server = auth_servers[ch - 1][1]
                        cfgs["NeOmega接入点启动模式"][
                            "验证服务器地址(更换时记得更改fbtoken)"
                        ] = auth_server
                        break
                    except ValueError:
                        Print.print_err("输入不合法，或者是不在范围内，请重新输入")
                Config.default_cfg("ToolDelta基本配置.json", cfgs, True)
            # 读取 token
            if not (fbtoken := sys_args_to_dict().get("user-token")):
                if not os.path.isfile("fbtoken"):
                    Print.print_inf(
                        "请选择登录方法:\n 1 - 使用账号密码 (登录成功后将自动获取 Token 到工作目录)\n 2 - 使用 Token(如果 Token 文件不存在则需要输入或将文件放入工作目录)\r"
                    )
                    Login_method: str = input(
                        Print.fmt_info("请输入你的选择：", "§6 输入 ")
                    )
                    while True:
                        if Login_method.isdigit() is False:
                            Login_method = input(
                                Print.fmt_info(
                                    "输入有误，请输入正确的序号：", "§6 警告 "
                                )
                            )
                        elif int(Login_method) > 2 or int(Login_method) < 1:
                            Login_method = input(
                                Print.fmt_info(
                                    "输入有误，请输入正确的序号：", "§6 警告 "
                                )
                            )
                        else:
                            break
                    if Login_method == "1":
                        try:
                            match cfgs["NeOmega接入点启动模式"][
                                "验证服务器地址(更换时记得更改fbtoken)"
                            ]:
                                case "https://liliya233.uk":
                                    token = auths.sign_login(constants.GUGU_APIS)
                                case "https://user.fastbuilder.pro":
                                    token = auths.sign_login(constants.FB_APIS)
                                case _:
                                    Print.print_err("暂无法登录该验证服务器")
                                    raise SystemExit
                            with open("fbtoken", "w", encoding="utf-8") as f:
                                f.write(token)
                        except requests.exceptions.RequestException as e:
                            Print.print_err(
                                f"登录失败，原因：{e}\n正在切换至 Token 登录"
                            )
                if_token()
                fbtokenFix()
                with open("fbtoken", encoding="utf-8") as f:
                    fbtoken = f.read()
            self.launcher.set_launch_data(
                serverNumber, serverPasswd, fbtoken, auth_server
            )
        elif type(self.launcher) is FrameNeOmegaLauncher:
            launch_data = cfgs.get(
                "NeOmega并行ToolDelta启动模式",
                constants.LAUNCHER_NEOMGPARALLELTTOOLDELTA_DEFAULT,
            )
            try:
                Config.check_auto(
                    constants.LAUNCHER_NEOMGPARALLELTTOOLDELTA_STD, launch_data
                )
            except Config.ConfigError as err:
                r = self.upgrade_cfg()
                if r:
                    Print.print_war("配置文件未升级，已自动升级，请重启 ToolDelta")
                else:
                    Print.print_err(
                        f"ToolDelta 基本配置-NeOmega 启动配置有误，需要更正：{err}"
                    )
                raise SystemExit from err
            serverNumber = launch_data["服务器号"]
            serverPasswd: str = launch_data["密码"]
            auth_server = launch_data.get("验证服务器地址(更换时记得更改fbtoken)", "")
            if serverNumber == 0:
                while 1:
                    try:
                        serverNumber = int(
                            input(Print.fmt_info("请输入租赁服号：", "§b 输入 "))
                        )
                        serverPasswd = (
                            getpass.getpass(
                                Print.fmt_info(
                                    "请输入租赁服密码 (不会回显，没有请直接回车): ",
                                    "§b 输入 ",
                                )
                            )
                            or ""
                        )
                        launch_data["服务器号"] = int(serverNumber)
                        launch_data["密码"] = serverPasswd
                        cfgs["NeOmega并行ToolDelta启动模式"] = launch_data
                        Config.default_cfg("ToolDelta基本配置.json", cfgs, True)
                        Print.print_suc("登录配置设置成功")
                        break
                    except Exception:
                        Print.print_err("输入有误，租赁服号和密码应当是纯数字")
            auth_servers = constants.AUTH_SERVERS
            if auth_server == "":
                Print.print_inf("选择 ToolDelta 机器人账号 使用的验证服务器：")
                for i, (auth_server_name, _) in enumerate(auth_servers):
                    Print.print_inf(f" {i + 1} - {auth_server_name}")
                Print.print_inf(
                    "§cNOTE: 使用的机器人账号是在哪里获取的就选择哪一个验证服务器，不能混用"
                )
                while 1:
                    try:
                        ch = int(input(Print.fmt_info("请选择：", "§f 输入 ")))
                        if ch not in range(1, len(auth_servers) + 1):
                            raise ValueError
                        auth_server = auth_servers[ch - 1][1]
                        cfgs["NeOmega并行ToolDelta启动模式"][
                            "验证服务器地址(更换时记得更改fbtoken)"
                        ] = auth_server
                        break
                    except ValueError:
                        Print.print_err("输入不合法，或者是不在范围内，请重新输入")
                Config.default_cfg("ToolDelta基本配置.json", cfgs, True)
            # 读取 token
            if not (fbtoken := sys_args_to_dict().get("user-token")):
                if not os.path.isfile("fbtoken"):
                    Print.print_inf(
                        "请选择登录方法:\n 1 - 使用账号密码 (登录成功后将自动获取 Token 到工作目录)\n 2 - 使用 Token(如果 Token 文件不存在则需要输入或将文件放入工作目录)\r"
                    )
                    Login_method: str = input(
                        Print.fmt_info("请输入你的选择：", "§6 输入 ")
                    )
                    while True:
                        if Login_method.isdigit() is False:
                            Login_method = input(
                                Print.fmt_info(
                                    "输入有误，请输入正确的序号：", "§6 警告 "
                                )
                            )
                        elif int(Login_method) > 2 or int(Login_method) < 1:
                            Login_method = input(
                                Print.fmt_info(
                                    "输入有误，请输入正确的序号：", "§6 警告 "
                                )
                            )
                        else:
                            break
                    if Login_method == "1":
                        try:
                            match cfgs["NeOmega并行ToolDelta启动模式"][
                                "验证服务器地址(更换时记得更改fbtoken)"
                            ]:
                                case "https://liliya233.uk":
                                    token = auths.sign_login(constants.GUGU_APIS)
                                case "https://user.fastbuilder.pro":
                                    token = auths.sign_login(constants.FB_APIS)
                                case _:
                                    Print.print_err("暂无法登录该验证服务器")
                                    raise SystemExit
                            with open("fbtoken", "w", encoding="utf-8") as f:
                                f.write(token)
                        except requests.exceptions.RequestException as e:
                            Print.print_err(
                                f"登录失败，原因：{e}\n正在切换至 Token 登录"
                            )
                if_token()
                fbtokenFix()
                with open("fbtoken", encoding="utf-8") as f:
                    fbtoken = f.read()
            self.launcher.set_launch_data(
                serverNumber, serverPasswd, fbtoken, auth_server
            )
        elif type(self.launcher) is FrameNeOmgAccessPointRemote:
            ...
        else:
            raise ValueError("LAUNCHER Error")
        Print.print_suc("配置文件读取完成")

    @staticmethod
    def change_config():
        """修改配置文件"""
        try:
            old_cfg = Config.get_cfg("ToolDelta基本配置.json", constants.LAUNCH_CFG_STD)
        except FileNotFoundError:
            Print.clean_print("§c未初始化配置文件, 无法进行修改")
            return
        except Config.ConfigError as err:
            Print.print_err(f"配置文件损坏：{err}")
            return
        if (
            old_cfg["启动器启动模式(请不要手动更改此项, 改为0可重置)"] - 1
        ) not in range(0, 2):
            Print.print_err(
                f"配置文件损坏：启动模式错误：{old_cfg['启动器启动模式(请不要手动更改此项, 改为0可重置)'] - 1}"
            )
            return
        while 1:
            md = (
                "NeOmega 框架 (NeOmega 模式，租赁服适应性强，推荐)",
                "NeOmega 框架 (NeOmega 连接模式，需要先启动对应的 neOmega 接入点)",
            )
            Print.clean_print("§b现有配置项如下:")
            Print.clean_print(
                f" 1. 启动器启动模式：{md[old_cfg['启动器启动模式(请不要手动更改此项, 改为0可重置)'] - 1]}"
            )
            Print.clean_print(f" 2. 是否记录日志：{old_cfg['是否记录日志']}")
            Print.clean_print("    §a直接回车: 保存并退出")
            resp = input(Print.clean_fmt("§6输入序号可修改配置项(0~4): ")).strip()
            if resp == "":
                Config.default_cfg("ToolDelta基本配置.json", old_cfg, True)
                Print.clean_print("§a配置已保存!")
                return
            match resp:
                case "1":
                    Print.print_inf(
                        "选择启动器启动模式 (之后可在 ToolDelta 启动配置更改):"
                    )
                    for i, (launcher_name, _) in enumerate(LAUNCHERS_SHOWN):
                        Print.print_inf(f" {i + 1} - {launcher_name}")
                    while 1:
                        try:
                            ch = int(input(Print.clean_fmt("请选择：")))
                            if ch not in range(1, len(LAUNCHERS_SHOWN) + 1):
                                raise ValueError
                            old_cfg[
                                "启动器启动模式(请不要手动更改此项, 改为0可重置)"
                            ] = ch
                            break
                        except ValueError:
                            Print.print_err("输入不合法，或者是不在范围内，请重新输入")
                            continue
                    input(
                        Print.clean_fmt(
                            f"§a已选择启动器启动模式：§f{md[old_cfg['启动器启动模式(请不要手动更改此项, 改为0可重置)'] - 1]}, 回车键继续"
                        )
                    )
                case "2":
                    old_cfg["是否记录日志"] = [True, False][old_cfg["是否记录日志"]]
                    input(
                        Print.clean_fmt(
                            f"日志记录模式已改为：{['§c关闭', '§a开启'][old_cfg['是否记录日志']]}, 回车键继续"
                        )
                    )

    @staticmethod
    def upgrade_cfg() -> bool:
        """升级配置文件

        Returns:
            bool: 是否升级了配置文件
        """
        old_cfg: dict = Config.get_cfg("ToolDelta基本配置.json", {})
        old_cfg_keys = old_cfg.keys()
        need_upgrade_cfg = False
        if "NeOmega接入点启动模式" in old_cfg:
            if isinstance(old_cfg["NeOmega接入点启动模式"]["密码"], int):
                old_cfg["NeOmega接入点启动模式"]["密码"] = str(
                    old_cfg["NeOmega接入点启动模式"]["密码"]
                )
                if old_cfg["NeOmega接入点启动模式"]["密码"] == "0":
                    old_cfg["NeOmega接入点启动模式"]["密码"] = ""
                need_upgrade_cfg = True
        for k, v in constants.LAUNCH_CFG.items():
            if k not in old_cfg_keys:
                old_cfg[k] = v
                need_upgrade_cfg = True
        if need_upgrade_cfg:
            Config.default_cfg("ToolDelta基本配置.json", old_cfg, True)
        return need_upgrade_cfg

    @staticmethod
    def welcome() -> None:
        """欢迎提示"""
        Print.print_with_info("§dToolDelta Panel Embed By SuperScript", Print.INFO_LOAD)
        Print.print_with_info(
            "§dToolDelta Wiki: https://td-wiki.dqyt.online/", Print.INFO_LOAD
        )
        Print.print_with_info(
            "§dToolDelta 项目地址：https://github.com/ToolDelta-Basic", Print.INFO_LOAD
        )
        Print.print_with_info(
            f"§dToolDelta v {'.'.join([str(i) for i in VERSION])}", Print.INFO_LOAD
        )
        Print.print_with_info("§dToolDelta Panel 已启动", Print.INFO_LOAD)

    @staticmethod
    def basic_operation():
        """初始化文件夹"""
        os.makedirs(f"插件文件/{constants.TOOLDELTA_CLASSIC_PLUGIN}", exist_ok=True)
        os.makedirs(f"插件文件/{constants.TOOLDELTA_INJECTED_PLUGIN}", exist_ok=True)
        os.makedirs("插件配置文件", exist_ok=True)
        os.makedirs("数据库文件", exist_ok=True)
        os.makedirs("tooldelta/neo_libs", exist_ok=True)
        os.makedirs("插件数据文件/game_texts", exist_ok=True)

    def add_console_cmd_trigger(
        self,
        triggers: list[str],
        arg_hint: str | None,
        usage: str,
        func: Callable[[list[str]], None | int],
    ) -> None:
        """注册 ToolDelta 控制台的菜单项

        Args:
            triggers (list[str]): 触发词列表
            arg_hint (str | None): 菜单命令参数提示句
            usage (str): 命令说明
            func (Callable[[list[str]], None]): 菜单回调方法
        """
        self.consoleMenu.append([usage, arg_hint, func, triggers])

    def init_console_menu(self):
        "初始化控制台菜单"

        @Utils.thread_func("控制台执行指令并获取回调", Utils.ToolDeltaThread.SYSTEM)
        def _execute_mc_command_and_get_callback(cmds: list[str]) -> None:
            """执行 Minecraft 指令并获取回调结果。

            Args:
                cmd (str): 要执行的 Minecraft 指令。

            Raises:
                ValueError: 当指令执行失败时抛出。
            """
            cmd = " ".join(cmds)
            try:
                result = self.link_game_ctrl.sendcmd_with_resp(cmd, 10)
                if (result.OutputMessages[0].Message == "commands.generic.syntax") | (
                    result.OutputMessages[0].Message == "commands.generic.unknown"
                ):
                    Print.print_err(f'未知的 MC 指令, 可能是指令格式有误: "{cmd}"')
                else:
                    if game_text_handler := self.link_game_ctrl.game_data_handler:
                        msgs_output = " ".join(
                            json.dumps(i)
                            for i in game_text_handler.Handle_Text_Class1(
                                result.as_dict["OutputMessages"]
                            )
                        )
                    else:
                        msgs_output = json.dumps(
                            result.as_dict["OutputMessages"],
                            indent=2,
                            ensure_ascii=False,
                        )
                    desc = json.dumps(
                        result.OutputMessages[0].Parameters,
                        indent=2,
                        ensure_ascii=False,
                    )
                    if result.SuccessCount:
                        Print.print_suc("指令执行成功: " + msgs_output)
                        Print.print_suc(desc)
                    else:
                        Print.print_war("指令执行失败: " + msgs_output)
                        Print.print_war(desc)
            except IndexError as exec_err:
                if isinstance(result, type(None)):
                    raise ValueError("指令执行失败") from exec_err
                if result.SuccessCount:
                    Print.print_suc(
                        f"指令执行成功, 详细返回结果:\n{json.dumps(result.as_dict['OutputMessages'], indent=2, ensure_ascii=False)}"
                    )
            except TimeoutError:
                Print.print_err("[超时] 指令获取结果返回超时")

        def _send_to_neomega(cmds: list[str]):
            assert self.launcher.neomg_proc
            assert self.launcher.neomg_proc.stdin
            self.launcher.neomg_proc.stdin.write(" ".join(cmds) + "\n")
            self.launcher.neomg_proc.stdin.flush()

        def _basic_help(_):
            menu = self.get_console_menus()
            Print.print_inf("§a以下是可选的菜单指令项: ")
            for usage, arg_hint, _, triggers in menu:
                if arg_hint:
                    Print.print_inf(
                        f" §e{' 或 '.join(triggers)} §b{arg_hint} §f->  {usage}"
                    )
                else:
                    Print.print_inf(f" §e{' 或 '.join(triggers)}  §f->  {usage}")

        self.add_console_cmd_trigger(
            ["?", "help", "帮助", "？"],
            None,
            "查询可用菜单指令",
            _basic_help,
        )
        self.add_console_cmd_trigger(
            ["exit"], None, "退出并关闭ToolDelta", lambda _: self.system_exit()
        )
        self.add_console_cmd_trigger(
            ["插件市场"],
            None,
            "进入插件市场",
            lambda _: plugin_market.market.enter_plugin_market(
                self.plugin_market_url, in_game=True
            ),
        )
        self.add_console_cmd_trigger(
            ["/"], "[指令]", "执行 MC 指令", _execute_mc_command_and_get_callback
        )
        self.add_console_cmd_trigger(
            ["list"],
            None,
            "查询在线玩家",
            lambda _: Print.print_inf(
                "在线玩家：" + ", ".join(self.link_game_ctrl.allplayers)
            ),
        )
        self.add_console_cmd_trigger(
            ["reload"],
            None,
            "重载插件 (可能有部分特殊插件无法重载)",
            lambda _: self.reload() or 1,
        )
        if isinstance(self.launcher, FrameNeOmegaLauncher):
            self.add_console_cmd_trigger(
                ["o"], "neomega命令", "执行neomega控制台命令", _send_to_neomega
            )

    def comsole_cmd_active(self) -> None:
        """激活控制台命令输入"""
        self.init_console_menu()
        Print.print_suc("ToolHack Terminal 进程已注入, 允许开启标准输入")

        def _try_execute_console_cmd(func, rsp, mode, arg1) -> int | None:
            try:
                if mode == 0:
                    rsp_arg = rsp.split()[1:]
                elif mode == 1:
                    rsp_arg = rsp[len(arg1) :].split()
            except IndexError:
                Print.print_err("[控制台执行命令] 指令缺少参数")
                return None
            try:
                return func(rsp_arg) or 0
            except Exception:
                Print.print_err(f"控制台指令出错: {traceback.format_exc()}")
                return 0

        def _console_cmd_thread() -> None:
            """控制台线程"""
            while 1:
                rsp = ""
                try:
                    while True:
                        res = sys.stdin.read(1)
                        if res == "\n":  # 如果是换行符，则输出当前输入并清空输入
                            break
                        if res in ("", "^C", "^D"):
                            Print.print_inf("按退出键退出中...")
                            self.launcher.update_status(SysStatus.NORMAL_EXIT)
                            return
                        rsp += res
                    for _, _, func, triggers in self.consoleMenu:
                        if not rsp.strip():
                            continue
                        if rsp == "exit":
                            Print.print_inf("用户命令退出中...")
                            self.launcher.update_status(SysStatus.NORMAL_EXIT)
                            return
                        if rsp.split()[0] in triggers:
                            res = _try_execute_console_cmd(func, rsp, 0, None)
                            if res == 1:
                                break
                            elif res == -1:
                                return
                        else:
                            for tri in triggers:
                                if rsp.startswith(tri):
                                    res = _try_execute_console_cmd(func, rsp, 1, tri)
                                    if res == 1:
                                        break
                                    elif res == -1:
                                        return
                    if res != 0 and res != 1 and rsp:
                        self.link_game_ctrl.say_to("@a", f"[§b控制台§r] §3{rsp}§r")
                except Exception:
                    Print.print_err(f"控制台指令执行出现问题: {traceback.format_exc()}")
                    Print.print_err(
                        "§6虽然出现了问题, 但是您仍然可以继续使用控制台菜单"
                    )

        self.createThread(
            _console_cmd_thread,
            usage="控制台指令执行",
            thread_level=Utils.ToolDeltaThread.SYSTEM,
        )

    def system_exit(self) -> None:
        """系统退出"""
        asyncio.run(safe_jump())
        self.link_plugin_group.execute_frame_exit(self.on_plugin_err)
        if not isinstance(self.launcher, FrameNeOmgAccessPointRemote):
            with contextlib.suppress(Exception):
                self.link_game_ctrl.sendwscmd(
                    f"/kick {self.link_game_ctrl.bot_name} ToolDelta 退出中。"
                )
            if not isinstance(self.launcher.neomg_proc, type(None)):
                if os.name == "nt":
                    self.launcher.neomg_proc.send_signal(signal.CTRL_BREAK_EVENT)
                else:
                    self.launcher.neomg_proc.send_signal(signal.SIGTERM)

        if isinstance(self.launcher, FB_LIKE_LAUNCHERS):
            self.launcher.exit_event.set()

    def get_console_menus(self) -> list:
        """获取控制台命令列表

        Returns:
            list: 命令列表
        """
        return self.consoleMenu

    def set_game_control(self, game_ctrl: "GameCtrl") -> None:
        """使用外源 GameControl

        Args:help
            game_ctrl (_type_): GameControl 对象
        """
        self.link_game_ctrl = game_ctrl

    def set_plugin_group(self, plug_grp) -> None:
        """使用外源 PluginGroup

        Args:
            plug_grp (_type_): PluginGroup 对象
        """
        self.link_plugin_group: "PluginGroup" = plug_grp

    def get_game_control(self) -> "GameCtrl":
        """获取 GameControl 对象

        Returns:
            GameCtrl: GameControl 对象
        """
        gcl: "GameCtrl" = self.link_game_ctrl
        return gcl

    @staticmethod
    def safelyExit() -> None:
        """安全退出"""
        utils.safe_close()
        publicLogger.exit()
        Print.print_inf("已保存数据与日志等信息。")

    def reload(self):
        """重载所有插件"""
        try:
            Print.print_inf("重载插件: 正在保存数据缓存文件..")
            utils.safe_close()
            self.consoleMenu.clear()
            Print.print_inf("重载插件: 正在重新载入插件..")
            self.link_plugin_group.reload()
            self.launcher.reload_listen_packets(
                self.link_game_ctrl.require_listen_packets
            )
            Print.print_suc("重载插件: 全部插件重载成功！")
        except Config.ConfigError as err:
            Print.print_err(f"重载插件时发现插件配置文件有误: {err}")
        except SystemExit:
            Print.print_err("重载插件遇到问题")
        except BaseException:
            Print.print_err("重载插件遇到问题 (报错如下):")
            Print.print_err(traceback.format_exc())
        finally:
            self.init_console_menu()


class GameCtrl:
    """游戏连接和交互部分"""

    def __init__(self, frame: "ToolDelta"):
        """初始化

        Args:
            frame (Frame): 继承 Frame 的对象
        """
        frame.basic_operation()
        try:
            self.game_texts_data = GameTextsLoader().game_texts_data
            self.game_data_handler = GameTextsHandle(self.game_texts_data)
        except Exception as err:
            Print.print_war(f"游戏文本翻译器不可用: {err}")
            self.game_texts_data = None
            self.game_data_handler = None
        self.linked_frame = frame
        self.players_uuid: dict[str, str] = {}
        self.allplayers: list[str] = []
        self.all_players_data = {}
        self.linked_frame: ToolDelta
        self.require_listen_packets = {9, 79, 63}
        self.launcher = self.linked_frame.launcher
        if isinstance(self.launcher, LAUNCHERS):
            self.launcher.packet_handler = lambda pckType, pck: Utils.createThread(
                self.packet_handler,
                (pckType, pck),
                usage="数据包处理",
                thread_level=Utils.ToolDeltaThread.SYSTEM,
            )
        # 初始化基本函数
        self.sendcmd = self.launcher.sendcmd
        self.sendwscmd = self.launcher.sendwscmd
        self.sendwocmd = self.launcher.sendwocmd
        self.sendPacket = self.launcher.sendPacket
        if isinstance(self.linked_frame.launcher, FrameNeOmgAccessPoint):
            self.requireUUIDPacket = False
        else:
            self.requireUUIDPacket = True

    def set_listen_packets_to_launcher(self) -> None:
        """
        向启动器初始化监听的游戏数据包
        仅限启动模块调用
        """
        self.launcher.add_listen_packets(*self.require_listen_packets)

    def add_listen_packet(self, pkt: int) -> None:
        """
        添加监听的数据包
        仅限内部与插件加载器调用

        Args:
            pkt (int): 数据包 ID
        """
        self.require_listen_packets.add(pkt)

    @Utils.thread_func("数据包处理方法", Utils.ToolDeltaThread.SYSTEM)
    def packet_handler(self, pkt_type: int, pkt: dict) -> None:
        """数据包处理分发任务函数

        Args:
            pkt_type (int): 数据包类型
            pkt (dict): 数据包内容
        """
        is_skiped = self.linked_frame.link_plugin_group.processPacketFunc(pkt_type, pkt)
        if is_skiped:
            return
        if pkt_type == PacketIDS.IDPlayerList:
            self.process_player_list(pkt, self.linked_frame.link_plugin_group)
        elif pkt_type == PacketIDS.IDText:
            self.process_text_packet(pkt, self.linked_frame.link_plugin_group)

    def process_player_list(self, pkt: dict, plugin_group: "PluginGroup") -> None:
        """处理玩家列表等数据包

        Args:
            pkt (dict): 数据包内容
            plugin_group (PluginGroup): 插件组对象
        """
        # 处理玩家进出事件
        res = self.launcher.get_players_and_uuids()
        if res:
            self.allplayers = list(res.keys())
            self.players_uuid.update(res)
        for player in pkt["Entries"]:
            isJoining = bool(player["Skin"]["SkinData"])
            playername = player["Username"]
            if isJoining and "§" in playername:
                self.say_to(
                    "@a",
                    "§l§7<§6§o!§r§l§7> §6此玩家名字中含特殊字符, 可能导致插件运行异常！",
                )
                self.all_players_data = self.launcher.omega.get_all_online_players()
            if isJoining:
                self.tmp_tp_player(playername)
                Print.print_inf(f"§e{playername} 加入了游戏")
                self.all_players_data = self.launcher.omega.get_all_online_players()
                if playername not in self.allplayers and not res:
                    self.allplayers.append(playername)
                    return
                plugin_group.execute_player_prejoin(
                    playername, self.linked_frame.on_plugin_err
                )
            else:
                playername = next(
                    (k for k, v in self.players_uuid.items() if v == player["UUID"]),
                    None,
                )
                if playername is None:
                    Print.print_war("无法获取 PlayerList 中玩家名字")
                    continue
                if playername != "???" and not res:
                    self.allplayers.remove(playername)
                Print.print_inf(f"§e{playername} 退出了游戏")
                self.all_players_data = self.launcher.omega.get_all_online_players()
                plugin_group.execute_player_leave(
                    playername, self.linked_frame.on_plugin_err
                )

    def process_text_packet(self, pkt: dict, plugin_grp: "PluginGroup") -> None:
        """处理 9 号数据包的消息

        Args:
            pkt (dict): 数据包内容
            plugin_grp (PluginGroup): 插件组对象
        """
        match pkt["TextType"]:
            case 2:
                if pkt["Message"] == "§e%multiplayer.player.joined":
                    player = pkt["Parameters"][0]
                    plugin_grp.execute_player_join(
                        player, self.linked_frame.on_plugin_err
                    )
                elif not pkt["Message"].startswith("§e%multiplayer.player.joined"):
                    if self.game_data_handler is not None:
                        jon = self.game_data_handler.Handle_Text_Class1(pkt)
                        Print.print_inf("§1" + " ".join(jon).strip('"'))
                    else:
                        Print.print_inf(pkt["Message"])
                    if pkt["Message"].startswith("death."):
                        if len(pkt["Parameters"]) >= 2:
                            killer = pkt["Parameters"][1]
                        else:
                            killer = None
                        plugin_grp.execute_player_death(
                            pkt["Parameters"][0],
                            killer,
                            pkt["Message"],
                            self.linked_frame.on_plugin_err,
                        )
            case 1 | 7:
                original_playername, msg = pkt["SourceName"], pkt["Message"]
                playername = Utils.to_plain_name(original_playername)
                # game_utils.waitMsg 需要监听玩家信息
                # 监听后, 消息仍被处理
                if playername in game_utils.player_waitmsg_cb.keys():
                    game_utils.player_waitmsg_cb[playername](msg)
                plugin_grp.execute_player_message(
                    playername, msg, self.linked_frame.on_plugin_err
                )
                Print.print_inf(f"<{playername}> {msg}")
            case 8:
                original_playername, msg = pkt["SourceName"], pkt["Message"]
                playername = Utils.to_plain_name(original_playername)
                Print.print_inf(
                    f"{playername} 使用 say 说：{msg.strip(f'[{playername}]')}"
                )
                plugin_grp.execute_command(
                    playername, msg, self.linked_frame.on_plugin_err
                )
            case 9:
                msg = pkt["Message"]
                try:
                    msg_text = json.loads(msg)["rawtext"]
                    if len(msg_text) > 0 and msg_text[0].get("translate") == "***":
                        Print.print_with_info("(该 tellraw 内容为敏感词)", "§f 消息 ")
                        return
                    msg_text = "".join([i["text"] for i in msg_text])
                    Print.print_with_info(msg_text, "§f 消息 ")
                except Exception:
                    pass

    def system_inject(self) -> None:
        """载入游戏时的初始化"""
        if hasattr(self.launcher, "bot_name"):
            self.tmp_tp_all_players()
        res = self.launcher.get_players_and_uuids()
        self.all_players_data = self.launcher.omega.get_all_online_players()
        self.give_bot_effect_invisibility()
        if res:
            self.allplayers = list(res.keys())
            self.players_uuid.update(res)
        else:
            while 1:
                try:
                    cmd_result = self.sendcmd_with_resp("/list")
                    if (
                        cmd_result.OutputMessages is None
                        or len(cmd_result.OutputMessages) < 2
                    ):
                        raise ValueError
                    if (
                        cmd_result.OutputMessages[1].Parameters is None
                        or len(cmd_result.OutputMessages[1].Parameters) < 1
                    ):
                        raise ValueError
                    self.allplayers = (
                        cmd_result.OutputMessages[1].Parameters[0].split(", ")
                    )
                    break
                except (TimeoutError, ValueError):
                    Print.print_war("获取全局玩家失败..重试")
        self.linked_frame.link_plugin_group.execute_init(
            self.linked_frame.on_plugin_err
        )
        self.inject_welcome()

    def inject_welcome(self) -> None:
        """初始化欢迎信息"""
        Print.print_suc(
            "成功连接到游戏网络并初始化, 在线玩家: "
            + ", ".join(self.allplayers)
            + ", 机器人 ID: "
            + self.bot_name
        )
        self.sendcmd("/tag @s add robot")
        Print.print_inf(
            "在控制台输入 §b插件市场§r 以§a一键获取§rToolDelta官方和第三方的插件"
        )
        Print.print_suc("在控制台输入 §fhelp / ?§r§a 可查看控制台命令")
        if isinstance(self.launcher, FrameNeOmegaLauncher):
            Print.print_suc("在控制台输入 o <neomega指令> 可执行NeOmega的控制台指令")

    @property
    def bot_name(self) -> str:
        if hasattr(self.launcher, "bot_name"):
            return self.launcher.get_bot_name()
        raise ValueError("此启动器框架无法产生机器人名")

    def sendcmd_with_resp(self, cmd: str, timeout: float = 30) -> Packet_CommandOutput:
        resp: Packet_CommandOutput = self.sendwscmd(cmd, True, timeout)  # type: ignore
        return resp

    def say_to(self, target: str, text: str) -> None:
        """向玩家发送消息

        Args:
            target (str): 玩家名/目标选择器
            msg (str): 消息
        """
        text_json = json.dumps({"rawtext": [{"text": text}]}, ensure_ascii=False)
        self.sendwocmd(f"tellraw {target} {text_json}")

    def player_title(self, target: str, text: str) -> None:
        """向玩家展示标题文本

        Args:
            target (str): 玩家名/目标选择器
            text (str): 文本
        """
        text_json = json.dumps({"rawtext": [{"text": text}]}, ensure_ascii=False)
        self.sendwocmd(f"titleraw {target} title {text_json}")

    def player_subtitle(self, target: str, text: str) -> None:
        """向玩家展示副标题文本

        Args:
            target (str): 玩家名/目标选择器
            text (str): 文本
        """
        text_json = json.dumps({"rawtext": [{"text": text}]}, ensure_ascii=False)
        self.sendwocmd(f"titleraw {target} subtitle {text_json}")

    def player_actionbar(self, target: str, text: str) -> None:
        """向玩家展示动作栏文本

        Args:
            target (str): 玩家名/目标选择器
            text (str): 文本
        """
        text_json = json.dumps({"rawtext": [{"text": text}]}, ensure_ascii=False)
        self.sendwocmd(f"titleraw {target} actionbar {text_json}")

    def get_game_data(self) -> dict:
        """获取游戏常见字符串数据

        Returns:
            dict: 游戏常见字符串数据
        """
        if self.game_texts_data is None:
            raise ValueError("游戏翻译器字符串数据不可用")
        return self.game_texts_data

    @Utils.timer_event(6400, "给予机器人隐身效果", Utils.ToolDeltaThread.SYSTEM)
    def give_bot_effect_invisibility(self) -> None:
        """给机器人添加隐身效果"""
        self.sendwocmd(f"/effect {self.bot_name} invisibility 99999 255 true")

    def tmp_tp_all_players(self) -> None:
        """
        内部调用：在 ToolDelta 连接到 NeOmega 后先 tp 所有玩家（防止玩家 entityruntimeid 为空）
        外部调用：临时传送至所有玩家后回到原位
        """
        BotPos: tuple[float, float, float] = getPosXYZ(self.bot_name)
        for player in self.allplayers:
            if player == self.bot_name:
                continue
            self.sendwocmd(f"tp {self.bot_name} {player}")
        self.sendwocmd(
            f"tp {self.bot_name} {str(int(BotPos[0])) + ' ' + str(int(BotPos[1])) + ' ' + str(int(BotPos[2]))}"
        )

    def tmp_tp_player(self, player: str) -> None:
        """临时传送玩家 (看一眼玩家就回来，多数用于捕获数据)
        Args:

            player (str): 玩家名

        """
        BotPos: tuple[float, float, float] = getPosXYZ(self.bot_name)
        self.sendwocmd(f"tp {self.bot_name} {player}")
        self.sendwocmd(
            f"tp {self.bot_name} {str(int(BotPos[0])) + ' ' + str(int(BotPos[1])) + ' ' + str(int(BotPos[2]))}"
        )

    def get_player_name_from_entity_runtime(self, runtimeid: int) -> str | None:
        """根据实体 runtimeid 获取玩家名

        Args:
            runtimeid (int): 实体 RuntimeID

        Returns:
            str | None: 玩家名
        """
        if not self.all_players_data:
            return None
        for player in self.all_players_data:
            if player.entity_runtime_id == runtimeid:
                return player.name
        return None

    def get_player_entity_runtime_id_from_name(self, player_name: str) -> int | None:
        """
        根据玩家名获取实体 runtimeid

        Args:
            player_name (str): 玩家名

        Returns:
            int | None: 实体 runtimeid
        """
        if not self.all_players_data:
            return None
        for player in self.all_players_data:
            if player.name == player_name:
                return player.entity_runtime_id
