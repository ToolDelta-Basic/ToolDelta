"""
ToolDelta基本框架

整个系统由三个部分组成
    Frame: 负责整个 ToolDelta 的基本框架运行
    GameCtrl: 负责对接游戏
        - Launchers: 负责将不同启动器的游戏接口统一成固定的接口, 供插件在多平台游戏接口运行(FastBuilder External, NeOmega, (TLSP, etc.))
    PluginGroup: 负责对插件进行统一管理
"""

import os
import sys
import time
import getpass
import traceback
from typing import TYPE_CHECKING, Callable
import asyncio
import ujson as json
import requests
import tooldelta
from tooldelta import (
    auths,
    constants,
    plugin_market,
)
from .constants import PRG_NAME
from .utils import Utils, safe_close
from .plugin_load.injected_plugin import safe_jump
from .get_tool_delta_version import get_tool_delta_version
from .color_print import Print
from .cfg import Cfg
from .logger import publicLogger
from .game_texts import GameTextsLoader, GameTextsHandle
from .urlmethod import if_token, fbtokenFix
from .sys_args import sys_args_to_dict
from .launch_cli import (
    FrameNeOmg,
    FrameNeOmgRemote,
    SysStatus,
)

from .packets import PacketIDS

sys_args_dict = sys_args_to_dict(sys.argv)
VERSION = get_tool_delta_version()
Config = Cfg()

if TYPE_CHECKING:
    from .plugin_load.PluginGroup import PluginGroup

LAUNCHERS: list[
    tuple[str, type[FrameNeOmg | FrameNeOmgRemote]]
] = [
    ("NeOmega 框架 (NeOmega模式, 租赁服适应性强, 推荐)", FrameNeOmg),
    (
        "NeOmega 框架 (NeOmega连接模式, 需要先启动对应的neOmega接入点)",
        FrameNeOmgRemote,
    ),
]

class Frame:
    """ToolDelta主框架"""

    class FrameBasic:
        """系统基本信息"""
        system_version = VERSION
        max_connect_fb_time = 60
        connect_fb_start_time = time.time()
        data_path = "插件数据文件/"

    class SystemVersionException(ImportError):
        """系统版本异常"""
        msg: str

    def __init__(self) -> None:
        """初始化"""
        self.createThread = Utils.createThread
        self.sys_data = self.FrameBasic()
        self.serverNumber: int = 0
        self.serverPasswd: str = ""
        self.launchMode: int = 0
        self.consoleMenu = []
        self.on_plugin_err = staticmethod(
            lambda name, _, err: Print.print_err(f"插件 <{name}> 出现问题: \n{err}")
        )
        self.launcher: FrameNeOmg | FrameNeOmgRemote
        self.is_mir: bool
        self.plugin_market_url: str
        self.link_game_ctrl: "GameCtrl"
        self.link_plugin_group: "PluginGroup"

    def loadConfiguration(self) -> None:
        """加载配置文件"""
        Config.default_cfg("ToolDelta基本配置.json", constants.LAUNCH_CFG)
        try:
            # 读取配置文件
            cfgs = Config.get_cfg("ToolDelta基本配置.json",
                                  constants.LAUNCH_CFG_STD)
            self.serverNumber = cfgs["服务器号"]
            self.serverPasswd = cfgs["密码"]
            self.launchMode = cfgs["启动器启动模式(请不要手动更改此项, 改为0可重置)"]
            self.is_mir = cfgs["是否使用github镜像"]
            self.plugin_market_url = cfgs["插件市场源"]
            auth_server = cfgs["验证服务器地址(更换时记得更改fbtoken)"]
            publicLogger.switch_logger(cfgs["是否记录日志"])
            if self.launchMode != 0 and self.launchMode not in range(1, len(LAUNCHERS) + 1):
                raise Config.ConfigError("你不该随意修改启动器模式, 现在赶紧把它改回0吧")
        except Config.ConfigError as err:
            # 配置文件有误
            r = self.upgrade_cfg()
            if r:
                Print.print_war("配置文件未升级, 已自动升级, 请重启 ToolDelta")
            else:
                Print.print_err(f"ToolDelta基本配置有误, 需要更正: {err}")
            raise SystemExit from err
        if self.serverNumber == 0:
            while 1:
                try:
                    self.serverNumber = int(input(
                        Print.fmt_info("请输入租赁服号: ", "§b 输入 ")
                    ))
                    self.serverPasswd = (
                        getpass.getpass(
                            Print.fmt_info(
                                "请输入租赁服密码(不会回显, 没有请直接回车): ", "§b 输入 "
                            )
                        )
                        or "0"
                    )
                    std = constants.LAUNCH_CFG.copy()
                    std["服务器号"] = int(self.serverNumber)
                    std["密码"] = int(self.serverPasswd)
                    Config.default_cfg("ToolDelta基本配置.json", std, True)
                    Print.print_suc("登录配置设置成功")
                    cfgs = std
                    break
                except Exception:
                    Print.print_err("输入有误， 租赁服号和密码应当是纯数字")
        auth_servers = constants.AUTH_SERVERS
        if auth_server == "":
            Print.print_inf("选择 ToolDelta机器人账号 使用的验证服务器:")
            for i, (auth_server_name, _) in enumerate(auth_servers):
                Print.print_inf(f" {i + 1} - {auth_server_name}")
            Print.print_inf(
                "§cNOTE: 使用的机器人账号是在哪里获取的就选择哪一个验证服务器, 不能混用"
            )
            while 1:
                try:
                    ch = int(input(Print.fmt_info("请选择: ", "§f 输入 ")))
                    if ch not in range(1, len(auth_servers) + 1):
                        raise ValueError
                    cfgs["验证服务器地址(更换时记得更改fbtoken)"] = auth_servers[
                        ch - 1
                    ][1]
                    break
                except ValueError:
                    Print.print_err("输入不合法, 或者是不在范围内, 请重新输入")
            Config.default_cfg("ToolDelta基本配置.json", cfgs, True)
            # 读取启动配置等
        if not os.path.isfile("fbtoken"):
            Print.print_inf(
                "请选择登录方法:\n 1 - 使用账号密码(登录成功后将自动获取Token到工作目录)\n 2 - 使用Token(如果Token文件不存在则需要输入或将文件放入工作目录)\r"
            )
            Login_method: str = input(Print.fmt_info("请输入你的选择:", "§6 输入 "))
            while True:
                if Login_method.isdigit() is False:
                    Login_method = input(
                        Print.fmt_info("输入有误, 请输入正确的序号: ", "§6 警告 ")
                    )
                elif int(Login_method) > 2 or int(Login_method) < 1:
                    Login_method = input(
                        Print.fmt_info("输入有误, 请输入正确的序号: ", "§6 警告 ")
                    )
                else:
                    break
            if Login_method == "1":
                try:
                    match cfgs["验证服务器地址(更换时记得更改fbtoken)"]:
                        case "https://liliya233.uk":
                            token = auths.liliya_login()
                        case "https://api.fastbuilder.pro":
                            token = auths.fbuc_login()
                        case _:
                            Print.print_err("暂无法登录该验证服务器")
                            raise SystemExit
                    with open("fbtoken", "w", encoding="utf-8") as f:
                        f.write(token)
                except requests.exceptions.RequestException as e:
                    Print.print_err(f"登录失败，原因：{e}\n正在切换至Token登录")
            if_token()

        if self.launchMode == 0:
            Print.print_inf("请选择启动器启动模式(之后可在ToolDelta启动配置更改):")
            for i, (launcher_name, _) in enumerate(LAUNCHERS):
                Print.print_inf(f" {i + 1} - {launcher_name}")
            while 1:
                try:
                    ch = int(input(Print.fmt_info("请选择: ", "§f 输入 ")))
                    if ch not in range(1, len(LAUNCHERS) + 1):
                        raise ValueError
                    cfgs["启动器启动模式(请不要手动更改此项, 改为0可重置)"] = ch
                    break
                except ValueError:
                    Print.print_err("输入不合法, 或者是不在范围内, 请重新输入")
            Config.default_cfg("ToolDelta基本配置.json", cfgs, True)
        # 修复fbtoken
        fbtokenFix()
        with open("fbtoken", "r", encoding="utf-8") as f:
            fbtoken = f.read()
        self.launcher = LAUNCHERS[
            cfgs["启动器启动模式(请不要手动更改此项, 改为0可重置)"] - 1
        ][1](
            self.serverNumber,
            self.serverPasswd,
            fbtoken,
            auth_server,
        )

    @staticmethod
    def change_config():
        "修改配置文件"
        try:
            old_cfg = Config.get_cfg("ToolDelta基本配置.json", constants.LAUNCH_CFG_STD)
        except FileNotFoundError:
            Print.clean_print("§c未初始化配置文件, 无法进行修改")
            return
        except Config.ConfigError as err:
            Print.print_err(f"配置文件损坏: {err}")
            return
        if (old_cfg['启动器启动模式(请不要手动更改此项, 改为0可重置)'] - 1) not in range(0, 2):
            Print.print_err(f"配置文件损坏: 启动模式错误: {old_cfg['启动器启动模式(请不要手动更改此项, 改为0可重置)'] - 1}")
            return
        while 1:
            md = (
                "NeOmega 框架 (NeOmega模式, 租赁服适应性强, 推荐)",
                "NeOmega 框架 (NeOmega连接模式, 需要先启动对应的neOmega接入点)",
            )
            Print.clean_print("§b现有配置项如下:")
            Print.clean_print(f" 1. 租赁服号: {old_cfg['服务器号']}")
            Print.clean_print(f" 2. 密码: <已隐藏>")
            Print.clean_print(f" 3. 启动器启动模式: {md[old_cfg['启动器启动模式(请不要手动更改此项, 改为0可重置)'] - 1]}")
            Print.clean_print(f" 4. 是否记录日志: {old_cfg['是否记录日志']}")
            Print.clean_print(f" 5. 验证服务器地址: {old_cfg['验证服务器地址(更换时记得更改fbtoken)']}")
            Print.clean_print(f"    §a直接回车: 保存并退出")
            resp = input(Print.clean_fmt("§6输入序号可修改配置项(0~4): ")).strip()
            if resp == "":
                Config.default_cfg("ToolDelta基本配置.json", old_cfg, True)
                Print.clean_print("§a配置已保存!")
                return
            match resp:
                case "1":
                    n = Utils.try_int(input(Print.clean_fmt("§b请输入租赁服号: ")))
                    if n is None:
                        input(Print.clean_fmt("§c不是合法租赁服号, 回车键继续"))
                        continue
                    old_cfg["服务器号"] = n
                    input(Print.clean_fmt(f"§f新的租赁服号: §a{n}§f, 回车键继续"))
                case "2":
                    n = getpass.getpass(Print.clean_fmt("§b请输入租赁服密码(自动隐藏): "))
                    if len(n) != 6:
                        input(Print.clean_fmt("§c不是合法租赁服六位数密码, 回车键继续"))
                        continue
                    n = Utils.try_int(n)
                    if n is None:
                        input(Print.clean_fmt("§c不是合法租赁服密码, 回车键继续"))
                        continue
                    old_cfg["密码"] = n
                    input(Print.clean_fmt(f"§f新的租赁服密码: §a******§f, 回车键继续"))
                case "3":
                    Print.print_inf("选择启动器启动模式(之后可在ToolDelta启动配置更改):")
                    for i, (launcher_name, _) in enumerate(LAUNCHERS):
                        Print.print_inf(f" {i + 1} - {launcher_name}")
                    while 1:
                        try:
                            ch = int(input(Print.clean_fmt("请选择: ")))
                            if ch not in range(1, len(LAUNCHERS) + 1):
                                raise ValueError
                            old_cfg["启动器启动模式(请不要手动更改此项, 改为0可重置)"] = ch
                            break
                        except ValueError:
                            Print.print_err("输入不合法, 或者是不在范围内, 请重新输入")
                            continue
                    input(Print.clean_fmt(f"§a已选择启动器启动模式: §f{md[old_cfg['启动器启动模式(请不要手动更改此项, 改为0可重置)'] - 1]}, 回车键继续"))
                case "4":
                    old_cfg['是否记录日志'] = [True, False][old_cfg['是否记录日志']]
                    input(Print.clean_fmt(f"日志记录模式已改为: {['§c关闭', '§a开启'][old_cfg['是否记录日志']]}, 回车键继续"))
                case "5":
                    n = input(Print.clean_fmt("§b请输入验证服务器地址: "))
                    if not n.startswith("http://") and not n.startswith("https://"):
                        input(Print.clean_fmt("§c不合法URL地址, 回车键继续"))
                        continue
                    old_cfg['验证服务器地址(更换时记得更改fbtoken)'] = n
                    input(Print.clean_fmt(f"§a验证服务器已设置, 回车键继续"))

    @staticmethod
    def upgrade_cfg() -> bool:
        """升级配置文件

        Returns:
            bool: 是否升级了配置文件
        """
        old_cfg = Config.get_cfg("ToolDelta基本配置.json", {})
        old_cfg_keys = old_cfg.keys()
        need_upgrade_cfg = False
        for k, v in constants.LAUNCH_CFG.items():
            if k not in old_cfg_keys:
                old_cfg[k] = v
                need_upgrade_cfg = True
        if need_upgrade_cfg:
            Config.default_cfg("ToolDelta基本配置.json", old_cfg, True)
        return need_upgrade_cfg

    def welcome(self) -> None:
        """欢迎提示"""
        Print.print_with_info(
            f"§d{PRG_NAME} Panel Embed By SuperScript", Print.INFO_LOAD
        )
        Print.print_with_info(
            f"§d{PRG_NAME} Wiki: https://tooldelta-wiki.tblstudio.cn/", Print.INFO_LOAD
        )
        Print.print_with_info(
            f"§d{PRG_NAME} 项目地址: https://github.com/ToolDelta", Print.INFO_LOAD
        )
        Print.print_with_info(
            f"§d{PRG_NAME} v {'.'.join([str(i) for i in VERSION])}", Print.INFO_LOAD
        )
        Print.print_with_info(f"§d{PRG_NAME} Panel 已启动", Print.INFO_LOAD)

    @staticmethod
    def plugin_load_finished(plugins: "PluginGroup"):
        """插件加载完成时的回调函数

        Args:
            plugins (PluginGroup): 插件组对象，包含已加载的插件信息
        """
        Print.print_suc(
            f"成功载入 §f{plugins.normal_plugin_loaded_num}§a 个组合式插件, §f{plugins.injected_plugin_loaded_num}§a 个注入式插件"
        )

    @staticmethod
    def basic_operation():
        """初始化文件夹"""
        os.makedirs(
            f"插件文件/{constants.TOOLDELTA_CLASSIC_PLUGIN}", exist_ok=True)
        os.makedirs(
            f"插件文件/{constants.TOOLDELTA_INJECTED_PLUGIN}", exist_ok=True)
        os.makedirs("插件配置文件", exist_ok=True)
        os.makedirs("tooldelta/neo_libs", exist_ok=True)
        os.makedirs("插件数据文件/game_texts", exist_ok=True)

    def add_console_cmd_trigger(
        self,
        triggers: list[str],
        arg_hint: str | None,
        usage: str,
        func: Callable[[list[str]], None],
    ) -> None:
        """注册ToolDelta控制台的菜单项

        Args:
            triggers (list[str]): 触发词列表
            arg_hint (str | None): 菜单命令参数提示句
            usage (str): 命令说明
            func (Callable[[list[str]], None]): 菜单回调方法
        """
        try:
            if self.consoleMenu.index(triggers) != -1:
                Print.print_war(f"§6后台指令关键词冲突: {func}, 不予添加至指令菜单")
        except Exception:
            self.consoleMenu.append([usage, arg_hint, func, triggers])

    def init_basic_help_menu(self, _) -> None:
        """初始化基本的帮助菜单"""
        menu = self.get_console_menus()
        Print.print_inf("§a以下是可选的菜单指令项: ")
        for usage, arg_hint, _, triggers in menu:
            if arg_hint:
                Print.print_inf(
                    f" §e{' 或 '.join(triggers)} §b{arg_hint} §f->  {usage}")
            else:
                Print.print_inf(f" §e{' 或 '.join(triggers)}  §f->  {usage}")

    def comsole_cmd_start(self) -> None:
        """启动控制台命令"""
        def _try_execute_console_cmd(func, rsp, mode, arg1):
            try:
                if mode == 0:
                    rsp_arg = rsp.split()[1:]
                elif mode == 1:
                    rsp_arg = rsp[len(arg1):].split()
            except IndexError:
                Print.print_err("[控制台执行命令] 指令缺少参数")
                return
            try:
                return func(rsp_arg) or 0
            except Exception:
                Print.print_err(f"控制台指令出错： {traceback.format_exc()}")
                return 0

        @Utils.thread_func
        def _execute_mc_command_and_get_callback(cmd: str) -> None:
            """执行Minecraft指令并获取回调结果。

            Args:
                cmd (str): 要执行的Minecraft指令。

            Raises:
                ValueError: 当指令执行失败时抛出。
            """
            cmd = " ".join(cmd)
            try:
                result = self.link_game_ctrl.sendcmd(cmd, True, 10)
                if isinstance(result, type(None)):
                    raise ValueError("指令执行失败")
                if (result.OutputMessages[0].Message == "commands.generic.syntax") | (
                    result.OutputMessages[0].Message == "commands.generic.unknown"
                ):
                    Print.print_err(f'未知的MC指令， 可能是指令格式有误： "{cmd}"')
                else:
                    mjon = self.link_game_ctrl.Game_Data_Handle.Handle_Text_Class1(result.as_dict["OutputMessages"])
                    if not result.SuccessCount:
                        print_str = "指令执行失败: " + " ".join(mjon); Print.print_war(print_str)
                        Print.print_war(result.as_dict["OutputMessages"])
                    else:
                        print_str = "指令执行成功: " + " ".join(mjon); Print.print_suc(print_str)
                        Print.print_suc(result.as_dict["OutputMessages"])

            except IndexError as exec_err:
                if isinstance(result, type(None)):
                    raise ValueError("指令执行失败") from exec_err
                if result.SuccessCount:
                    Print.print_suc(
                        f"指令执行成功: \n{json.dumps(result.as_dict['OutputMessages'], indent=2, ensure_ascii=False)}"
                    )
            except TimeoutError:
                Print.print_err("[超时] 指令获取结果返回超时")

        def _console_cmd_thread() -> None:
            """控制台线程"""
            self.add_console_cmd_trigger(
                ["?", "help", "帮助"],
                None,
                "查询可用菜单指令",
                self.init_basic_help_menu,
            )
            self.add_console_cmd_trigger(
                ["exit"],
                None,
                f"退出并关闭{PRG_NAME}",
                lambda _: tooldelta.safe_jump(out_task=True),
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
                ["/"],
                "[指令]",
                "执行MC指令",
                _execute_mc_command_and_get_callback
            )
            self.add_console_cmd_trigger(
                ["list"],
                None,
                "查询在线玩家",
                lambda _: Print.print_inf(
                    "在线玩家: " + ", ".join(self.link_game_ctrl.allplayers)
                ),
            )
            while 1:
                rsp = ""
                while True:
                    res = sys.stdin.read(1)
                    if res == "\n":  # 如果是换行符，则输出当前输入并清空输入
                        break
                    if res in ("", "^C", "^D"):
                        Print.print_inf("按退出键退出中...")
                        if isinstance(self.launcher, (FrameNeOmgRemote, FrameNeOmg)):
                            self.launcher.status = SysStatus.NORMAL_EXIT
                        self.system_exit()
                        return
                    rsp += res
                for _, _, func, triggers in self.consoleMenu:
                    if not rsp:
                        continue
                    if rsp.split()[0] in triggers:
                        res = _try_execute_console_cmd(func, rsp, 0, None)
                        if res == -1:
                            return
                    else:
                        for tri in triggers:
                            if rsp.startswith(tri):
                                res = _try_execute_console_cmd(
                                    func, rsp, 1, tri)
                                if res == -1:
                                    return
                if res != 0 and rsp:
                    self.link_game_ctrl.say_to('@a', f'[§bToolDelta控制台§r] §3{rsp}§r')

        self.createThread(_console_cmd_thread, usage="控制台指令")

    def system_exit(self) -> None:
        """系统退出"""
        asyncio.run(safe_jump())
        self.link_plugin_group.execute_frame_exit(self.on_plugin_err)
        exit_status_code = getattr(self.launcher, "secret_exit_key", "null")
        if self.link_game_ctrl.allplayers and not isinstance(
            self.launcher, (FrameNeOmgRemote,)
        ):
            try:
                self.link_game_ctrl.sendwscmd(
                    f"/kick {self.link_game_ctrl.bot_name} ToolDelta 退出中(看到这条消息请重新加入游戏)\nSTATUS CODE: {exit_status_code}"
                )
            except Exception:
                pass
        time.sleep(0.5)
        if isinstance(self.launcher, (FrameNeOmgRemote, FrameNeOmg)):
            self.launcher.exit_event.set()

    def get_console_menus(self) -> list:
        """获取控制台命令列表

        Returns:
            list: 命令列表
        """
        return self.consoleMenu

    def set_game_control(self, game_ctrl) -> None:
        """使用外源GameControl

        Args:
            game_ctrl (_type_): GameControl对象
        """
        self.link_game_ctrl: "GameCtrl" = game_ctrl

    def set_plugin_group(self, plug_grp) -> None:
        """使用外源PluginGroup

        Args:
            plug_grp (_type_): PluginGroup对象
        """
        self.link_plugin_group: "PluginGroup" = plug_grp

    def get_game_control(self) -> "GameCtrl":
        """获取GameControl对象

        Returns:
            GameCtrl: GameControl对象
        """
        gcl: "GameCtrl" = self.link_game_ctrl
        return gcl

    @staticmethod
    def safelyExit() -> None:
        """安全退出"""
        safe_close()
        publicLogger.exit()
        Print.print_inf("已保存数据与日志等信息.")


class GameCtrl:
    """游戏连接和交互部分"""

    def __init__(self, frame: "Frame"):
        """初始化

        Args:
            frame (Frame): 继承Frame的对象
        """
        frame.basic_operation()
        self.Game_Data = GameTextsLoader().game_texts_data
        self.Game_Data_Handle = GameTextsHandle(self.Game_Data)
        self.linked_frame = frame
        self.players_uuid = {}
        self.allplayers = []
        self.bot_name = ""
        self.linked_frame: Frame
        self.pkt_unique_id: int = 0
        self.pkt_cache: list = []
        self.require_listen_packets = {9, 79, 63}
        self.store_uuid_pkt: dict[str, str] | None = None
        self.launcher = self.linked_frame.launcher
        if isinstance(self.launcher, (FrameNeOmgRemote, FrameNeOmg)):
            self.launcher.packet_handler = lambda pckType, pck: Utils.createThread(
                self.packet_handler, (pckType, pck), usage="数据包处理")
        # 初始化基本函数
        self.sendcmd = self.launcher.sendcmd
        self.sendwscmd = self.launcher.sendwscmd
        self.sendwocmd = self.launcher.sendwocmd
        self.sendPacket = self.launcher.sendPacket
        if isinstance(self.linked_frame.launcher, FrameNeOmg):
            self.requireUUIDPacket = False
        else:
            self.requireUUIDPacket = True

    def set_listen_packets(self) -> None:
        """
        向启动器初始化监听的游戏数据包

        不应该再次调用此方法
        """
        for pktID in self.require_listen_packets:
            self.launcher.add_listen_packets(pktID)

    def add_listen_pkt(self, pkt: int) -> None:
        """添加监听的数据包

        Args:
            pkt (int): 数据包ID
        """
        self.require_listen_packets.add(pkt)

    @Utils.run_as_new_thread
    def packet_handler(self, pkt_type: int, pkt: dict) -> None:
        """数据包处理分发任务函数

        Args:
            pkt_type (int): 数据包类型
            pkt (dict): 数据包内容
        """
        is_skiped = self.linked_frame.link_plugin_group.processPacketFunc(
            pkt_type, pkt)
        if is_skiped:
            return
        if pkt_type == PacketIDS.PlayerList:
            self.process_player_list(pkt, self.linked_frame.link_plugin_group)
        elif pkt_type == PacketIDS.Text:
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
                self.say_to("@a", f"§l§7<§6§o!§r§l§7> §6此玩家名字中含特殊字符, 可能导致插件运行异常!")
                # 没有VIP名字供测试...
            if isJoining:
                Print.print_inf(f"§e{playername} 加入了游戏")
                if playername not in self.allplayers and not res:
                    self.allplayers.append(playername)
                    return
                plugin_group.execute_player_join(
                    playername, self.linked_frame.on_plugin_err
                )
            else:
                playername = next(
                    (k for k, v in self.players_uuid.items()
                     if v == player["UUID"]),
                    None,
                )
                if playername is None:
                    Print.print_war("无法获取PlayerList中玩家名字")
                    continue
                if playername != "???" and not res:
                    self.allplayers.remove(playername)
                Print.print_inf(f"§e{playername} 退出了游戏")
                plugin_group.execute_player_leave(
                    playername, self.linked_frame.on_plugin_err
                )

    def process_text_packet(self, pkt: dict, plugin_grp: "PluginGroup") -> None:
        """处理9号数据包的消息

        Args:
            pkt (dict): 数据包内容
            plugin_grp (PluginGroup): 插件组对象
        """
        match pkt["TextType"]:
            case 2:
                if pkt["Message"] == "§e%multiplayer.player.joined":
                    player = pkt["Parameters"][0]
                    plugin_grp.execute_player_prejoin(
                        player, self.linked_frame.on_plugin_err
                    )
                elif not pkt["Message"].startswith("§e%multiplayer.player.joined") and not pkt["Message"].startswith("§e%multiplayer.player.left"):
                    jon = self.Game_Data_Handle.Handle_Text_Class1(pkt)
                    Print.print_inf(("§1" + " ".join(jon)))
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
                player, msg = pkt["SourceName"], pkt["Message"]
                plugin_grp.execute_player_message(
                    player, msg, self.linked_frame.on_plugin_err
                )
                Print.print_inf(f"<{player}> {msg}")
            case 8:
                player, msg = pkt["SourceName"], pkt["Message"]
                Print.print_inf(f"{player} 使用say说: {msg.strip(f'[{player}]')}")
                plugin_grp.execute_player_message(
                    player, msg, self.linked_frame.on_plugin_err
                )
            case 9:
                msg = pkt["Message"]
                try:
                    msg_text = json.loads(msg)["rawtext"]
                    if len(msg_text) > 0 and msg_text[0].get("translate") == "***":
                        Print.print_with_info("(该tellraw内容为敏感词)", "§f 消息 ")
                        return
                    msg_text = "".join([i["text"] for i in msg_text])
                    Print.print_with_info(msg_text, "§f 消息 ")
                except Exception:
                    pass
            case 10:
                self.Game_Data_Handle.Handle_Text_Class2(pkt)

    def Inject(self) -> None:
        """载入游戏时的初始化"""
        res = self.launcher.get_players_and_uuids()
        if res:
            self.allplayers = list(res.keys())
            self.players_uuid.update(res)
        else:
            while 1:
                try:
                    cmd_result = self.sendwscmd("/list", True)
                    if cmd_result is None:
                        Print.print_err("获取全局玩家失败..重试")
                        continue
                    if cmd_result.OutputMessages is None or len(cmd_result.OutputMessages) < 2:
                        Print.print_err("获取全局玩家失败..重试")
                        continue
                    if cmd_result.OutputMessages[1].Parameters is None or len(cmd_result.OutputMessages[1].Parameters) < 1:
                        Print.print_err("获取全局玩家失败..重试")
                        continue
                    self.allplayers = (
                        cmd_result
                        .OutputMessages[1]
                        .Parameters[0]
                        .split(", ")
                    )
                    break
                except TimeoutError:
                    Print.print_war("获取全局玩家失败..重试")
        self.bot_name = self.launcher.get_bot_name()
        if self.bot_name is None:
            self.bot_name = self.allplayers[0]
        self.linked_frame.comsole_cmd_start()
        self.linked_frame.link_plugin_group.execute_init(
            self.linked_frame.on_plugin_err
        )
        Print.print_suc("初始化注入式函数init任务执行完毕")
        self.inject_welcome()

    def inject_welcome(self) -> None:
        """初始化欢迎信息"""

        if isinstance(self.bot_name, str):
            Print.print_suc(
                "初始化完成, 在线玩家: "
                + ", ".join(self.allplayers)
                + ", 机器人ID: "+self.bot_name
            )
        else:
            Print.print_suc("初始化完成, 在线玩家: " + ", ".join(self.allplayers))
            Print.print_war("未能获取机器人ID")
        self.sendcmd("/tag @s add robot")
        Print.print_suc("§f在控制台输入 §ahelp / ?§f可查看控制台命令")

    def say_to(self, target: str, msg: str) -> None:
        """向玩家发送消息

        Args:
            target (str): 玩家名/目标选择器
            msg (str): 消息
        """
        self.sendwocmd("tellraw " + target +
                       ' {"rawtext":[{"text":"' + msg + '"}]}')

    def player_title(self, target: str, text: str) -> None:
        """向玩家展示标题文本

        Args:
            target (str): 玩家名/目标选择器
            text (str): 文本
        """
        self.sendwocmd(f"title {target} title {text}")

    def player_subtitle(self, target: str, text: str) -> None:
        """向玩家展示副标题文本

        Args:
            target (str): 玩家名/目标选择器
            text (str): 文本
        """
        self.sendwocmd(f"title {target} subtitle {text}")

    def player_actionbar(self, target: str, text: str) -> None:
        """向玩家展示动作栏文本

        Args:
            target (str): 玩家名/目标选择器
            text (str): 文本
        """
        self.sendwocmd(f"title {target} actionbar {text}")

    def get_game_data(self) -> dict:
        """获取游戏数据

        Returns:
            dict: 游戏数据
        """
        return self.Game_Data
