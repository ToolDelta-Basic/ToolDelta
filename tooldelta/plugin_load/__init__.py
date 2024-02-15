import os, sys, traceback, zipfile, time, threading, importlib, asyncio
from typing import Callable, Type, Any
from . import dotcs_plugin
from . import classic_plugin
from . import injected_plugin
from .classic_plugin import Plugin, PluginAPI
from ..color_print import Print
from ..cfg import Cfg
from ..builtins import Builtins
from ..basic_mods import dotcs_module_env
from ..get_python_libs import get_single_lib


class PluginSkip(EOFError): ...

NON_FUNC = lambda *_: None

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
        self.injected_plugin_loaded_num = 0
        self.linked_frame = frame
        self.PRG_NAME = PRG_NAME
        self._dotcs_repeat_threadings = {"1s": [], "10s": [], "30s": [], "1m": []}
        self.linked_frame.linked_plugin_group = self

    def require(self, module_name: str, pip_name = ""):
        try:
            importlib.import_module(module_name)
        except (ModuleNotFoundError, ImportError):
            get_single_lib(pip_name if pip_name else module_name)

    def read_all_plugins(self):
        dotcs_plugin.read_plugin_from_old(self, dotcs_module_env)
        classic_plugin.read_plugin_from_new(self, {})
        asyncio.run(injected_plugin.load_plugin(self))

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
        def deco(func):
            self.plugin_added_cache["packets"].append((pktID, func))
            return func

        return deco

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

    def get_plugin_api(self, apiName: str, min_version: tuple | None = None) -> PluginAPI:
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

    def _add_plugin(self, plugin: Plugin):
        self.plugins.append(plugin)

    def _add_listen_packet_id(self, packetType: int):
        self.listen_packet_ids.add(packetType)
        self.linked_frame.link_game_ctrl.add_listen_pkt(packetType)

    def _add_listen_packet_func(self, packetType, func: Callable):
        if self.packet_funcs.get(str(packetType), None):
            self.packet_funcs[str(packetType)].append(func)
        else:
            self.packet_funcs[str(packetType)] = [func]

    def execute_dotcs_repeat(self):
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
                        Print.print_err(
                            f"原dotcs插件 <{fname}> (计划任务1min)报错: {err}"
                        )
                lastTime1m = nowTime
            if nowTime - lastTime30s > 30:
                for fname, func in self._dotcs_repeat_threadings["30s"]:
                    try:
                        func()
                    except Exception as err:
                        Print.print_err(
                            f"原dotcs插件 <{fname}> (计划任务30s)报错: {err}"
                        )
                lastTime30s = nowTime
            if nowTime - lastTime10s > 10:
                for fname, func in self._dotcs_repeat_threadings["10s"]:
                    try:
                        func()
                    except Exception as err:
                        Print.print_err(
                            f"原dotcs插件 <{fname}> (计划任务10s)报错: {err}"
                        )
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
        player: str,
        killer: str,
        msg: str,
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


# NOTE 快捷导入插件函数(待增加)

from .injected_plugin.movent import (
    sendcmd,
    sendfbcmd,
    sendPacket,
    sendPacketJson,
    sendwocmd,
    sendwscmd,
    tellrawText,
    get_all_player,
    getTarget,
    rawText,
    is_op,
    getPos,
    get_robotname,
    countdown,
    getBlockTile,
    getTickingAreaList,
)

from .injected_plugin import player_message, player_join, player_left, repeat, init
