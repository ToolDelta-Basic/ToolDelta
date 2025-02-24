import importlib
import os
import sys
import traceback
from typing import TYPE_CHECKING, TypeVar, Any
from collections.abc import Callable

from tooldelta.cfg import Cfg
from tooldelta.color_print import fmts
from tooldelta.utils import Utils
from tooldelta.constants import (
    TOOLDELTA_PLUGIN_DIR,
    TOOLDELTA_CLASSIC_PLUGIN,
    PacketIDS,
)
from ..basic import plugin_is_enabled
from ..exceptions import NotValidPluginError, SystemVersionException
from . import event_cbs
from .plugin_cls import Plugin

if TYPE_CHECKING:
    from tooldelta.plugin_load.plugins import PluginGroup

_PLUGIN_CLS_TYPE = TypeVar("_PLUGIN_CLS_TYPE")
_SUPER_CLS = TypeVar("_SUPER_CLS")
_TV = TypeVar("_TV")
loaded_plugin_modules = []

__caches__ = {"plugin": None, "api_name": "", "frame": None}
_cached_broadcast_evts: dict[str, list[Callable]] = {}
_cached_packet_cbs: list[tuple[int, Callable]] = []
_cached_all_packets_listener: Callable | None = None


# -------------------------- OLD -------------------------


# TODO: 会存储已删除的插件模块, 可能导致内存泄漏
def add_plugin(plugin: type[_PLUGIN_CLS_TYPE]) -> type[_PLUGIN_CLS_TYPE]:
    """
    添加ToolDelta类式插件的插件主类

    Args:
        plugin (type[Plugin]): 插件主类

    Raises:
        NotValidPluginError: 插件主类必须继承 Plugin 类

    Returns:
        type[Plugin]: 插件主类
    """
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
        fmts.clean_print("§d正在以直接运行模式运行插件..")
        return plugin
    plugin_ins = plugin(__caches__["frame"])  # type: ignore
    __caches__["plugin"] = plugin_ins
    return plugin


def add_plugin_as_api(apiName: str):
    """
    添加 ToolDelta 类式插件主类，同时作为 API 插件提供接口供其他插件进行使用

    Args:
        apiName (str): API 名
    """

    def _add_plugin_2_api(api_plugin: type[_PLUGIN_CLS_TYPE]) -> type[_PLUGIN_CLS_TYPE]:
        if not Plugin.__subclasscheck__(api_plugin):
            raise NotValidPluginError("API 插件主类必须继承 Plugin 类")
        if __caches__["plugin"] is not None:
            raise NotValidPluginError("调用了多次 @add_plugin")
        if __caches__["frame"] is None:
            fmts.clean_print("§d正在以直接运行模式运行插件..")
            return api_plugin
        plugin_ins = api_plugin(__caches__["frame"])  # type: ignore
        __caches__["plugin"] = plugin_ins
        __caches__["api_name"] = apiName
        return api_plugin

    return _add_plugin_2_api


def help(plugin: Plugin) -> None:
    """
    查看插件帮助.
    常用于查看 get_plugin_api() 方法获取到的插件实例的帮助.
    """
    plugin_docs = "<plugins.help>: " + plugin.name + "开放的 API 接口说明:\n"
    for attr_name, attr in plugin.__dict__.items():
        if not attr_name.startswith("__") and attr.__doc__ is not None:
            plugin_docs += (
                "\n §a" + attr_name + ":§f\n    " + attr.__doc__.replace("\n", "\n    ")
            )
    fmts.clean_print(plugin_docs)


# Plugin get and execute


def read_plugins(plugin_grp: "PluginGroup") -> None:
    """
    读取插件

    Args:
        plugin_grp (PluginGroup): 插件组
    """
    global _cached_all_packets_listener
    PLUGIN_PATH = os.path.join(TOOLDELTA_PLUGIN_DIR, TOOLDELTA_CLASSIC_PLUGIN)
    if PLUGIN_PATH not in sys.path:
        sys.path.append(PLUGIN_PATH)
    event_cbs.broadcast_listener.clear()
    event_cbs.packet_funcs.clear()
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
    global _cached_all_packets_listener
    if isinstance(plugin_group, type(None)):
        raise ValueError("插件组未初始化读取")
    if isinstance(plugin_group.linked_frame, type(None)):
        raise ValueError("插件组未绑定框架")
    __caches__["frame"] = plugin_group.linked_frame
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
            fmts.print_war(f"{plugin_dirname} 文件夹 未发现插件文件，跳过加载")
            return None
        plugin_or_none: Plugin | None = __caches__.get("plugin")
        if plugin_or_none is None:
            raise NotValidPluginError(
                "需要调用 1 次 @plugins.add_plugin 以注册插件主类，然而没有调用"
            )
        plugin: Plugin = plugin_or_none
        if plugin.name is None or plugin.name == "":
            raise ValueError(f"插件主类 {plugin.__class__.__name__} 需要作者名")
        _v0, _v1, _v2 = plugin.version

        # 收集事件监听函数
        for evt_name in event_cbs.plugins_funcs.keys():
            if hasattr(plugin, evt_name):
                event_cbs.plugins_funcs.setdefault(evt_name, [])
                event_cbs.plugins_funcs[evt_name].append(
                    (plugin.name, getattr(plugin, evt_name))
                )

        # 收集到了需要监听的数据包
        if _cached_packet_cbs != []:
            for pktType, func in _cached_packet_cbs:
                ins_func = getattr(plugin, func.__name__)
                if ins_func is None:
                    raise NotValidPluginError("数据包监听不能在主插件类以外定义")
                if pktType not in event_cbs.packet_funcs.keys():
                    event_cbs.packet_funcs[pktType] = []
                event_cbs.packet_funcs[pktType].append(ins_func)

        # 监听全部数据包的监听器
        # 实话实说, 这里写的乱糟糟的
        if allpkt_func := _cached_all_packets_listener:
            allpkt_func = getattr(plugin, allpkt_func.__name__)
            if allpkt_func is None:
                raise NotValidPluginError("数据包监听不能在主插件类以外定义")

            def make_cached_func(name, pktID_1):
                def _allpkt_listener(pkt):
                    allpkt_func(pktID_1, pkt)
                    return False

                _allpkt_listener.__name__ = name
                return _allpkt_listener

            for pktID in range(304):
                if pktID in PacketIDS.__dict__.values():
                    if pktID in (PacketIDS.IDPyRpc, 304):
                        continue

                    if pktID not in event_cbs.packet_funcs.keys():
                        event_cbs.packet_funcs[pktID] = []
                    event_cbs.packet_funcs[pktID].append(
                        make_cached_func(allpkt_func.__name__, pktID)
                    )

        # 收集到了作为API的插件
        if __caches__["api_name"] != "":
            plugin_group.plugins_api[__caches__["api_name"]] = plugin

        # 收集到了广播监听器
        if _cached_broadcast_evts != {}:
            for evt, funcs in _cached_broadcast_evts.items():
                for func in funcs:
                    ins_func = getattr(plugin, func.__name__)
                    if ins_func is None:
                        raise NotValidPluginError("广播事件监听不能在主插件类以外定义")
                    if event_cbs.broadcast_listener.get(evt) is None:
                        event_cbs.broadcast_listener[evt] = []
                    event_cbs.broadcast_listener[evt].append(ins_func)

        fmts.print_suc(
            f"已{mode_str}插件 §f{plugin.name}§b@{_v0}.{_v1}.{_v2} §a作者: §r{plugin.author}"
        )
        plugin_group.normal_plugin_loaded_num += 1
        return plugin
    except NotValidPluginError as err:
        fmts.print_err(f"插件 {plugin_dirname} 不合法：{err.args[0]}")
        raise SystemExit from err
    except Cfg.ConfigError as err:
        fmts.print_err(f"插件 {plugin_dirname} 配置文件报错：{err}")
        fmts.print_err(
            "你也可以直接删除配置文件，重新启动 ToolDelta 以自动生成配置文件"
        )
        raise SystemExit from err
    except Utils.SimpleJsonDataReader.DataReadError as err:
        fmts.print_err(f"插件 {plugin_dirname} 读取数据失败：{err}")
    except SystemVersionException as err:
        fmts.print_err(f"插件 {plugin_dirname} 需要更高版本的 ToolDelta 加载：{err}")
        raise SystemExit
    except Exception as err:
        fmts.print_err(f"加载插件 {plugin_dirname} 出现问题，报错如下：")
        fmts.print_err("§c" + traceback.format_exc())
        raise SystemExit from err
    finally:
        _cached_broadcast_evts.clear()
        _cached_packet_cbs.clear()
        _cached_all_packets_listener = None
    return None


# 向下兼容
# 已经废弃


def add_packet_listener(pktID: int | list[int]):
    def deco(func: Callable[[_SUPER_CLS, dict], bool]):
        # 存在缓存区, 等待 class_plugin 实例化
        if pktID == -1:
            for n, i in PacketIDS.__dict__.items():
                if n[0].isupper():
                    _cached_packet_cbs.append((i, func))
        elif isinstance(pktID, int):
            _cached_packet_cbs.append((pktID, func))
        else:
            for i in pktID:
                _cached_packet_cbs.append((i, func))
        return func

    return deco


def add_any_packet_listener(func: Callable[[_SUPER_CLS, int, dict], bool]):
    global _cached_all_packets_listener
    _cached_all_packets_listener = func
    return func


def add_broadcast_listener(evt_name: str):
    def deco(
        func: Callable[[_SUPER_CLS, _TV], Any],
    ) -> Callable[[_SUPER_CLS, _TV], Any]:
        # 存在缓存区, 等待 class_plugin 实例化
        if _cached_broadcast_evts.get(evt_name):
            _cached_broadcast_evts[evt_name].append(func)
        else:
            _cached_broadcast_evts[evt_name] = [func]
        return func

    return deco
