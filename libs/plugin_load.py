from typing import Callable, Type
from .color_print import Print
import os, sys, traceback, zipfile, time, threading, re
from .cfg import Cfg
from .builtins import Builtins
try:
    raise
    from .pluginDec import decPluginAndCMP
except:
    decPluginAndCMP = None

class PluginSkip(EOFError):...

NON_FUNC = lambda *_: None
NOT_IMPORTALL_RULE = re.compile("from .* import \*")

def unzip_plugin(zip_dir, exp_dir):
    try:
        f = zipfile.ZipFile(zip_dir, "r")
        f.extractall(exp_dir)
    except Exception as err:
        Print.print_err(f"zipfile: 解压失败: {err}")
        print(traceback.format_exc())
        os._exit(0)

class Plugin:
    name = "<未命名插件>"
    version = (0, 0, 1)
    author = "?"
    def __init__(self):
        self.require_listen_packets = []
        self.dotcs_old_type = False

    def add_req_listen_packet(self, pktID):
        if not pktID in self.require_listen_packets:
            self.require_listen_packets.append(pktID)

    def import_original_dotcs_plugin(self, plugin_prg: str, old_dotcs_env: dict, module_env: dict, plugin_group):
        # dotcs插件太不规范了!!
        self.dotcs_old_type = True
        old_dotcs_env.update(module_env)
        runcode_tmp = {}
        plugin_prg_lines = plugin_prg.split("\n")
        _dotcs_runcode = {}
        evts = {}
        while 1:
            if "" in plugin_prg_lines:
                plugin_prg_lines.remove("")
            else:
                break
        plugin_start = -1
        plugin_end = 0
        plugin_prev_type = ""

        for line in range(len(plugin_prg_lines)):
            if "import *" in plugin_prg_lines[line]:
                Print.print_war(f"DotCS插件 存在异常的代码 'import *', 已自动替换为 pass: §7{line} §f|{plugin_prg_lines[line]}")
                plugin_prg_lines[line] = NOT_IMPORTALL_RULE.sub("pass", plugin_prg_lines[line])
            if plugin_prg_lines[line].startswith("# PLUGIN TYPE: "):
                if plugin_start + 1:
                    plugin_end = line
                    runcode_tmp[plugin_prev_type] = "\n".join(plugin_prg_lines[plugin_start:plugin_end])
                plugin_start = line + 1
                plugin_prev_type = plugin_prg_lines[line].strip("# PLUGIN TYPE: ")
        if plugin_start + 1:
            plugin_end = len(plugin_prg_lines)
            runcode_tmp[plugin_prev_type] = "\n".join(plugin_prg_lines[plugin_start:plugin_end])

        old_dotcs_env.update({"plugin_group": plugin_group})
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
                                fun_exec_code = f"def packet_{pktID}(packetType, jsonPkt):\n "
                                self.add_req_listen_packet(pktID)
                        except:
                            Print.print_war(f"§c不合法的监听数据包ID： {k}, 已跳过")  
                    else:
                        raise Exception(f"无法识别的DotCS插件事件样式： {k}")
            # DotCS 有太多的插件都会出现作用域问题, 在此只能这么修复了
            # ouch
            p_code = fun_exec_code + """globals().update(plugin_group.dotcs_global_vars)\n """ \
                + runcode_tmp[k].replace("\n", "\n ") + \
                    "\n plugin_group.dotcs_global_vars.update(locals())"
            try:
                exec(p_code, old_dotcs_env, _dotcs_runcode)
            except Exception as err:
                Print.print_err(f"DotCS插件 <{self.name}> 出错: {err}")
                raise
        for codetype in [
                "on_def",
                "on_init",
                "on_player_prejoin",
                "on_player_join",
                "on_player_message",
                "on_player_death",
                "on_player_leave"
        ]:
            if _dotcs_runcode.get(codetype, None):
                evts[codetype] = [self.name, _dotcs_runcode[codetype]]
        if _dotcs_runcode.get(f"repeat1s", None):
                evts["repeat1s"] = [self.name, _dotcs_runcode[f"repeat1s"]]
        if _dotcs_runcode.get(f"repeat10s", None):
                evts["repeat10s"] = [self.name, _dotcs_runcode[f"repeat10s"]]
        if _dotcs_runcode.get(f"repeat30s", None):
                evts["repeat30s"] = [self.name, _dotcs_runcode[f"repeat30s"]]
        if _dotcs_runcode.get(f"repeat1m", None):
                evts["repeat1m"] = [self.name, _dotcs_runcode[f"repeat1m"]]
        return evts

class PluginAPI:
    name = "<未命名插件api>"
    version = (0, 0, 1)

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
        "on_player_leave": []
    }


    def __init__(self, frame, PRG_NAME):
        self.listen_packets = []
        self.old_dotcs_env = {}
        self.dotcs_global_vars = {}
        self.packet_funcs: dict[str, list[Callable]] = {}
        self.plugins_api = {}
        self.excType = 0
        self.PRG_NAME = ""
        self._broadcast_evts = {}
        self.linked_frame = frame
        self.PRG_NAME = PRG_NAME
        self._dotcs_repeat_threadings = {"1s": [], "10s": [], "30s": [], "1m": []}
      
    def reset(self):
        self.plugins.clear()
        self.listen_packets.clear()
        self.packet_funcs.clear()
        self.plugins_funcs.clear()
        self.plugins_funcs.update({
            "on_def": [],
            "on_inject": [],
            "on_player_prejoin": [],
            "on_player_join": [],
            "on_player_message": [],
            "on_player_death": [],
            "on_player_leave": []
        })
        self.excType = 1
        self._dotcs_repeat_threadings = {"1s": [], "10s": [], "30s": [], "1m": []}

    def add_plugin(self, plugin: Type[Plugin]):
        self.plugins.append(plugin)
        
    def add_broadcast_listener(self, evt_name: str):
        "将下面的方法作为一个广播事件接收器"
        def deco(func: Callable[[any], bool]):
            if self._broadcast_evts.get(evt_name, None):
                self._broadcast_evts[evt_name].append(func)
            else:
                self._broadcast_evts[evt_name] = [func]
        return deco
    
    def broadcastEvt(self, evt_name: str, **kwargs) -> list[any] | None:
        "向全局广播一个特定事件, 可以传入附加信息参数"
        callback_list = []
        res = self._broascast_evts.get(evt_name, None)
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

    def add_plugin(self, plugin: Plugin):
        self.plugins.append(plugin)

    def add_listen_packet(self, packetType: int):
        if not packetType in self.listen_packets:
            self.listen_packets.append(packetType)

    def add_listen_packet_func(self, packetType, func: Callable):
        if self.packet_funcs.get(str(packetType), None):
            self.packet_funcs[str(packetType)].append(func)
        else:
            self.packet_funcs[str(packetType)] = [func]

    def addPluginAPI(self, apiName: str, version: tuple):
        def _add_api(api: PluginAPI):
            if not PluginAPI.__subclasshook__(api):
                Print.print_err(f"组件API {api.name} 不合法： 主类没有继承 PluginAPI")
                raise SystemExit
            else:
                try:
                    api = api(self.linked_frame)
                    api.name, api.version = apiName, version
                    self.plugins_api[apiName] = api
                except Exception as err:
                    Print.print_err(f"组件API {api.name} 出现问题： {err}")
                    raise SystemExit
        return _add_api

    def getPluginAPI(self, apiName: str, min_version: tuple = None):
        api = self.plugins_api.get(apiName, None)
        if api:
            if min_version and api.version < min_version:
                raise self.PluginAPIVersionError(apiName, min_version, api.version)
            return api
        else:
            raise self.PluginAPINotFoundError(apiName)
        
    def checkSystemVersion(this, need_vers: tuple[int, int, int]):
        if need_vers > this.linked_frame.sys_data.system_version:
            raise this.linked_frame.SystemVersionException(
                f"该组件需要{this.linked_frame.PRG_NAME}为{'.'.join([str(i) for i in this.linked_frame.sys_data.system_version])}版本"
            )

    def read_plugin_from_old(self, module_env: dict):
        sys.path.append(os.getcwd() + "/DotCS兼容插件")
        for file in os.listdir("DotCS兼容插件"):
            try:
                if file.endswith(".py"):
                    Print.print_inf(f"§6载入DotCS插件: {file.strip('.py')}", end="\r")
                    with open("DotCS兼容插件/" + file, "r", encoding='utf-8') as f:
                        code = f.read()
                    plug = Plugin()
                    plug.name = file.strip(".py")
                    evts = plug.import_original_dotcs_plugin(code, self.linked_frame._get_old_dotcs_env(), module_env, self)
                    if "repeat10s" in evts.keys() or "repeat1s" in evts.keys() or "repeat30s" in evts.keys() or "repeat1m" in evts.keys():
                        evtnew = evts.copy()
                        for i in evtnew.keys():
                            if i.startswith("repeat"):
                                del evts[i]
                                self._dotcs_repeat_threadings[i.strip("repeat")].append(evtnew[i])
                    for k, v in evts.items():
                        self.plugins_funcs[k].append(v)
                    self.add_plugin(plug)
                    Print.print_suc(f"§a成功载入插件 §2<DotCS> §a{plug.name}")
            except Exception as err:
                Print.print_err(f"§c加载插件 {plug.name} 出现问题: {err}")
                raise

    def read_plugin_from_new(self, root_env: dict):
        pkt_funcs: dict[str, str] = {}
        plug_cls_cache = [None, 0]
        def _listen_packet(packetType: int):
            def _decorate(func: Callable[[dict], None]):
                pkt_funcs.update({str(packetType): func.__name__})
                return func
            return _decorate
        def _add_plugin_new(plugin: Type[Plugin]):
            plug_cls_cache[1] += 1
            assert Plugin.__subclasscheck__(plugin), 1
            plugin_body = plugin(self.linked_frame)
            plug_cls_cache[0] = plugin_body
            self.plugins.append(plugin_body)
            _v0, _v1, _v2 = plugin_body.version
            if hasattr(plugin_body, "on_def"):
                self.plugins_funcs["on_def"].append([plugin_body.name, plugin_body.on_def])
            if hasattr(plugin_body, "on_inject"):
                self.plugins_funcs["on_inject"].append([plugin_body.name, plugin_body.on_inject])
            if hasattr(plugin_body, "on_player_prejoin"):
                self.plugins_funcs["on_player_prejoin"].append([plugin_body.name, plugin_body.on_player_prejoin])
            if hasattr(plugin_body, "on_player_join"):
                self.plugins_funcs["on_player_join"].append([plugin_body.name, plugin_body.on_player_join])
            if hasattr(plugin_body, "on_player_message"):
                self.plugins_funcs["on_player_message"].append([plugin_body.name, plugin_body.on_player_message])
            if hasattr(plugin_body, "on_player_death"):
                self.plugins_funcs["on_player_death"].append([plugin_body.name, plugin_body.on_player_death])
            if hasattr(plugin_body, "on_player_leave"):
                self.plugins_funcs["on_player_leave"].append([plugin_body.name, plugin_body.on_player_leave])

            Print.print_suc(f"成功载入插件 {plugin_body.name} 版本：{_v0}.{_v1}.{_v2}  作者：{plugin_body.author}")

        loc_env = {"add_plugin": _add_plugin_new, "addPluginAPI": self.addPluginAPI, "listen_packet": _listen_packet}
        root_env.update(loc_env)
        for plugin_dir in os.listdir(f"{self.PRG_NAME}插件"):
            if not os.path.isdir(f"{self.PRG_NAME}插件/" + plugin_dir.strip(".zip")) and os.path.isfile(f"{self.PRG_NAME}插件/" + plugin_dir) and plugin_dir.endswith(".zip"):
                Print.print_with_info(f"§6正在解压插件{plugin_dir}, 请稍后", "§6 解压 ")
                unzip_plugin(f"{self.PRG_NAME}插件/" + plugin_dir, f"{self.PRG_NAME}插件/" + plugin_dir.strip(".zip"))
                Print.print_suc(f"§a成功解压插件{plugin_dir} -> 插件目录")
                plugin_dir = plugin_dir.strip(".zip")
            if os.path.isdir(f"{self.PRG_NAME}插件/" + plugin_dir):
                pkt_funcs.clear()
                plug_cls_cache.clear()
                plug_cls_cache += [None, 0]
                sys.path.append(os.getcwd() + f"/{self.PRG_NAME}插件/" + plugin_dir)
                try:
                    if os.path.isfile(f"{self.PRG_NAME}插件/" + plugin_dir + "/__init__.py"):
                        with open(f"{self.PRG_NAME}插件/" + plugin_dir + "/__init__.py", "r", encoding='utf-8') as f:
                            code = f.read()
                        exec(code, root_env)
                    elif os.path.isfile(f"{self.PRG_NAME}插件/" + plugin_dir + "/__MAIN__.tdenc"):
                        if decPluginAndCMP is not None:
                            with open(f"{self.PRG_NAME}插件/" + plugin_dir + "/__MAIN__.tdenc", "rb") as f:
                                cp = decPluginAndCMP(f.read())
                                if (cp == 0) | (cp == 1):
                                    raise Exception(f"加密插件: {plugin_dir} 加载失败 ERR={cp}")
                                exec(cp, root_env)
                        else:
                            Print.print_err(f"未开启高级模式(需要付费或使用专属面板), 无法加载加密插件{plugin_dir}, 跳过加载")
                            continue
                    else:
                        Print.print_err(f"{plugin_dir} 文件夹 未发现插件文件, 跳过加载")
                        continue
                    assert plug_cls_cache[1] <= 1, 2
                    assert not pkt_funcs or (pkt_funcs and plug_cls_cache[1] != 0), 3
                    for k in pkt_funcs:
                        pktType = int(k)
                        self.add_listen_packet(pktType)
                        self.add_listen_packet_func(pktType, getattr(plug_cls_cache[0], pkt_funcs[k]))
                        self.linked_frame.link_game_ctrl.add_listen_pkt(pktType)
                except AssertionError as err:
                    if err.args[0] == 1:
                        Print.print_err(f"插件 {plugin_dir} 不合法： 主类没有继承 Plugin")
                    elif err.args[0] == 2:
                        Print.print_err(f"插件 {plugin_dir} 不合法： 只能调用一次 @add_plugin, 实际{plug_cls_cache[1]}次")
                    elif err.args[0] == 3:
                        Print.print_err(f"插件 {plugin_dir} 不合法： 没有调用 @add_plugin 却监听了数据包")
                    else:
                        raise
                except Cfg.ConfigError as err:
                    Print.print_err(f"插件 {plugin_dir} 配置文件报错：{err}")
                    Print.print_err(f"你也可以直接删除配置文件, 重新启动ToolDelta以自动生成配置文件")
                    raise SystemExit
                except Builtins.SimpleJsonDataReader.DataReadError as err:
                    Print.print_err(f"插件 {plugin_dir} 读取数据失败: {err}")
                except Exception as err:
                    if "() takes no arguments" in str(err):
                        Print.print_err(f"插件 {plugin_dir} 不合法： 主类初始化时应接受 1 个参数: Frame")
                    else:
                        Print.print_err(f"加载插件 {plugin_dir} 出现问题, 报错如下: ")
                        Print.print_err(traceback.format_exc())
                        raise SystemExit
        for spec_func in loc_env.keys():
            del root_env[spec_func]

    def read_plugin_from_nonop(self, root_env: dict):
        for plugin_dir in os.listdir(f"{self.PRG_NAME}无OP运行插件"):
            if os.path.isdir(f"{self.PRG_NAME}运行插件/" + plugin_dir):
                Print.print_inf(f"§6加载无OP运行插件: {plugin_dir}")
                with open(f"{self.PRG_NAME}无OP运行插件/" + plugin_dir + "/__init__.py", "r", encoding='utf-8') as f:
                    code = f.read()

    def add_listen_packet(self, pktID: int):
        if not pktID in self.listen_packets: 
            self.listen_packets.append(pktID)

    def execute_dotcs_repeat(self, on_plugin_err):
        threading.Thread(target=self.run_dotcs_repeat_funcs).start()

    def run_dotcs_repeat_funcs(self):
        lastTime10s = 0
        lastTime30s = 0
        lastTime1m = 0
        if not any(self._dotcs_repeat_threadings.values()):
            return
        Print.print_inf(f"开始运行 {sum([len(funcs) for funcs in self._dotcs_repeat_threadings.values()])} 个原dotcs计划任务方法")
        while 1:
            time.sleep(1)
            nowTime = time.time()
            if nowTime - lastTime1m > 60:
                for fname, func in self._dotcs_repeat_threadings["1m"]:
                    try:
                        # A strong desire to delete "try" block !!
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
                Print.print_err(f"插件 {name} 需要该前置组件 {err.name} 版本: {err.m_ver}, 但是现有版本过低: {err.n_ver}")
                raise SystemExit
            except Exception as err:
                 onerr(name, err, traceback.format_exc())

    def execute_init(self, onerr: Callable[[str, Exception, str], None] = NON_FUNC):
        for name, func in self.plugins_funcs["on_inject"]:
            try:
                func()
            except Exception as err:
                 onerr(name, err, traceback.format_exc())

    def execute_player_prejoin(self, player, onerr: Callable[[str, Exception, str], None] = NON_FUNC):
        for name, func in self.plugins_funcs["on_player_prejoin"]:
            try:
                func(player)
            except Exception as err:
                 onerr(name, err, traceback.format_exc())

    def execute_player_join(self, player, onerr: Callable[[str, Exception, str], None] = NON_FUNC):
        for name, func in self.plugins_funcs["on_player_join"]:
            try:
                func(player)
            except Exception as err:
                 onerr(name, err, traceback.format_exc())

    def execute_player_message(self, player, msg, onerr: Callable[[str, Exception, str], None] = NON_FUNC):
        pat = f"[{player}] "
        if msg.startswith(pat):
            msg = msg.strip(pat)
        for name, func in self.plugins_funcs["on_player_message"]:
            try:
                func(player, msg)
            except Exception as err:
                 onerr(name, err, traceback.format_exc())

    def execute_player_leave(self, player, onerr: Callable[[str, Exception, str], None] = NON_FUNC):
        for name, func in self.plugins_funcs["on_player_join"]:
            try:
                func(player)
            except Exception as err:
                 onerr(name, err, traceback.format_exc())

    def execute_player_death(self, player, killer, msg, onerr: Callable[[str, Exception, str], None] = NON_FUNC):
        for name, func in self.plugins_funcs["on_player_death"]:
            try:
                func(player, killer, msg)
            except Exception as err:
                 onerr(name, err, traceback.format_exc())

    def execute_packet(self, packetID, packet, onerr: Callable[[str, Exception, str], None] = NON_FUNC):
        "Really will be in used?"
        for plugin in self.plugins:
            try:
                if plugin.dotcs_old_type:
                    if packetID in plugin.require_listen_packets:
                        plugin.dotcs_runcode.get(f"packet_{packetID}", NON_FUNC)(packet)
            except PluginSkip:
                pass
            except Exception as err:
                onerr(plugin.name, err, traceback.format_exc())

    def processPacketFunc(self, pktID: int, pkt: dict):
        d = self.packet_funcs.get(str(pktID), None)
        if d:
            for func in d:
                try:
                    func(pkt)
                except:
                    Print.print_err(f"插件方法 {func} 出错：")
                    Print.print_err(traceback.format_exc())
