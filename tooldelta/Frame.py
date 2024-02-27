from . import (
    builtins,
    old_dotcs_env,
    plugin_market,
    sys_args,
)
from .get_tool_delta_version import get_tool_delta_version
from .color_print import Print
from .basic_mods import (
    Callable,
    os,
    sys,
    time,
    traceback,
    requests,
    platform,
    subprocess,
    ping3,
    re,
    getpass,
    hashlib,
)
from .cfg import Cfg as _Cfg
from .launch_cli import (
    FrameFBConn,
    FrameNeOmg,
    FrameNeOmgRemote,
    SysStatus,
)
from .logger import publicLogger
from .plugin_load.PluginGroup import PluginGroup
from .urlmethod import download_file
from .sys_args import sys_args_to_dict
from typing import List, Union

# 整个系统由三个部分组成
#  Frame: 负责整个 ToolDelta 的基本框架运行
#  GameCtrl: 负责对接游戏
#    - Launchers: 负责将不同启动器的游戏接口统一成固定的接口, 供插件在多平台游戏接口运行(FastBuilder External, NeOmega, (TLSP, etc.))
#  PluginGroup: 负责管理和运行插件


PRG_NAME = "ToolDelta"
VERSION = get_tool_delta_version()
Builtins = builtins.Builtins
Config = _Cfg()


class Frame:
    # 系统框架
    class SystemVersionException(OSError):
        ...

    class FrameBasic:
        system_version = VERSION
        max_connect_fb_time = 60
        connect_fb_start_time = time.time()
        data_path = "data/"

    createThread = ClassicThread = Builtins.createThread
    PRG_NAME = PRG_NAME
    sys_data = FrameBasic()
    serverNumber: str = ""
    serverPasswd: int
    launchMode: int = 0
    consoleMenu = []
    link_game_ctrl = None
    link_plugin_group = None
    old_dotcs_threadinglist = []
    on_plugin_err = staticmethod(
        lambda name, _, err: Print.print_err(f"插件 <{name}> 出现问题: \n{err}")
    )

    @staticmethod
    def check_use_token(tok_name="", check_md=""):
        res = sys_args.sys_args_to_dict(sys.argv)
        res = res.get(tok_name, 1)
        if (res == 1 and check_md) or res != check_md:
            Print.print_err("启动参数错误")
            raise SystemExit

    def IF_Token(self):
        if not os.path.isfile("fbtoken"):
            Print.print_err(
                "请到FB官网 user.fastbuilder.pro 下载FBToken, 并放在本目录中, 或者在下面输入fbtoken"
            )
            fbtoken = input(Print.fmt_info("请输入fbtoken: ", "§b 输入 "))
            if fbtoken:
                with open("fbtoken", "w", encoding="utf-8") as f:
                    f.write(fbtoken)
            else:
                Print.print_err("未输入fbtoken, 无法继续")
                raise SystemExit

    def Login_Fc(self) -> requests.Response:
        try:
            FastBuilderApi: list = [
                "https://api.fastbuilder.pro/api/phoenix/login",
                "https://api.fastbuilder.pro/api/new",
                "https://api.fastbuilder.pro/api/api",
                "https://api.fastbuilder.pro/api/login",
                "https://api.fastbuilder.pro",
            ]
            hash_obj: hashlib._Hash = hashlib.sha256()
            username: str = input(Print.fmt_info("请输入账号:", "§6 账号 "))
            hash_obj.update(
                getpass.getpass(Print.fmt_info("请输入密码(已隐藏):", "§6 密码 ")).encode()
            )
            __password: str = hash_obj.hexdigest()
            __mfa_code: str = getpass.getpass(
                Print.fmt_info("请输入双重验证码(已隐藏)(如未设置请直接回车):", "§6 MFA  ")
            )
            Authorization: str = requests.get(url=FastBuilderApi[1], timeout=5).text
            # so?我写完你跟我说{'message': '无效用户名或一次性密码，注意: 为防止账号盗用，您不再能够使用用户中心的密码登陆 PhoenixBuilder ，请使用 FBToken 或用户中心一次性密码登陆。', 'success': False}
            # repo = requests.post(url=FastBuilderApi[0],data=json.dumps({"username":username,"password":__password,"server_code":"","server_passcode":"","client_public_key":""},ensure_ascii=False),headers={"Content-Type": "application/json","authorization": f"Bearer {Authorization}"})
            # print(json.loads((str(repo.text).strip("n"))))
            # 拜拜了您嘞,我直接用用户中心的Api去了
            repo: requests.Response = requests.post(
                url=FastBuilderApi[3],
                data=json.dumps(
                    {
                        "username": username,
                        "password": __password,
                        "mfa_code": __mfa_code,
                    },
                    ensure_ascii=False,
                ),
                headers={
                    "Content-Type": "application/json",
                    "authorization": f"Bearer {Authorization}",
                },
            )
            repo_text: dict = json.loads(repo.text)
            repo_message: str = repo_text["message"]
            repo_success: bool = repo_text["success"]
            if repo.status_code != 200:
                Print.print_war(
                    f"请求Api接口失败，将自动使用Token登陆!状态码:{repo.status_code}，返回值:{repo.text}"
                )
                self.IF_Token()
            if repo_success == False:
                if "Invalid username, password, or MFA code." in repo_message:
                    Print.print_war(f"登陆失败，无效的用户名、密码或MFA代码!")
                    self.Login_Fc()
            elif repo_success == True:
                with_perfix: dict = json.loads(
                    requests.get(
                        url=FastBuilderApi[2],
                        data=json.dumps({"with_prefix": FastBuilderApi[4]}),
                        timeout=5,
                        headers={
                            "Content-Type": "application/json",
                            "authorization": f"Bearer {Authorization}",
                        },
                    ).text
                )
                fetch_announcements: dict = json.loads(
                    requests.get(
                        url=FastBuilderApi[4] + with_perfix["fetch_announcements"],
                        timeout=5,
                        headers={
                            "Content-Type": "application/json",
                            "authorization": f"Bearer {Authorization}",
                        },
                    ).text
                )
                fetch_profile: dict = json.loads(
                    requests.get(
                        url=FastBuilderApi[4] + with_perfix["fetch_profile"],
                        timeout=5,
                        headers={
                            "Content-Type": "application/json",
                            "authorization": f"Bearer {Authorization}",
                        },
                    ).text
                )
                get_helper_status: dict = json.loads(
                    requests.get(
                        url=FastBuilderApi[4] + with_perfix["get_helper_status"],
                        timeout=5,
                        headers={
                            "Content-Type": "application/json",
                            "authorization": f"Bearer {Authorization}",
                        },
                    ).text
                )
                self.UserInfo: dict = {
                    "isadmin": repo_text["isadmin"],
                    "blc": fetch_profile["blc"],
                    "cn_username": fetch_profile["cn_username"],
                    "phoenix_otp": fetch_profile["phoenix_otp"],
                    "points": fetch_profile["points"],
                    "slots": fetch_profile["slots"],
                    "get_helper_status": get_helper_status,
                }
                self.token = requests.get(
                    url=FastBuilderApi[4] + with_perfix["get_phoenix_token"],
                    data=json.dumps({"secret": f"{Authorization}"}),
                    timeout=5,
                    headers={
                        "Content-Type": "application/json",
                        "authorization": f"Bearer {Authorization}",
                    },
                ).text
                with open("fbtoken", "w", encoding="utf-8") as f:
                    f.write(self.token)
        except Exception as err:
            Print.print_err(f"使用账号密码登陆的过程中出现异常!可能由网络环境导致! {err}")

    def Test_site_latency(self, Da: dict) -> list:
        # Da 变量数据结构
        # class Da(object):
        #     def __init__(self) -> dict:
        #         self.url: str
        #         self.mirror_url: list       (Union[list,str] <- 未采用!如只需要提交单个镜像网站需以["https://dl.mirrorurl.com"]方式传入)
        # 返回结构:{"https://dl.url1.com","https://dl.url2.com"}返回类型:list排序方式:从快到慢,所以通常使用Fastest_url:str = next(iter(Url_sor))[0]就可使用最快的链接
        tmp_speed: dict = {}
        tmp_speed[Da["url"]] = ping3.ping(
            re.search(
                r"(?<=http[s]://)[.\w-]*(:\d{,8})?((?=/)|(?!/))", Da["url"]
            ).group()
        )
        for url in Da["mirror_url"]:
            Tmp: Union[float, None] = ping3.ping(
                re.search(r"(?<=http[s]://)[.\w-]*(:\d{,8})?((?=/)|(?!/))", url).group()
            )
            tmp_speed[url] = Tmp if Tmp != None else 1024
        return sorted(tmp_speed.items(), key=lambda x: x[1])

    def auto_update(self):
        # 因行数缩减所以此函数可读性极差!
        try:
            latest_version: str = requests.get(
                "https://api.github.com/repos/ToolDelta/ToolDelta/releases/latest"
            ).json()["tag_name"]
            Version: str = f"{get_tool_delta_version()[0]}.{get_tool_delta_version()[1]}.{get_tool_delta_version()[2]}"
            if not latest_version == Version:
                if ".py" in os.path.basename(
                    __file__
                ) and ".pyc" not in os.path.basename(__file__):
                    Print.print_load(f"检测到最新版本 -> {latest_version}，请及时拉取最新版本代码!")
                    return True
                Print.print_load(f"检测到最新版本 -> {latest_version}，正在下载最新版本的ToolDelta!")
                if platform.system() == "Linux":
                    Url_sor: dict = self.Test_site_latency(
                        {
                            "url": f"https://gh.ddlc.top/https://github.com/ToolDelta/ToolDelta/releases/download/{latest_version}/ToolDelta-linux",
                            "mirror_url": [
                                f"https://mirror.ghproxy.com/https://github.com/ToolDelta/ToolDelta/releases/download/{latest_version}/ToolDelta-linux",
                                f"https://hub.gitmirror.com/https://github.com/ToolDelta/ToolDelta/releases/download/{latest_version}/ToolDelta-linux",
                            ],
                        }
                    )
                    Fastest_url: str = next(iter(Url_sor))[0]
                    URL: str = Fastest_url
                    file_path: str = os.path.join(os.getcwd(), "ToolDelta-linux_new")
                elif platform.system() == "Windows":
                    Url_sor: dict = self.Test_site_latency(
                        {
                            "url": f"https://gh.ddlc.top/https://github.com/ToolDelta/ToolDelta/releases/download/{latest_version}/ToolDelta-windows.exe",
                            "mirror_url": [
                                f"https://mirror.ghproxy.com/https://github.com/ToolDelta/ToolDelta/releases/download/{latest_version}/ToolDelta-windows.exe",
                                f"https://hub.gitmirror.com/https://github.com/ToolDelta/ToolDelta/releases/download/{latest_version}/ToolDelta-windows.exe",
                            ],
                        }
                    )
                    Fastest_url: str = next(iter(Url_sor))[0]
                    URL: str = Fastest_url
                    file_path: str = os.path.join(
                        os.getcwd(), "ToolDelta-windows_new.exe"
                    )
                download_file(URL, file_path)
                if os.path.exists(file_path):
                    try:
                        if platform.system() == "Windows":
                            for filewalks in os.walk(os.getcwd(), topdown=False):
                                for files in filewalks[2]:
                                    if (
                                        ".exe" in files
                                        and "new" not in files
                                        and "ToolDelta" in files
                                        or "tooldelta" in files
                                    ):
                                        Win_Old_ToolDelta_Path: str = os.path.join(
                                            filewalks[0], files
                                        )
                        upgrade = (
                            open("upgrade.sh", "w")
                            if platform.system() == "Linux"
                            else open("upgrade.bat", "w")
                        )
                        TempShell: str = (
                            f'#!/bin/bash\nif [ -f "{file_path}" ];then\n  sleep 3\n  rm -f {os.getcwd()}/{os.path.basename(__file__)}\n  mv {os.getcwd()}/ToolDelta-linux_new {os.getcwd()}/{os.path.basename(__file__)}\n  chmod 777 {os.path.basename(__file__)}\n  ./{os.path.basename(__file__)}\nelse\n  exit\nfi'
                            if platform.system() == "Linux"
                            else f"@echo off\ncd {os.getcwd()}\nif not exist {Win_Old_ToolDelta_Path} exit\ntimeout /T 3 /NOBREAK\ndel {Win_Old_ToolDelta_Path}\nren ToolDelta-windows_new.exe {os.path.basename(Win_Old_ToolDelta_Path)}\nstart {Win_Old_ToolDelta_Path}"
                        )
                        upgrade.write(TempShell)
                        upgrade.close()
                        if platform.system() == "Linux":
                            subprocess.Popen(
                                "sh upgrade.sh", cwd=os.getcwd(), shell=True
                            )
                        elif platform.system() == "Windows":
                            subprocess.Popen("upgrade.bat", cwd=os.getcwd(), shell=True)
                        sys.exit()
                    except Exception as err:
                        Print.print_err(f"在生成或尝试运行更新脚本时出现异常! {err}")
                        exit(1)
            else:
                Print.print_suc(f"检测成功,当前为最新版本 -> {Version}，无需更新!")
        except Exception as err:
            Print.print_war(
                f"在检测最新版本或更新ToolDelta至最新版本时出现异常，ToolDelta将会在下次启动时重新更新! {err}"
            )

    def read_cfg(self):
        # 读取启动配置等
        public_launcher: List[
            tuple[str, type[FrameFBConn | FrameNeOmg | FrameNeOmgRemote]]
        ] = [
            (
                "FastBuilder External 模式 (经典模式) §c(已停止维护, 无法适应新版本租赁服!)",
                FrameFBConn,
            ),
            ("NeOmega 框架 (NeOmega模式, 租赁服适应性强, 推荐)", FrameNeOmg),
            (
                "NeOmega 框架 (NeOmega连接模式, 需要先启动对应的neOmega接入点)",
                FrameNeOmgRemote,
            ),
        ]
        CFG: dict = {
            "服务器号": 0,
            "密码": 0,
            "启动器启动模式(请不要手动更改此项, 改为0可重置)": 0,
            "验证服务器地址(更换时记得更改fbtoken)": "https://api.fastbuilder.pro",
            "是否记录日志": True,
            "插件市场源": "https://mirror.ghproxy.com/raw.githubusercontent.com/ToolDelta/ToolDelta/main/plugin_market",
        }
        CFG_STD: dict = {
            "服务器号": int,
            "密码": int,
            "启动器启动模式(请不要手动更改此项, 改为0可重置)": Config.NNInt,
            "验证服务器地址(更换时记得更改fbtoken)": str,
            "是否记录日志": bool,
            "插件市场源": str,
        }
        if not os.path.isfile("fbtoken"):
            Print.print_inf(
                "请选择登陆方法:\n 1 - 使用账号密码(登陆成功后将自动获取Token到工作目录)\n 2 - 使用Token(如果Token文件不存在则需要输入或将文件放入工作目录)\r"
            )
            Login_method: str = input(Print.fmt_info("请输入你的选择:", "§6 输入 "))
            while True:
                if Login_method.isdigit() == False:
                    Login_method = input(Print.fmt_info("输入不合法!请输入正确的数值:", "§6 警告 "))
                elif int(Login_method) > 2 or int(Login_method) < 1:
                    Login_method = input(Print.fmt_info("输入不合法!请输入正确的数值:", "§6 警告 "))
                else:
                    break
            if Login_method == "1":
                self.Login_Fc()
            elif Login_method == "2":
                self.IF_Token()
            else:
                self.IF_Token()

        Config.default_cfg("ToolDelta基本配置.json", CFG)
        try:
            cfgs = Config.get_cfg("ToolDelta基本配置.json", CFG_STD)
            self.serverNumber = str(cfgs["服务器号"])
            self.serverPasswd = cfgs["密码"]
            self.launchMode = cfgs["启动器启动模式(请不要手动更改此项, 改为0可重置)"]
            self.plugin_market_url = cfgs["插件市场源"]
            auth_server = cfgs["验证服务器地址(更换时记得更改fbtoken)"]
            publicLogger.switch_logger(cfgs["是否记录日志"])
            if self.launchMode != 0 and self.launchMode not in range(
                1, len(public_launcher) + 1
            ):
                raise Config.ConfigError("你不该随意修改启动器模式, 现在赶紧把它改回0吧")
        except Config.ConfigError as err:
            r = self.upgrade_cfg(CFG)
            if r:
                Print.print_war("配置文件未升级, 已自动升级, 请重启 ToolDelta")
            else:
                Print.print_err(f"ToolDelta基本配置有误, 需要更正: {err}")
            raise SystemExit
        if self.serverNumber == "0":
            while 1:
                try:
                    self.serverNumber = input(Print.fmt_info("请输入租赁服号: ", "§b 输入 "))
                    self.serverPasswd = (
                        input(Print.fmt_info("请输入租赁服密码(没有请直接回车): ", "§b 输入 ")) or "0"
                    )
                    std = CFG.copy()
                    std["服务器号"] = int(self.serverNumber)
                    std["密码"] = int(self.serverPasswd)
                    Config.default_cfg("ToolDelta基本配置.json", std, True)
                    Print.print_suc("登陆配置设置成功")
                    cfgs = std
                    break
                except:
                    Print.print_err("输入有误， 租赁服号和密码应当是纯数字")
        if self.launchMode == 0:
            Print.print_inf("请选择启动器启动模式(之后可在ToolDelta启动配置更改):")
            for i, (launcher_name, _) in enumerate(public_launcher):
                Print.print_inf(f" {i + 1} - {launcher_name}")
            while 1:
                try:
                    ch = int(input(Print.fmt_info("请选择: ", "输入")))
                    if ch not in range(1, len(public_launcher) + 1):
                        raise AssertionError
                    cfgs["启动器启动模式(请不要手动更改此项, 改为0可重置)"] = ch
                    break
                except (ValueError, AssertionError):
                    Print.print_err("输入不合法, 或者是不在范围内, 请重新输入")
            Config.default_cfg("ToolDelta基本配置.json", cfgs, True)
        launcher: Callable = public_launcher[cfgs["启动器启动模式(请不要手动更改此项, 改为0可重置)"] - 1][1]
        self.fbtokenFix()
        with open("fbtoken", "r", encoding="utf-8") as f:
            fbtoken = f.read()
        self.launcher: FrameFBConn | FrameNeOmg | FrameNeOmgRemote = launcher(
            self.serverNumber, self.serverPasswd, fbtoken, auth_server
        )

    @staticmethod
    def upgrade_cfg(cfg_std):
        # 升级本地的配置文件
        old_cfg = Config.get_cfg("ToolDelta基本配置.json", {})
        old_cfg_keys = old_cfg.keys()
        need_upgrade_cfg = False
        if "验证服务器地址(更换时记得更改fbtoken)" not in old_cfg_keys:
            old_cfg["验证服务器地址(更换时记得更改fbtoken)"] = "https://api.fastbuilder.pro"
            need_upgrade_cfg = True
        if "是否记录日志" not in old_cfg_keys:
            old_cfg["是否记录日志"] = False
            need_upgrade_cfg = True
        if "插件市场源" not in old_cfg_keys:
            old_cfg["插件市场源"] = cfg_std["插件市场源"]
            need_upgrade_cfg = True
        if need_upgrade_cfg:
            Config.default_cfg("ToolDelta基本配置.json", old_cfg, True)
        return need_upgrade_cfg

    @staticmethod
    def welcome():
        # 欢迎提示
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
    def plugin_load_finished(plugins: PluginGroup):
        # 插件成功载入提示
        Print.print_suc(
            f"成功载入 §f{plugins.normal_plugin_loaded_num}§a 个组合式插件, §f{plugins.injected_plugin_loaded_num}§a 个注入式插件, §f{plugins.dotcs_plugin_loaded_num}§a 个DotCS插件"
        )

    @staticmethod
    def basic_operation():
        # 初始化文件夹
        os.makedirs("插件文件/原DotCS插件", exist_ok=True)
        os.makedirs("插件文件/ToolDelta注入式插件", exist_ok=True)
        os.makedirs("插件文件/ToolDelta组合式插件", exist_ok=True)
        os.makedirs("插件配置文件", exist_ok=True)
        os.makedirs("tooldelta/fb_conn", exist_ok=True)
        os.makedirs("tooldelta/neo_libs", exist_ok=True)
        os.makedirs("status", exist_ok=True)
        os.makedirs("data/status", exist_ok=True)
        os.makedirs("data/players", exist_ok=True)

    @staticmethod
    def fbtokenFix():
        # 对异常FbToken的自动修复
        with open("fbtoken", "r", encoding="utf-8") as f:
            token = f.read()
            if "\n" in token:
                Print.print_war("fbtoken里有换行符， 会造成fb登陆失败， 已自动修复")
                with open("fbtoken", "w", encoding="utf-8") as f:
                    f.write(token.replace("\n", ""))

    def add_console_cmd_trigger(
        self,
        triggers: list[str],
        arg_hint: str | None,
        usage: str,
        func: Callable[[list[str]], None],
    ):
        """
        注册ToolDelta控制台的菜单项

        参数:
            triggers: 触发词列表
            arg_hint: 菜单命令参数提示句
            usage: 命令说明
            func: 菜单回调方法 (list[str])
        """
        try:
            if self.consoleMenu.index(triggers) != -1:
                Print.print_war(f"§6后台指令关键词冲突: {func}, 不予添加至指令菜单")
        except:
            self.consoleMenu.append([usage, arg_hint, func, triggers])

    def init_basic_help_menu(self, _):
        menu = self.get_console_menus()
        Print.print_inf("§a以下是可选的菜单指令项: ")
        for usage, arg_hint, _, triggers in menu:
            if arg_hint:
                Print.print_inf(f" §e{' 或 '.join(triggers)} {arg_hint}  §f->  {usage}")
            else:
                Print.print_inf(f" §e{' 或 '.join(triggers)}  §f->  {usage}")

    def comsole_cmd_start(self):
        def _try_execute_console_cmd(func, rsp, mode, arg1):
            try:
                if mode == 0:
                    rsp_arg = rsp.split()[1:]
                elif mode == 1:
                    rsp_arg = rsp[len(arg1) :].split()
            except IndexError:
                Print.print_err("[控制台执行命令] 指令缺少参数")
                return
            try:
                return func(rsp_arg) or 0
            except:
                Print.print_err(f"控制台指令出错： {traceback.format_exc()}")
                return 0

        def _console_cmd_thread():
            self.add_console_cmd_trigger(
                ["?", "help", "帮助"],
                None,
                "查询可用菜单指令",
                self.init_basic_help_menu,
            )
            self.add_console_cmd_trigger(
                ["exit"], None, f"退出并关闭{PRG_NAME}", lambda _: self.system_exit()
            )
            self.add_console_cmd_trigger(
                ["插件市场"],
                None,
                "进入插件市场",
                lambda _: plugin_market.market.enter_plugin_market(
                    self.plugin_market_url
                ),
            )
            try:
                while 1:
                    rsp = input()
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
                                    res = _try_execute_console_cmd(func, rsp, 1, tri)
                                    if res == -1:
                                        return
            except (EOFError, KeyboardInterrupt):
                Print.print_inf("使用 Ctrl+C 退出中...")
                self.system_exit()

        self.createThread(_console_cmd_thread, usage="控制台指令")

    def system_exit(self):
        exit_status_code = getattr(self.launcher, "secret_exit_key", "null")
        if self.link_game_ctrl.allplayers and not isinstance(
            self.launcher, (FrameNeOmgRemote,)
        ):
            try:
                self.link_game_ctrl.sendwscmd(
                    f"/kick {self.link_game_ctrl.bot_name} ToolDelta 退出中(看到这条消息请重新加入游戏)\nSTATUS CODE: {exit_status_code}"
                )
            except:
                pass
        time.sleep(0.5)
        self.launcher.status = SysStatus.NORMAL_EXIT
        self.launcher.exit_event.set()
        return -1

    def _get_old_dotcs_env(self):
        # 获取 dotcs 的插件环境
        return old_dotcs_env.get_dotcs_env(self, Print)

    def get_console_menus(self):
        # 获取所有控制台命令菜单
        return self.consoleMenu

    def set_game_control(self, game_ctrl):
        "使用外源GameControl..."
        self.link_game_ctrl: GameCtrl = game_ctrl

    def set_plugin_group(self, plug_grp):
        "使用外源PluginGroup..."
        self.link_plugin_group: PluginGroup = plug_grp

    def get_game_control(self):
        gcl: GameCtrl = self.link_game_ctrl
        return gcl

    @staticmethod
    def safe_close():
        builtins.safe_close()
        publicLogger.exit()
        Print.print_inf("已保存数据与日志等信息.")


sys_args_dict = sys_args_to_dict(sys.argv)
createThread = Builtins.createThread

from .builtins import Builtins
from .basic_mods import asyncio, datetime, json
from .packets import PacketIDS
from .plugin_load.injected_plugin import (
    execute_death_message,
    execute_init,
    execute_player_join,
    execute_player_left,
    execute_player_message,
    execute_repeat,
)


class GameCtrl:
    # 游戏连接和交互部分
    def __init__(self, frame: Frame):
        self.linked_frame = frame
        self.players_uuid = {}
        self.allplayers = []
        self.bot_name = ""
        self.linked_frame: Frame
        self.pkt_unique_id: int = 0
        self.pkt_cache: list = []
        self.require_listen_packets = {9, 79, 63}
        self.store_uuid_pkt: dict[str, str] | None = None

    def init_funcs(self):
        self.launcher = self.linked_frame.launcher
        self.launcher.packet_handler = lambda pckType, pck: createThread(
            self.packet_handler, (pckType, pck)
        )
        self.sendcmd = self.launcher.sendcmd
        self.sendwscmd = self.launcher.sendwscmd
        self.sendwocmd = self.launcher.sendwocmd
        self.sendPacket = self.launcher.sendPacket
        self.sendfbcmd = self.launcher.sendfbcmd
        if isinstance(self.linked_frame.launcher, FrameNeOmg):
            self.requireUUIDPacket = False
        else:
            self.requireUUIDPacket = True

    def set_listen_packets(self):
        # 向启动器初始化监听的游戏数据包
        # 不应该再次调用此方法
        for pktID in self.require_listen_packets:
            self.launcher.add_listen_packets(pktID)

    def add_listen_pkt(self, pkt: int):
        self.require_listen_packets.add(pkt)

    @Builtins.run_as_new_thread
    def packet_handler(self, pkt_type: int, pkt: dict):
        if pkt_type == PacketIDS.PlayerList:
            self.process_player_list(pkt, self.linked_frame.link_plugin_group)
        elif pkt_type == PacketIDS.Text:
            self.process_text_packet(pkt, self.linked_frame.link_plugin_group)
        self.linked_frame.linked_plugin_group.processPacketFunc(pkt_type, pkt)

    def process_player_list(self, pkt, plugin_group: PluginGroup):
        # 处理玩家进出事件
        for player in pkt["Entries"]:
            isJoining = bool(player["Skin"]["SkinData"])
            playername = player["Username"]
            if isJoining:
                self.players_uuid[playername] = player["UUID"]
                (
                    self.allplayers.append(playername)
                    if playername not in self.allplayers
                    else None
                )
                if not self.requireUUIDPacket:
                    Print.print_inf(f"§e{playername} 加入了游戏, UUID: {player['UUID']}")
                    asyncio.run(execute_player_join(playername))
                    plugin_group.execute_player_join(
                        playername, self.linked_frame.on_plugin_err
                    )
                else:
                    self.bot_name = pkt["Entries"][0]["Username"]
                    self.requireUUIDPacket = False
            else:
                for k in self.players_uuid:
                    if self.players_uuid[k] == player["UUID"]:
                        playername = k
                        break
                else:
                    Print.print_war("无法获取PlayerList中玩家名字")
                    continue
                self.allplayers.remove(playername) if playername != "???" else None
                Print.print_inf(f"§e{playername} 退出了游戏")
                asyncio.run(execute_player_left(playername))
                plugin_group.execute_player_leave(
                    playername, self.linked_frame.on_plugin_err
                )

    def process_text_packet(self, pkt: dict, plugin_grp: PluginGroup):
        # 处理9号数据包的消息, 因特殊原因将一些插件事件放到此处理
        match pkt["TextType"]:
            case 2:
                if pkt["Message"] == "§e%multiplayer.player.joined":
                    player = pkt["Parameters"][0]
                    plugin_grp.execute_player_prejoin(
                        player, self.linked_frame.on_plugin_err
                    )
                if pkt["Message"] == "§e%multiplayer.player.join":
                    player = pkt["Parameters"][0]
                elif pkt["Message"] == "§e%multiplayer.player.left":
                    player = pkt["Parameters"][0]
                elif pkt["Message"].startswith("death."):
                    Print.print_inf(f"{pkt['Parameters'][0]} 失败了: {pkt['Message']}")
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
                    asyncio.run(execute_death_message(pkt["Parameters"][0], killer))
            case 1 | 7:
                player, msg = pkt["SourceName"], pkt["Message"]
                asyncio.run(execute_player_message(player, msg))
                plugin_grp.execute_player_message(
                    player, msg, self.linked_frame.on_plugin_err
                )

                Print.print_inf(f"<{player}> {msg}")
            case 8:
                player, msg = pkt["SourceName"], pkt["Message"]
                Print.print_inf(f"{player} 使用say说: {msg.strip(f'[{player}]')}")
                asyncio.run(execute_player_message(player, msg))
                plugin_grp.execute_player_message(
                    player, msg, self.linked_frame.on_plugin_err
                )
            case 9:
                msg = pkt["Message"]
                try:
                    Print.print_inf(
                        "".join([i["text"] for i in json.loads(msg)["rawtext"]])
                    )
                except:
                    pass

    def Inject(self):
        # 载入游戏时的初始化
        res = self.launcher.get_players_and_uuids()
        if res:
            self.allplayers = list(res.keys())
            self.players_uuid.update(res)
        else:
            while 1:
                try:
                    self.allplayers = (
                        self.sendwscmd("/testfor @a", True)
                        .OutputMessages[0]
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
        Builtins.createThread(asyncio.run, (execute_repeat(),))
        Print.print_inf("正在执行初始化注入式函数init任务")
        asyncio.run(execute_init())
        Print.print_suc("初始化注入式函数init任务执行完毕")
        self.inject_welcome()

    def inject_welcome(self):
        # 载入游戏后的欢迎提示语
        Print.print_suc(
            "初始化完成, 在线玩家: " + ", ".join(self.allplayers) + ", 机器人ID: " + self.bot_name
        )
        time.sleep(0.5)
        self.say_to("@a", "§l§7[§f!§7] §r§fToolDelta Enabled!")
        self.say_to(
            "@a",
            "§l§7[§f!§7] §r§f北京时间 " + datetime.datetime.now().strftime("§a%H§f : §a%M"),
        )
        self.say_to("@a", "§l§7[§f!§7] §r§f输入.help获取更多帮助哦")
        self.sendcmd("/tag @s add robot")
        Print.print_suc("§f在控制台输入 §ahelp / ?§f可查看控制台命令")

    def say_to(self, target: str, msg: str):
        """
        向玩家发送聊天栏信息

        参数:
            target: 玩家名/目标选择器
            msg: 信息
        """
        self.sendwocmd("tellraw " + target + ' {"rawtext":[{"text":"' + msg + '"}]}')

    def player_title(self, target: str, text: str):
        """
        向玩家展示大标题文本

        参数:
            target: 玩家名/目标选择器
            text: 文本
        """
        self.sendwocmd(f"title {target} title {text}")

    def player_subtitle(self, target: str, text: str):
        """
        向玩家展示小标题文本

        参数:
            target: 玩家名/目标选择器
            text: 文本
        """
        self.sendwocmd(f"title {target} subtitle {text}")

    def player_actionbar(self, target: str, text: str):
        """
        向玩家展示行动栏文本

        参数:
            target: 玩家名/目标选择器
            text: 文本
        """
        self.sendwocmd(f"title {target} actionbar {text}")
