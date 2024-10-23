"ToolDelta 类式插件"

import importlib
import os
import sys
import traceback
from typing import TYPE_CHECKING, TypeVar
from collections.abc import Callable

from tooldelta.cfg import Cfg
from tooldelta.color_print import Print
from tooldelta.utils import Utils
from tooldelta.constants import (
    TOOLDELTA_PLUGIN_DIR,
    TOOLDELTA_CLASSIC_PLUGIN,
    TOOLDELTA_PLUGIN_DATA_DIR,
    PacketIDS,
)
from .. import (
    NotValidPluginError,
    PluginAPINotFoundError,
    PluginAPIVersionError,
    plugin_is_enabled,
)

if TYPE_CHECKING:
    # 类型注释
    from tooldelta import ToolDelta
    from tooldelta.plugin_load.PluginGroup import PluginGroup

_ON_ERROR_CB = Callable[[str, Exception, str], None]
__caches__ = {"plugin": None, "api_name": "", "frame": None}
plugins_funcs: dict[str, list[tuple[str, Callable]]] = {
    "on_def": [],
    "on_inject": [],
    "on_player_prejoin": [],
    "on_player_join": [],
    "on_player_message": [],
    "on_player_death": [],
    "on_player_leave": [],
    "on_command": [],
    "on_frame_exit": [],
    "on_reload": [],
}
packet_funcs: dict[int, list[Callable]] = {}
broadcast_evts_listener: dict[str, list[Callable]] = {}
loaded_plugin_modules = []


class Plugin:
    "插件主类"

    name: str = ""
    "插件名"
    version = (0, 0, 1)
    "插件版本号"
    author = "?"
    "作者名"
    description = "..."
    "简介"

    __path_created__ = False

    def __init__(self, frame: "ToolDelta"):
        self.frame = frame
        self.game_ctrl = frame.get_game_control()

    @property
    def data_path(self) -> str:
        "该插件的数据文件夹路径 (调用时直接创建数据文件夹)"
        path = os.path.join(TOOLDELTA_PLUGIN_DATA_DIR, self.name)
        if not self.__path_created__:
            os.makedirs(path, exist_ok=True)
            self.__path_created__ = True
        return path

    def make_data_path(self):
        os.makedirs(os.path.join(TOOLDELTA_PLUGIN_DATA_DIR, self.name), exist_ok=True)
        self.__path_created__ = True

    def print(self, msg: str):
        Print.print_inf(f"{self.name}: {msg}")

    def format_data_path(self, *paths: str):
        return os.path.join(self.data_path, *paths)


_PLUGIN_CLS_TYPE = TypeVar("_PLUGIN_CLS_TYPE")


def add_plugin(plugin: type[_PLUGIN_CLS_TYPE]) -> type[_PLUGIN_CLS_TYPE]:
    try:
        if not Plugin.__subclasscheck__(plugin):
            raise NotValidPluginError(f"插件主类必须继承 Plugin 类 而不是 {plugin}")
    except TypeError as exc:
        raise NotValidPluginError(
            f"插件主类必须继承 Plugin 类 而不是 {plugin.__class__}"
        ) from exc
    if __caches__["plugin"] is not None:
        raise NotValidPluginError("调用了多次 @add_plugin")
    if __caches__["frame"] is None:
        Print.clean_print("§d正在以直接运行模式运行插件..")
        return plugin
    plugin_ins = plugin(__caches__["frame"])  # type: ignore
    __caches__["plugin"] = plugin_ins
    return plugin


def add_plugin_as_api(apiName: str):
    def _add_plugin_2_api(api_plugin: type[_PLUGIN_CLS_TYPE]) -> type[_PLUGIN_CLS_TYPE]:
        if not Plugin.__subclasscheck__(api_plugin):
            raise NotValidPluginError("API 插件主类必须继承 Plugin 类")
        if __caches__["plugin"] is not None:
            raise NotValidPluginError("调用了多次 @add_plugin")
        if __caches__["frame"] is None:
            Print.clean_print("§d正在以直接运行模式运行插件..")
            return api_plugin
        plugin_ins = api_plugin(__caches__["frame"])  # type: ignore
        __caches__["plugin"] = plugin_ins
        __caches__["api_name"] = apiName
        return api_plugin

    return _add_plugin_2_api


# Plugin get and execute


def read_plugins(plugin_grp: "PluginGroup") -> None:
    """
    读取插件

    Args:
        plugin_grp (PluginGroup): 插件组
    """
    PLUGIN_PATH = os.path.join(TOOLDELTA_PLUGIN_DIR, TOOLDELTA_CLASSIC_PLUGIN)
    if PLUGIN_PATH not in sys.path:
        sys.path.append(PLUGIN_PATH)
    broadcast_evts_listener.clear()
    packet_funcs.clear()
    for plugin_dir in os.listdir(PLUGIN_PATH):
        if not plugin_is_enabled(plugin_dir):
            continue
        if os.path.isdir(os.path.join(PLUGIN_PATH, plugin_dir)):
            sys.path.append(os.path.join(PLUGIN_PATH, plugin_dir))
            load_plugin(plugin_grp, plugin_dir)
            if os.path.isfile(
                data_path := os.path.join(
                    "插件文件", TOOLDELTA_CLASSIC_PLUGIN, plugin_dir, "datas.json"
                )
            ):
                plugin_data = Utils.JsonIO.SafeJsonLoad(data_path)
                plugin_grp.loaded_plugin_ids.append(plugin_data["plugin-id"])


def load_plugin(plugin_group: "PluginGroup", plugin_dirname: str) -> None | Plugin:
    """加载插件

    Args:
        plugin_group (PluginGroup): 插件组类
        plugin_dirname (str): 插件目录名
        hot_load (bool, optional): 是否热加载

    Raises:
        ValueError: 插件组未初始化读取
        ValueError: 插件组未绑定框架
        ValueError: 插件主类需要作者名
        ValueError: 插件主类需要作者名
        NotValidPluginError: 插件 不合法
        SystemExit: 插件名字不合法
        SystemExit: 插件配置文件报错
        SystemExit: 插件读取数据失败

    Returns:
        Union[None, Plugin]: 插件实例
    """
    if isinstance(plugin_group, type(None)):
        raise ValueError("插件组未初始化读取")
    if isinstance(plugin_group.linked_frame, type(None)):
        raise ValueError("插件组未绑定框架")
    __caches__["plugin"] = None
    __caches__["api_name"] = ""
    try:
        if os.path.isfile(
            os.path.join(
                "插件文件", TOOLDELTA_CLASSIC_PLUGIN, plugin_dirname, "__init__.py"
            )
        ):
            plugin_module = importlib.import_module(plugin_dirname)
            if plugin_module in loaded_plugin_modules:
                importlib.reload(plugin_module)
                mode_str = "重载"
            else:
                loaded_plugin_modules.append(plugin_module)
                mode_str = "载入"
        else:
            Print.print_war(f"{plugin_dirname} 文件夹 未发现插件文件，跳过加载")
            return None
        plugin_or_none: Plugin | None = __caches__.get("plugin")
        if plugin_or_none is None:
            raise NotValidPluginError(
                "需要调用 1 次 @plugins.add_plugin 以注册插件主类，然而没有调用"
            )
        plugin: Plugin = plugin_or_none
        if plugin.name is None or plugin.name == "":
            raise ValueError(f"插件主类 {plugin.__class__.__name__} 需要作者名")
        plugin_group.plugins.append(plugin)
        _v0, _v1, _v2 = plugin.version

        # 收集事件监听函数
        for evt_name in plugins_funcs.keys():
            if hasattr(plugin, evt_name):
                plugins_funcs.setdefault(evt_name, [])
                plugins_funcs[evt_name].append((plugin.name, getattr(plugin, evt_name)))

        # 收集到了需要监听的数据包
        if plugin_group._cached_packet_cbs != []:
            for pktType, func in plugin_group._cached_packet_cbs:
                ins_func = getattr(plugin, func.__name__)
                if ins_func is None:
                    raise NotValidPluginError("数据包监听不能在主插件类以外定义")
                if pktType not in packet_funcs.keys():
                    packet_funcs[pktType] = []
                packet_funcs[pktType].append(ins_func)

        # 监听全部数据包的监听器
        # 实话实说, 这里写的乱糟糟的
        if allpkt_func := plugin_group._cached_all_packets_listener:
            allpkt_func = getattr(plugin, allpkt_func.__name__)
            if allpkt_func is None:
                raise NotValidPluginError("数据包监听不能在主插件类以外定义")

            def make_cached_func(name, pktID_1):
                def _allpkt_listener(pkt):
                    allpkt_func(pktID_1, pkt)

                _allpkt_listener.__name__ = name
                return _allpkt_listener

            for pktID in range(304):
                if pktID in PacketIDS.__dict__.values():
                    if pktID in (PacketIDS.IDPyRpc, 304):
                        continue

                    if pktID not in packet_funcs.keys():
                        packet_funcs[pktID] = []
                    packet_funcs[pktID].append(
                        make_cached_func(allpkt_func.__name__, pktID)
                    )

        # 收集到了作为API的插件
        if __caches__["api_name"] != "":
            plugin_group.plugins_api[__caches__["api_name"]] = plugin

        # 收集到了广播监听器
        if plugin_group._cached_broadcast_evts != {}:
            for evt, funcs in plugin_group._cached_broadcast_evts.items():
                for func in funcs:
                    ins_func = getattr(plugin, func.__name__)
                    if ins_func is None:
                        raise NotValidPluginError("广播事件监听不能在主插件类以外定义")
                    if broadcast_evts_listener.get(evt) is None:
                        broadcast_evts_listener[evt] = []
                    broadcast_evts_listener[evt].append(ins_func)

        Print.print_suc(
            f"已{mode_str}插件 §f{plugin.name}§b@{_v0}.{_v1}.{_v2} §a作者: §r{plugin.author}"
        )
        plugin_group.normal_plugin_loaded_num += 1
        return plugin
    except NotValidPluginError as err:
        Print.print_err(f"插件 {plugin_dirname} 不合法：{err.args[0]}")
        raise SystemExit from err
    except Cfg.ConfigError as err:
        Print.print_err(f"插件 {plugin_dirname} 配置文件报错：{err}")
        Print.print_err(
            "你也可以直接删除配置文件，重新启动 ToolDelta 以自动生成配置文件"
        )
        raise SystemExit from err
    except Utils.SimpleJsonDataReader.DataReadError as err:
        Print.print_err(f"插件 {plugin_dirname} 读取数据失败：{err}")
    except plugin_group.linked_frame.SystemVersionException as err:
        Print.print_err(f"插件 {plugin_dirname} 需要更高版本的 ToolDelta 加载：{err}")
        raise SystemExit
    except Exception as err:
        Print.print_err(f"加载插件 {plugin_dirname} 出现问题，报错如下：")
        Print.print_err("§c" + traceback.format_exc())
        raise SystemExit from err
    finally:
        plugin_group._cached_broadcast_evts.clear()
        plugin_group._cached_packet_cbs.clear()
        plugin_group._cached_all_packets_listener = None
    return None


# 魔法方法执行部分


def _init_frame(frame: "ToolDelta"):
    __caches__["frame"] = frame


def reload():
    """系统调用, 重置所有处理函数"""
    for v in plugins_funcs.values():
        v.clear()
    for v in packet_funcs.values():
        v.clear()


def execute_def(onerr: _ON_ERROR_CB) -> None:
    """执行插件的二次初始化方法

    Args:
        onerr (Callable[[str, Exception, str], None], optional): 插件出错时的处理方法。Defaults to NON_FUNC.

    Raises:
        SystemExit: 缺少前置
        SystemExit: 前置版本过低
    """
    try:
        for name, func in plugins_funcs["on_def"]:
            func()
    except PluginAPINotFoundError as err:
        Print.print_err(f"插件 {name} 需要包含该种接口的前置组件：{err.name}")
        raise SystemExit from err
    except PluginAPIVersionError as err:
        Print.print_err(
            f"插件 {name} 需要该前置组件 {err.name} 版本：{err.m_ver}, 但是现有版本过低：{err.n_ver}"
        )
        raise SystemExit from err
    except Exception as err:
        onerr(name, err, traceback.format_exc())
        raise SystemExit


def execute_init(onerr: _ON_ERROR_CB) -> None:
    """执行插件的连接游戏后初始化方法

    Args:
        onerr (Callable[[str, Exception, str], None], optional): 插件出错时的处理方法
    """
    for name, func in plugins_funcs["on_inject"]:
        try:
            func()
        except Exception as err:
            onerr(name, err, traceback.format_exc())


def execute_player_prejoin(player, onerr: _ON_ERROR_CB) -> None:
    """执行玩家加入前的方法

    Args:
        player (_type_): 玩家
        onerr (Callable[[str, Exception, str], None], optional): 插件出错时的处理方法
    """
    for name, func in plugins_funcs["on_player_prejoin"]:
        try:
            func(player)
        except Exception as err:
            onerr(name, err, traceback.format_exc())


def execute_player_join(player: str, onerr: _ON_ERROR_CB) -> None:
    """执行玩家加入的方法

    Args:
        player (str): 玩家
        onerr (Callable[[str, Exception, str], None], optional): q 插件出错时的处理方法
    """
    for name, func in plugins_funcs["on_player_join"]:
        try:
            func(player)
        except Exception as err:
            onerr(name, err, traceback.format_exc())


def execute_player_message(
    player: str,
    msg: str,
    onerr: _ON_ERROR_CB,
) -> None:
    """执行玩家消息的方法

    Args:
        player (str): 玩家
        msg (str): 消息
        onerr (Callable[[str, Exception, str], None], optional): 插件出错时的处理方法
    """
    pat = f"[{player}] "
    if msg.startswith(pat):
        msg = msg.strip(pat)
    for name, func in plugins_funcs["on_player_message"]:
        try:
            func(player, msg)
        except Exception as err:
            onerr(name, err, traceback.format_exc())


def execute_player_leave(player: str, onerr: _ON_ERROR_CB) -> None:
    """执行玩家离开的方法

    Args:
        player (str): 玩家
        onerr (Callable[[str, Exception, str], None], optional): 插件出错时的处理方法
    """
    for name, func in plugins_funcs["on_player_leave"]:
        try:
            func(player)
        except Exception as err:
            onerr(name, err, traceback.format_exc())


def execute_player_death(
    player: str,
    killer: str | None,
    msg: str,
    onerr: _ON_ERROR_CB,
):
    """执行玩家死亡的方法

    Args:
        player (str): 玩家
        killer (str | None): 击杀者
        msg (str): 消息
        onerr (Callable[[str, Exception, str], None], optional): 插件出错时的处理方法
    """
    for name, func in plugins_funcs["on_player_death"]:
        try:
            func(player, killer, msg)
        except Exception as err:
            onerr(name, err, traceback.format_exc())


def execute_frame_exit(onerr: _ON_ERROR_CB):
    """执行框架退出的方法

    Args:
        onerr (Callable[[str, Exception, str], None], optional): 插件出错时的处理方法
    """
    for name, func in plugins_funcs["on_frame_exit"]:
        try:
            func()
        except Exception as err:
            onerr(name, err, traceback.format_exc())


def execute_reloaded(onerr: _ON_ERROR_CB):
    """执行插件重载的方法

    Args:
        onerr (Callable[[str, Exception, str], None], optional): 插件出错时的处理方法
    """
    for name, func in plugins_funcs["on_reload"]:
        try:
            func()
        except Exception as err:
            onerr(name, err, traceback.format_exc())


def execute_command(
    name: str,
    msg: str,
    onerr: _ON_ERROR_CB,
) -> None:
    """执行命令 say 的方法

    Args:
        player (str): 玩家
        cmd (str): 命令
        onerr (Callable[[str, Exception, str], None], optional): 插件出错时的处理方法
    """
    for plugin_name, func in plugins_funcs["on_command"]:
        try:
            func(plugin_name, msg)
        except Exception as err:
            onerr(plugin_name, err, traceback.format_exc())


def execute_packet_funcs(pktID: int, pkt: dict, onerr: _ON_ERROR_CB) -> bool:
    """处理数据包监听器

    Args:
        pktID (int): 数据包 ID
        pkt (dict): 数据包

    Returns:
        bool: 是否处理成功
    """
    d = packet_funcs.get(pktID)
    if d:
        for func in d:
            try:
                res = func(pkt)
                if res:
                    return True
            except Exception as err:
                onerr("插件方法:" + func.__name__, err, traceback.format_exc())
    return False
