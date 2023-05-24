from typing import Callable, Tuple, Type
from .color_print import Print
import os
import sys
import traceback
from .cfg import Cfg
from .builtins import Builtins


class PluginSkip(Exception):
    ...


NON_FUNC = lambda *_: None
_print = Print


class Plugin:
    name = "<未命名插件>"
    version = (0, 0, 1)
    author = "?"

    def __init__(this):
        this.require_listen_packets = []
        this.dotcs_old_type = False

    def add_req_listen_packet(this, pktID):
        if not pktID in this.require_listen_packets:
            this.require_listen_packets.append(pktID)

    def import_original_dotcs_plugin(this, plugin_prg: str, old_dotcs_env: dict, module_env: dict):
        this.dotcs_old_type = True
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
            if plugin_prg_lines[line].startswith("# PLUGIN TYPE: "):
                if plugin_start + 1:
                    plugin_end = line
                    runcode_tmp[plugin_prev_type] = "\n".join(
                        plugin_prg_lines[plugin_start:plugin_end])
                plugin_start = line + 1
                plugin_prev_type = plugin_prg_lines[line].strip(
                    "# PLUGIN TYPE: ")
        if plugin_start + 1:
            plugin_end = len(plugin_prg_lines)
            runcode_tmp[plugin_prev_type] = "\n".join(
                plugin_prg_lines[plugin_start:plugin_end])

        for k in runcode_tmp:
            match k:
                case "def":
                    def_exec_code = "def %s_launch(frame):\n "
                case "init":
                    def_exec_code = "def %s_init():\n "
                case "player prejoin":
                    def_exec_code = "def %s_player_prejoin(playername):\n "
                case "player join":
                    def_exec_code = "def %s_player_join(playername):\n "
                case "player message":
                    def_exec_code = "def %s_player_message(playername, msg):\n "
                case "player leave":
                    def_exec_code = "def %s_player_leave(playername):\n "
                case "player death":
                    def_exec_code = "def %s_player_death(playername, killer, msg):\n "
                case "packet":
                    def_exec_code = "def %s_packet(packetType, jsonPkt):\n "
                case "repeat 1s":
                    def_exec_code = "def %s_repeat1s():\n "
                case "repeat 10s":
                    def_exec_code = "def %s_repeat2s():\n "
                case "repeat 30s":
                    def_exec_code = "def %s_repeat30s():\n "
                case "repeat 1m":
                    def_exec_code = "def %s_repeat1m():\n "
                case _:
                    if k.startswith("packet"):
                        try:
                            pktID = int(k.split()[1])
                            def_exec_code = f"def %s_packet_{pktID}():\n "
                            this.add_req_listen_packet(pktID)
                        except:
                            _print.print_war(f"§c不合法的监听数据包ID： {k}, 已跳过")
                    else:
                        _print.print_war(f"§c无法识别的插件事件样式： {k}, 已跳过")
            p_code = def_exec_code % this.name + \
                runcode_tmp[k].replace("\n", "\n ")
            try:
                # 奇怪， 作用域没有用， 两个类里的变量字典会互相干扰?
                # oh我知道了
                exec(p_code, old_dotcs_env, _dotcs_runcode)
                if this._dotcs_runcode.get(f"{this.name}_launch", None):
                    evts["on_def"] = [this.name,
                                      _dotcs_runcode[f"{this.name}_launch"]]
                if this._dotcs_runcode.get(f"{this.name}_init", None):
                    evts["on_inject"] = [this.name,
                                         _dotcs_runcode[f"{this.name}_init"]]
                if this._dotcs_runcode.get(f"{this.name}_player_prejoin", None):
                    evts["on_player_prejoin"] = [this.name,
                                                 _dotcs_runcode[f"{this.name}_player_prejoin"]]
                if this._dotcs_runcode.get(f"{this.name}_player_join", None):
                    evts["on_player_join"] = [this.name,
                                              _dotcs_runcode[f"{this.name}_player_join"]]
                if this._dotcs_runcode.get(f"{this.name}_player_leave", None):
                    evts["on_player_leave"] = [this.name,
                                               _dotcs_runcode[f"{this.name}_player_death"]]
                if this._dotcs_runcode.get(f"{this.name}_player_leave", None):
                    evts["on_player_death"] = [this.name,
                                               _dotcs_runcode[f"{this.name}_player_death"]]
                return evts
            except Exception as err:
                _print.print_err(f"§c插件<{this.name}>出错: {err}， 跳过执行")


class PluginAPI:
    name = "<未命名api>"
    version = (0, 0, 1)


class PluginGroup:
    class PluginAPINotFoundError(ModuleNotFoundError):
        def __init__(this, name):
            this.name = name

    class PluginAPIVersionError(ModuleNotFoundError):
        def __init__(this, name, m_ver, n_ver):
            this.name = name
            this.m_ver = m_ver
            this.n_ver = n_ver
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

    def __init__(this, frame, PRG_NAME):
        this.listen_packets = []
        this.old_dotcs_env = {}
        this.linked_frame = None
        this.packet_funcs: dict[str, list[Callable]] = {}
        this.plugins_api = {}
        this.excType = 0
        this.PRG_NAME = ""
        this._broadcast_evts = {}
        this.inked_frame = frame
        this.PRG_NAME = PRG_NAME
      
    def reset(this):
        this.plugins.clear()
        this.listen_packets.clear()
        this.packet_funcs.clear()
        this.plugins_funcs.clear()
        this.plugins_funcs.update({
            "on_def": [],
            "on_inject": [],
            "on_player_prejoin": [],
            "on_player_join": [],
            "on_player_message": [],
            "on_player_death": [],
            "on_player_leave": []
        })
        this.excType = 1

    def add_plugin(this, plugin: Plugin):
        this.plugins.append(plugin)
        
    def add_broadcast_listener(this, evt_name: str):
        "将下面的方法作为一个广播事件接收器"
        def deco(func: Callable[[any], bool]):
            if this._broadcast_evts.get(evt_name, None):
                this._broadcast_evts[evt_name].append(func)
            else:
                this._broadcast_evts[evt_name] = [func]
        return deco
    
    def broadcastEvt(this, evt_name: str, **kwargs) -> list[any] | None:
        "向全局广播一个特定事件, 可以传入附加信息参数"
        callback_list = []
        res = this._broascast_evts.get(evt_name, None)
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

    def add_listen_packet(this, packetType: int):
        if not packetType in this.listen_packets:
            this.listen_packets.append(packetType)

    def add_listen_packet_func(this, packetType, func: Callable):
        if this.packet_funcs.get(str(packetType), None):
            this.packet_funcs[str(packetType)].append(func)
        else:
            this.packet_funcs[str(packetType)] = [func]

    def addPluginAPI(this, apiName: str, version: tuple):
        def _add_api(api: PluginAPI):
            if not PluginAPI.__subclasshook__(api):
                _print.print_err(f"组件API {api.name} 不合法： 主类没有继承 PluginAPI")
                raise SystemExit
            else:
                try:
                    api = api(this.linked_frame)
                    api.name, api.version = apiName, version
                    this.plugins_api[apiName] = api
                except Exception as err:
                    _print.print_err(f"组件API {api.name} 出现问题： {err}")
                    raise SystemExit
        return _add_api

    def getPluginAPI(this, apiName: str, min_version: tuple = None):
        api = this.plugins_api.get(apiName, None)
        if api:
            if min_version and api.version < min_version:
                raise this.PluginAPIVersionError(
                    apiName, min_version, api.version)
            return api
        else:
            raise this.PluginAPINotFoundError(apiName)

    def read_plugin_from_old(this, module_env: dict):
        for file in os.listdir("DotCS兼容插件"):
            try:
                if file.endswith(".py"):
                    _print.print_inf(f"§6加载DotCS插件: {file.strip('.py')}")
                    with open("DotCS兼容插件/" + file, "r", encoding='utf-8') as f:
                        code = f.read()
                    plug = Plugin()
                    plug.name = file.strip(".py")
                    evts = plug.import_original_dotcs_plugin(
                        code, this.linked_frame._get_old_dotcs_env(), module_env)
                    this.plugins_funcs.update(evts)
                    this.add_plugin(plug)
                    _print.print_suc(f"§a成功加载插件 {plug.name}")
            except Exception as err:
                _print.print_err("§c加载插件出现问题: ")
                print(err)
                traceback.print_exc()

    def read_plugin_from_new(this, root_env: dict):
        pkt_funcs: dict[str, str] = {}
        plug_cls_cache = [None, 0]

        def _listen_packet(packetType: int):
            def _add(func: Callable[[dict], None]):
                pkt_funcs.update({str(packetType): func.__name__})
                return func
            return _add

        def _add_plugin_new(plugin: Plugin):
            plug_cls_cache[1] += 1
            assert Plugin.__subclasscheck__(plugin), 1
            plugin_body: Plugin = plugin(this.linked_frame)
            plug_cls_cache[0] = plugin_body
            this.plugins.append(plugin_body)
            _v0, _v1, _v2 = plugin_body.version
            if hasattr(plugin_body, "on_def"):
                this.plugins_funcs["on_def"].append(
                    [plugin_body.name, plugin_body.on_def])
            if hasattr(plugin_body, "on_inject"):
                this.plugins_funcs["on_inject"].append(
                    [plugin_body.name, plugin_body.on_inject])
            if hasattr(plugin_body, "on_player_prejoin"):
                this.plugins_funcs["on_player_prejoin"].append(
                    [plugin_body.name, plugin_body.on_player_prejoin])
            if hasattr(plugin_body, "on_player_join"):
                this.plugins_funcs["on_player_join"].append(
                    [plugin_body.name, plugin_body.on_player_join])
            if hasattr(plugin_body, "on_player_message"):
                this.plugins_funcs["on_player_message"].append(
                    [plugin_body.name, plugin_body.on_player_message])
            if hasattr(plugin_body, "on_player_death"):
                this.plugins_funcs["on_player_death"].append(
                    [plugin_body.name, plugin_body.on_player_death])
            if hasattr(plugin_body, "on_player_leave"):
                this.plugins_funcs["on_player_leave"].append(
                    [plugin_body.name, plugin_body.on_player_leave])

            _print.print_suc(
                f"成功载入插件 {plugin_body.name} 版本：{_v0}.{_v1}.{_v2}  作者：{plugin_body.author}")

        loc_env = {"add_plugin": _add_plugin_new, "addPluginAPI": this.addPluginAPI,
                   "listen_packet": _listen_packet, "plugins": this.linked_frame.link_plugin_group}
        root_env.update(loc_env)
        for plugin_dir in os.listdir(f"{this.PRG_NAME}插件"):
            if os.path.isdir(f"{this.PRG_NAME}插件/" + plugin_dir):
                pkt_funcs.clear()
                plug_cls_cache.clear()
                plug_cls_cache += [None, 0]
                sys.path.append(
                    os.getcwd() + f"/{this.PRG_NAME}插件/" + plugin_dir)
                try:
                    with open(f"{this.PRG_NAME}插件/" + plugin_dir + "/__init__.py", "r", encoding='utf-8') as f:
                        code = f.read()
                    exec(code, root_env)
                    assert plug_cls_cache[1] <= 1, 2
                    assert not pkt_funcs or (
                        pkt_funcs and plug_cls_cache[1] != 0), 3
                    for k in pkt_funcs:
                        pktType = int(k)
                        this.add_listen_packet(pktType)
                        this.add_listen_packet_func(
                            pktType, getattr(plug_cls_cache[0], pkt_funcs[k]))
                        this.linked_frame.link_game_ctrl.add_listen_pkt(
                            pktType)
                except FileNotFoundError as err:
                    if "__init__.py" in err:
                        _print.print_err(f"插件 {plugin_dir} 不合法： 没有__init__.py")
                    else:
                        raise
                except AssertionError as err:
                    if err.args[0] == 1:
                        _print.print_err(f"插件 {plugin_dir} 不合法： 主类没有继承 Plugin")
                    elif err.args[0] == 2:
                        _print.print_err(
                            f"插件 {plugin_dir} 不合法： 只能调用一次 @add_plugin, 实际{plug_cls_cache[1]}次")
                    elif err.args[0] == 3:
                        _print.print_err(
                            f"插件 {plugin_dir} 不合法： 没有调用 @add_plugin 却监听了数据包")
                    else:
                        raise
                except Cfg.ConfigError as err:
                    _print.print_err(f"插件 {plugin_dir} 配置文件报错：{err}")
                    _print.print_err(f"你也可以直接删除配置文件, 重新启动ToolDelta以自动生成配置文件")
                    raise SystemExit
                except PluginGroup.PluginAPINotFoundError as err:
                    _print.print_err(
                        f"插件 {plugin_dir} 需要包含该种接口的前置组件: {err.name}")
                    raise SystemExit
                except PluginGroup.PluginAPIVersionError as err:
                    _print.print_err(
                        f"插件 {plugin_dir} 需要该前置组件 {err.name} 版本: {err.m_ver}, 但是现有版本过低: {err.n_ver}")
                    raise SystemExit
                except Builtins.SimpleJsonDataReader.DataReadError as err:
                    _print.print_err(f"插件 {plugin_dir} 读取数据失败: {err}")
                except Exception as err:
                    if "() takes no arguments" in str(err):
                        _print.print_err(
                            f"插件 {plugin_dir} 不合法： 主类初始化时应接受 1 个参数: Frame")
                    else:
                        _print.print_err(f"加载插件 {plugin_dir} 出现问题，报错如下: ")
                        _print.print_err(traceback.format_exc())
                        raise SystemExit

    def read_plugin_from_nonop(this, root_env: dict):
        for plugin_dir in os.listdir(f"{this.PRG_NAME}无OP运行插件"):
            if os.path.isdir(f"{this.PRG_NAME}运行插件/" + plugin_dir):
                _print.print_inf(f"§6加载无OP运行插件: {plugin_dir}")
                with open(f"{this.PRG_NAME}无OP运行插件/" + plugin_dir + "/__init__.py", "r", encoding='utf-8') as f:
                    code = f.read()

    def add_listen_packet(this, pktID: int):
        if not pktID in this.listen_packets:
            this.listen_packets.append(pktID)

    def execute_def(this, onerr: Callable[[str, Exception, str], None]):
        for name, func in this.plugins_funcs["on_def"]:
            try:
                func()
            except Exception as err:
                onerr(name, err, traceback.format_exc())

    def execute_init(this, onerr: Callable[[str, Exception, str], None]):
        for name, func in this.plugins_funcs["on_inject"]:
            try:
                func()
            except Exception as err:
                onerr(name, err, traceback.format_exc())

    def execute_player_prejoin(this, player, onerr: Callable[[str, Exception, str], None]):
        for name, func in this.plugins_funcs["on_player_prejoin"]:
            try:
                func(player)
            except Exception as err:
                onerr(name, err, traceback.format_exc())

    def execute_player_join(this, player, onerr: Callable[[str, Exception, str], None] = NON_FUNC):
        for name, func in this.plugins_funcs["on_player_join"]:
            try:
                func(player)
            except Exception as err:
                onerr(name, err, traceback.format_exc())

    def execute_player_message(this, player, msg, onerr: Callable[[str, Exception, str], None]):
        pat = f"[{player}] "
        if msg.startswith(pat):
            msg = msg.strip(pat)
        for name, func in this.plugins_funcs["on_player_message"]:
            try:
                func(player, msg)
            except Exception as err:
                onerr(name, err, traceback.format_exc())

    def execute_player_leave(this, player, onerr: Callable[[str, Exception, str], None]):
        for name, func in this.plugins_funcs["on_player_join"]:
            try:
                func(player)
            except Exception as err:
                onerr(name, err, traceback.format_exc())

    def execute_player_death(this, player, killer, msg, onerr: Callable[[str, Exception, str], None]):
        for name, func in this.plugins_funcs["on_player_death"]:
            try:
                func(player, killer, msg)
            except Exception as err:
                onerr(name, err, traceback.format_exc())

    def execute_packet(this, packetID, packet, onerr: Callable[[str, Exception, str], None]):
        "Really will be in used?"
        for plugin in this.plugins:
            try:
                if plugin.dotcs_old_type:
                    if packetID in plugin.require_listen_packets:
                        plugin.dotcs_runcode.get(
                            f"{plugin.name}_packet_{packetID}", NON_FUNC)(packet)
            except PluginSkip:
                pass
            except Exception as err:
                onerr(plugin.name, err, traceback.format_exc())

    def processPacketFunc(this, pktID: int, pkt: dict):
        d = this.packet_funcs.get(str(pktID), None)
        if d:
            for func in d:
                try:
                    print(func.__name__)
                    func(pkt)
                except:
                    _print.print_err(f"插件方法 {func} 出错：")
                    _print.print_err(traceback.format_exc())
