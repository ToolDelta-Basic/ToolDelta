from typing import Callable, Type, Any
import os, sys, traceback, zipfile, time, threading, re, importlib
from .color_print import Print
from .cfg import Cfg
from .builtins import Builtins

try:
    # you'd like to delete this block
    plugin_dec = importlib.__import__(".pluginDec")
    decPluginAndCMP = plugin_dec
except:
    decPluginAndCMP = None


class PluginSkip(EOFError):
    ...


NON_FUNC = lambda *_: None
NOT_IMPORTALL_RULE = re.compile(r"from .* import \*")


def unzip_plugin(zip_dir, exp_dir):
    try:
        f = zipfile.ZipFile(zip_dir, "r")
        f.extractall(exp_dir)
    except Exception as err:
        Print.print_err(f"zipfile: 解压失败: {err}")
        print(traceback.format_exc())
        os._exit(0)


def _import_original_dotcs_plugin(
    plugin_code: str, old_dotcs_env: dict, module_env: dict, plugin_group
):
    # dotcs插件太不规范了!!
    plugin_body = Plugin()
    plugin_body.dotcs_old_type = True
    old_dotcs_env.update(module_env)
    runcode_tmp = {}
    plugin_code_lines = plugin_code.split("\n")
    _dotcs_runcode = {}
    evts = {}
    packetFuncs = []
    while 1:
        if "" in plugin_code_lines:
            plugin_code_lines.remove("")
        else:
            break
    plugin_start = -1
    plugin_end = 0
    plugin_prev_type = ""

    for line in range(len(plugin_code_lines)):
        if "import *" in plugin_code_lines[line]:
            Print.print_war(
                f"DotCS插件 存在异常的代码 'import *', 已自动替换为 pass: §7{line} §f|{plugin_code_lines[line]}"
            )
            plugin_code_lines[line] = NOT_IMPORTALL_RULE.sub(
                "pass", plugin_code_lines[line]
            )
        if plugin_code_lines[line].startswith("# PLUGIN TYPE: "):
            if plugin_start + 1:
                plugin_end = line
                runcode_tmp[plugin_prev_type] = "\n".join(
                    plugin_code_lines[plugin_start:plugin_end]
                )
            plugin_start = line + 1
            plugin_prev_type = plugin_code_lines[line].strip("# PLUGIN TYPE: ")
    if plugin_start + 1:
        plugin_end = len(plugin_code_lines)
        runcode_tmp[plugin_prev_type] = "\n".join(
            plugin_code_lines[plugin_start:plugin_end]
        )

    old_dotcs_env.update({"plugin_group": plugin_group})
    fun_exec_code = ""
    for k in runcode_tmp:
        match k:
            case "def":
                fun_exec_code = "def on_def():\n "
            case "init":
                fun_exec_code = "def on_inject():\n "
            case "player prejoin":
                fun_exec_code = "def on_player_prejoin(playername):\n "
            case "player join":
                fun_exec_code = "def on_player_join(playername):\n "
            case "player message":
                fun_exec_code = "def on_player_message(playername, msg):\n "
            case "player leave":
                fun_exec_code = "def on_player_leave(playername):\n "
            case "player death":
                fun_exec_code = "def on_player_death(playername, killer, msg):\n "
            case "repeat 1s":
                fun_exec_code = "def repeat1s():\n "
            case "repeat 10s":
                fun_exec_code = "def repeat10s():\n "
            case "repeat 30s":
                fun_exec_code = "def repeat30s():\n "
            case "repeat 1m":
                fun_exec_code = "def repeat1m():\n "
            case _:
                if k.startswith("packet"):
                    try:
                        pktID = int(k.split()[1])
                        if pktID == -1:
                            Print.print_war(f"§c无法监听任意数据包, 已跳过")
                        else:
                            fun_exec_code = (
                                f"def packet_{pktID}(jsonPkt):\n packetType={pktID}\n "
                            )
                            plugin_body._add_req_listen_packet(pktID)
                            packetFuncs.append((pktID, f"packet_{pktID}"))
                    except:
                        Print.print_war(f"§c不合法的监听数据包ID： {k}, 已跳过")
                else:
                    raise Exception(f"无法识别的DotCS插件事件样式： {k}")
        # DotCS 有太多的插件都会出现作用域问题, 在此只能这么修复了
        p_code = (
            fun_exec_code
            + """globals().update(plugin_group.dotcs_global_vars)\n """
            + runcode_tmp[k].replace("\n", "\n ")
            + "\n plugin_group.dotcs_global_vars.update(locals())"
        )
        try:
            exec(p_code, old_dotcs_env, _dotcs_runcode)
        except Exception as err:
            Print.print_err(f"DotCS插件 <{plugin_body.name}> 出错: {err}")
            raise
    newPacketFuncs = []
    for pkt, funcname in packetFuncs:
        newPacketFuncs.append((pkt, _dotcs_runcode[funcname]))
    for codetype in [
        "on_def",
        "on_inject",
        "on_player_prejoin",
        "on_player_join",
        "on_player_message",
        "on_player_death",
        "on_player_leave",
    ]:
        if _dotcs_runcode.get(codetype, None):
            evts[codetype] = [plugin_body.name, _dotcs_runcode[codetype]]
        if _dotcs_runcode.get(f"repeat1s", None):
            evts["repeat1s"] = [plugin_body.name, _dotcs_runcode[f"repeat1s"]]
        if _dotcs_runcode.get(f"repeat10s", None):
            evts["repeat10s"] = [plugin_body.name, _dotcs_runcode[f"repeat10s"]]
        if _dotcs_runcode.get(f"repeat30s", None):
            evts["repeat30s"] = [plugin_body.name, _dotcs_runcode[f"repeat30s"]]
        if _dotcs_runcode.get(f"repeat1m", None):
            evts["repeat1m"] = [plugin_body.name, _dotcs_runcode[f"repeat1m"]]
    return plugin_body, evts, newPacketFuncs


class Plugin:
    name = "<未命名插件>"
    version = (0, 0, 1)
    author = "?"

    def __init__(self):
        self.require_listen_packets = []
        self.dotcs_old_type = False

    def _add_req_listen_packet(self, pktID):
        if not pktID in self.require_listen_packets:
            self.require_listen_packets.append(pktID)


class PluginAPI:
    name = "<未命名插件api>"
    version = (0, 0, 1)

    def __init__(self, _):
        raise Exception("需要初始化__init__方法")


class PluginGroup:
    class PluginAPINotFoundError(ModuleNotFoundError):
        def __init__(self, name):
            self.name = name

    class PluginAPIVersionError(ModuleNotFoundError):
        def __init__(self, name, m_ver, n_ver):
            self.name = name
            self.m_ver = m_ver
            self.n_ver = n_ver

    plugins: list[Plugin] = []
    plugins_funcs: dict[str, list] = {
        "on_def": [],
        "on_inject": [],
        "on_player_prejoin": [],
        "on_player_join": [],
        "on_player_message": [],
        "on_player_death": [],
        "on_player_leave": [],
    }
    plugin_added_cache = {"plugin": None, "packets": []}
    pluginAPI_added_cache = []

    def __init__(self, frame, PRG_NAME):
        self.listen_packet_ids = set()
        self.old_dotcs_env = {}
        self.dotcs_global_vars = {}
        self.packet_funcs: dict[str, list[Callable]] = {}
        self.plugins_api: dict[str, PluginAPI] = {}
        self.excType = 0
        self.PRG_NAME = ""
        self._broadcast_evts = {}
        self.dotcs_plugin_loaded_num = 0
        self.normal_plugin_loaded_num = 0
        self.linked_frame = frame
        self.PRG_NAME = PRG_NAME
        self._dotcs_repeat_threadings = {"1s": [], "10s": [], "30s": [], "1m": []}
        self.linked_frame.linked_plugin_group = self

    def add_broadcast_listener(self, evt_name: str):
        "将下面的方法作为一个广播事件接收器"

        def deco(func: Callable[[Any], bool]):
            if self._broadcast_evts.get(evt_name, None):
                self._broadcast_evts[evt_name].append(func)
            else:
                self._broadcast_evts[evt_name] = [func]

        return deco

    def broadcastEvt(self, evt_name: str, **kwargs) -> list[Any] | None:
        "向全局广播一个特定事件, 可以传入附加信息参数"
        callback_list = []
        res = self._broadcast_evts.get(evt_name, None)
        if res:
            for f in res:
                interrupt, *res2 = f(**kwargs)
                if res2:
                    callback_list.append(res2)
                    if interrupt:
                        break
            return callback_list
        else:
            return None

    def add_plugin(self, plugin):
        assert Plugin.__subclasscheck__(plugin), (1, "插件主类必须继承Plugin类")
        self.plugin_added_cache["plugin"] = plugin
        return plugin

    def add_packet_listener(self, pktID):
        def decorator(func):
            self.plugin_added_cache["packets"].append((pktID, func))
            return func

        return decorator

    def add_plugin_api(self, apiName: str):
        def _add_api(api: Type[PluginAPI]):
            assert PluginAPI.__subclasscheck__(api), (1, "插件API类必须继承PluginAPI类")
            self.pluginAPI_added_cache.append((apiName, api))

        return _add_api

    def add_plugin_as_api(self, apiName: str):
        def _add_plugin_2_api(api_plugin: Type[PluginAPI]):
            assert PluginAPI.__subclasscheck__(api_plugin), (
                1,
                "API插件API类必须继承PluginAPI类和Plugin类",
            )
            self.plugin_added_cache["plugin"] = api_plugin
            self.pluginAPI_added_cache.append(apiName)

        return _add_plugin_2_api

    def get_plugin_api(self, apiName: str, min_version: tuple | None = None):
        api = self.plugins_api.get(apiName, None)
        if api:
            if min_version and api.version < min_version:
                raise self.PluginAPIVersionError(apiName, min_version, api.version)
            return api
        else:
            raise self.PluginAPINotFoundError(apiName)

    def checkSystemVersion(self, need_vers: tuple[int, int, int]):
        if need_vers > self.linked_frame.sys_data.system_version:
            raise self.linked_frame.SystemVersionException(
                f"该组件需要{self.linked_frame.PRG_NAME}为{'.'.join([str(i) for i in self.linked_frame.sys_data.system_version])}版本"
            )

    def read_plugin_from_old(self, module_env: dict):
        sys.path.append(os.getcwd() + "/DotCS兼容插件")
        dotcs_env = self.linked_frame._get_old_dotcs_env()
        files = os.listdir("DotCS兼容插件")
        files.sort()
        for file in files:
            try:
                if file.endswith(".py"):
                    Print.print_inf(f"§6载入DotCS插件: {file.strip('.py')}", end="\r")
                    with open("DotCS兼容插件/" + file, "r", encoding="utf-8") as f:
                        code = f.read()
                    plugin, evts, pkfuncs = _import_original_dotcs_plugin(
                        code, dotcs_env, module_env, self
                    )
                    plugin.name = file.strip(".py")
                    if (
                        "repeat10s" in evts.keys()
                        or "repeat1s" in evts.keys()
                        or "repeat30s" in evts.keys()
                        or "repeat1m" in evts.keys()
                    ):
                        evtnew = evts.copy()
                        for i in evtnew.keys():
                            if i.startswith("repeat"):
                                del evts[i]
                                self._dotcs_repeat_threadings[i.strip("repeat")].append(
                                    evtnew[i]
                                )
                    for pkt, func in pkfuncs:
                        self.__add_listen_packet_id(pkt)
                        self.__add_listen_packet_func(pkt, func)
                        Print.print_suc(
                            f"[DotCS插件 特殊数据包监听] 添加成功: {plugin.name} <- {func.__name__}"
                        )
                    for k, v in evts.items():
                        self.plugins_funcs[k].append(v)
                    self.__add_plugin(plugin)
                    self.dotcs_plugin_loaded_num += 1
                    Print.print_suc(f"§a成功载入插件 §2<DotCS> §a{plugin.name}")
            except Exception as err:
                try:
                    plugin_name = plugin.name  # type: ignore
                except:
                    plugin_name = file
                Print.print_err(f"§c加载插件 {plugin_name} 出现问题: {err}")
                raise

    def read_plugin_from_new(self, root_env: dict):
        for plugin_dir in os.listdir(f"{self.PRG_NAME}插件"):
            if (
                not os.path.isdir(f"{self.PRG_NAME}插件/" + plugin_dir.strip(".zip"))
                and os.path.isfile(f"{self.PRG_NAME}插件/" + plugin_dir)
                and plugin_dir.endswith(".zip")
            ):
                Print.print_with_info(f"§6正在解压插件{plugin_dir}, 请稍后", "§6 解压 ")
                unzip_plugin(
                    f"{self.PRG_NAME}插件/" + plugin_dir,
                    f"{self.PRG_NAME}插件/" + plugin_dir.strip(".zip"),
                )
                Print.print_suc(f"§a成功解压插件{plugin_dir} -> 插件目录")
                plugin_dir = plugin_dir.strip(".zip")
            if os.path.isdir(f"{self.PRG_NAME}插件/" + plugin_dir):
                sys.path.append(os.getcwd() + f"/{self.PRG_NAME}插件/" + plugin_dir)
                self.plugin_added_cache["plugin"] = None
                self.plugin_added_cache["packets"].clear()
                self.pluginAPI_added_cache.clear()
                try:
                    if os.path.isfile(
                        f"{self.PRG_NAME}插件/" + plugin_dir + "/__init__.py"
                    ):
                        with open(
                            f"{self.PRG_NAME}插件/" + plugin_dir + "/__init__.py",
                            "r",
                            encoding="utf-8",
                        ) as f:
                            code = f.read()
                        exec(code, root_env)
                        # 理论上所有插件共享一个整体环境
                    elif os.path.isfile(
                        f"{self.PRG_NAME}插件/" + plugin_dir + "/__MAIN__.tdenc"
                    ):
                        if decPluginAndCMP is not None:
                            with open(
                                f"{self.PRG_NAME}插件/" + plugin_dir + "/__MAIN__.tdenc",
                                "rb",
                            ) as f:
                                compiled_pcode = decPluginAndCMP(f.read())
                                if (compiled_pcode == 0) | (compiled_pcode == 1):
                                    raise AssertionError(3, compiled_pcode)
                                if not isinstance(compiled_pcode, int):
                                    exec(compiled_pcode, root_env)
                        else:
                            Print.print_err(f"该条件下无法加载加密插件{plugin_dir}, 跳过加载")
                            continue
                    else:
                        Print.print_war(f"{plugin_dir} 文件夹 未发现插件文件, 跳过加载")
                        continue
                    assert self.plugin_added_cache["plugin"] is not None, 2
                    plugin = self.plugin_added_cache["plugin"]
                    plugin_body: Plugin = plugin(self.linked_frame)
                    self.plugins.append([plugin_body.name, plugin_body])
                    _v0, _v1, _v2 = plugin_body.version  # type: ignore
                    if hasattr(plugin_body, "on_def"):
                        self.plugins_funcs["on_def"].append(
                            [plugin_body.name, plugin_body.on_def]
                        )
                    if hasattr(plugin_body, "on_inject"):
                        self.plugins_funcs["on_inject"].append(
                            [plugin_body.name, plugin_body.on_inject]
                        )
                    if hasattr(plugin_body, "on_player_prejoin"):
                        self.plugins_funcs["on_player_prejoin"].append(
                            [plugin_body.name, plugin_body.on_player_prejoin]
                        )
                    if hasattr(plugin_body, "on_player_join"):
                        self.plugins_funcs["on_player_join"].append(
                            [plugin_body.name, plugin_body.on_player_join]
                        )
                    if hasattr(plugin_body, "on_player_message"):
                        self.plugins_funcs["on_player_message"].append(
                            [plugin_body.name, plugin_body.on_player_message]
                        )
                    if hasattr(plugin_body, "on_player_death"):
                        self.plugins_funcs["on_player_death"].append(
                            [plugin_body.name, plugin_body.on_player_death]
                        )
                    if hasattr(plugin_body, "on_player_leave"):
                        self.plugins_funcs["on_player_leave"].append(
                            [plugin_body.name, plugin_body.on_player_leave]
                        )
                    Print.print_suc(
                        f"成功载入插件 {plugin_body.name} 版本: {_v0}.{_v1}.{_v2}  作者：{plugin_body.author}"
                    )
                    self.normal_plugin_loaded_num += 1
                    if self.plugin_added_cache["packets"] != []:
                        for pktType, func in self.plugin_added_cache["packets"]:  # type: ignore
                            self.__add_listen_packet_id(pktType)
                            self.__add_listen_packet_func(
                                pktType, getattr(plugin_body, func.__name__)
                            )
                    if self.pluginAPI_added_cache is not None:
                        for _api in self.pluginAPI_added_cache:
                            if isinstance(_api, str):
                                self.plugins_api[_api] = plugin_body
                            else:
                                (apiName, api) = _api
                                self.plugins_api[apiName] = api(self.linked_frame)
                except AssertionError as err:
                    if err.args[0] == 2:
                        Print.print_err(
                            f"插件 {plugin_dir} 不合法: 只能调用一次 @plugins.add_plugin, 实际调用了0次或多次"
                        )
                        raise SystemExit
                    elif err.args[0] == 3:
                        Print.print_err(f"加密插件: {plugin_dir} 加载失败 ERR={err.args[1]}")
                        raise SystemExit
                    if len(err.args[0]) == 2:
                        Print.print_err(f"插件 {plugin_dir} 不合法: {err.args[0][1]}")
                        raise SystemExit
                    else:
                        raise
                except Cfg.ConfigError as err:
                    Print.print_err(f"插件 {plugin_dir} 配置文件报错：{err}")
                    Print.print_err(f"你也可以直接删除配置文件, 重新启动ToolDelta以自动生成配置文件")
                    raise SystemExit
                except Builtins.SimpleJsonDataReader.DataReadError as err:
                    Print.print_err(f"插件 {plugin_dir} 读取数据失败: {err}")
                except self.linked_frame.SystemVersionException:
                    Print.print_err(f"插件 {plugin_dir} 需要更高版本的ToolDelta加载: {err}")
                except Exception as err:
                    if "() takes no arguments" in str(err):
                        Print.print_err(f"插件 {plugin_dir} 不合法： 主类初始化时应接受 1 个参数: Frame")
                    else:
                        Print.print_err(f"加载插件 {plugin_dir} 出现问题, 报错如下: ")
                        Print.print_err("§c" + traceback.format_exc())
                        raise SystemExit

    def read_plugin_from_nonop(self, root_env: dict):
        for plugin_dir in os.listdir(f"{self.PRG_NAME}无OP运行插件"):
            if os.path.isdir(f"{self.PRG_NAME}运行插件/" + plugin_dir):
                Print.print_inf(f"§6加载无OP运行插件: {plugin_dir}")
                with open(
                    f"{self.PRG_NAME}无OP运行插件/" + plugin_dir + "/__init__.py",
                    "r",
                    encoding="utf-8",
                ) as f:
                    code = f.read()
                    # This function should only be avaliable on ToolDelta Advanced Version.

    def __add_plugin(self, plugin: Plugin):
        self.plugins.append(plugin)

    def __add_listen_packet_id(self, packetType: int):
        self.listen_packet_ids.add(packetType)
        self.linked_frame.link_game_ctrl.add_listen_pkt(packetType)

    def __add_listen_packet_func(self, packetType, func: Callable):
        if self.packet_funcs.get(str(packetType), None):
            self.packet_funcs[str(packetType)].append(func)
        else:
            self.packet_funcs[str(packetType)] = [func]

    def execute_dotcs_repeat(self, on_plugin_err):
        "启动dotcs插件的循环执行模式插件事件"
        threading.Thread(target=self.run_dotcs_repeat_funcs).start()

    def run_dotcs_repeat_funcs(self):
        lastTime10s = 0
        lastTime30s = 0
        lastTime1m = 0
        if not any(self._dotcs_repeat_threadings.values()):
            return
        Print.print_inf(
            f"开始运行 {sum([len(funcs) for funcs in self._dotcs_repeat_threadings.values()])} 个原dotcs计划任务方法"
        )
        while 1:
            time.sleep(1)
            nowTime = time.time()
            if nowTime - lastTime1m > 60:
                for fname, func in self._dotcs_repeat_threadings["1m"]:
                    try:
                        # A strong desire to remove "try" block !!
                        func()
                    except Exception as err:
                        Print.print_err(f"原dotcs插件 <{fname}> (计划任务1min)报错: {err}")
                lastTime1m = nowTime
            if nowTime - lastTime30s > 30:
                for fname, func in self._dotcs_repeat_threadings["30s"]:
                    try:
                        func()
                    except Exception as err:
                        Print.print_err(f"原dotcs插件 <{fname}> (计划任务30s)报错: {err}")
                lastTime30s = nowTime
            if nowTime - lastTime10s > 10:
                for fname, func in self._dotcs_repeat_threadings["10s"]:
                    try:
                        func()
                    except Exception as err:
                        Print.print_err(f"原dotcs插件 <{fname}> (计划任务10s)报错: {err}")
                lastTime10s = nowTime
            for fname, func in self._dotcs_repeat_threadings["1s"]:
                try:
                    func()
                except Exception as err:
                    Print.print_err(f"原dotcs插件 <{fname}> (计划任务1s) 报错: {err}")

    def execute_def(self, onerr: Callable[[str, Exception, str], None] = NON_FUNC):
        for name, func in self.plugins_funcs["on_def"]:
            try:
                func()
            except PluginGroup.PluginAPINotFoundError as err:
                Print.print_err(f"插件 {name} 需要包含该种接口的前置组件: {err.name}")
                raise SystemExit
            except PluginGroup.PluginAPIVersionError as err:
                Print.print_err(
                    f"插件 {name} 需要该前置组件 {err.name} 版本: {err.m_ver}, 但是现有版本过低: {err.n_ver}"
                )
                raise SystemExit
            except Exception as err:
                onerr(name, err, traceback.format_exc())

    def execute_init(self, onerr: Callable[[str, Exception, str], None] = NON_FUNC):
        for name, func in self.plugins_funcs["on_inject"]:
            try:
                func()
            except Exception as err:
                onerr(name, err, traceback.format_exc())

    def execute_player_prejoin(
        self, player, onerr: Callable[[str, Exception, str], None] = NON_FUNC
    ):
        for name, func in self.plugins_funcs["on_player_prejoin"]:
            try:
                func(player)
            except Exception as err:
                onerr(name, err, traceback.format_exc())

    def execute_player_join(
        self, player, onerr: Callable[[str, Exception, str], None] = NON_FUNC
    ):
        for name, func in self.plugins_funcs["on_player_join"]:
            try:
                func(player)
            except Exception as err:
                onerr(name, err, traceback.format_exc())

    def execute_player_message(
        self, player, msg, onerr: Callable[[str, Exception, str], None] = NON_FUNC
    ):
        pat = f"[{player}] "
        if msg.startswith(pat):
            msg = msg.strip(pat)
        for name, func in self.plugins_funcs["on_player_message"]:
            try:
                func(player, msg)
            except Exception as err:
                onerr(name, err, traceback.format_exc())

    def execute_player_leave(
        self, player, onerr: Callable[[str, Exception, str], None] = NON_FUNC
    ):
        for name, func in self.plugins_funcs["on_player_leave"]:
            try:
                func(player)
            except Exception as err:
                onerr(name, err, traceback.format_exc())

    def execute_player_death(
        self,
        player,
        killer,
        msg,
        onerr: Callable[[str, Exception, str], None] = NON_FUNC,
    ):
        for name, func in self.plugins_funcs["on_player_death"]:
            try:
                func(player, killer, msg)
            except Exception as err:
                onerr(name, err, traceback.format_exc())

    def processPacketFunc(self, pktID: int, pkt: dict):
        d = self.packet_funcs.get(str(pktID), None)
        if d:
            for func in d:
                try:
                    res = func(pkt)
                    if res:
                        return True
                except:
                    Print.print_err(f"插件方法 {func.__name__} 出错：")
                    Print.print_err(traceback.format_exc())
        return False
