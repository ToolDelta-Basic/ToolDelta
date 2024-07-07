"ToolDelta 类式插件"

import importlib
import os
import sys
import traceback
from typing import TYPE_CHECKING, Union, TypeVar
from ...color_print import Print
from ...utils import Utils
from ...cfg import Cfg
from ...plugin_load import plugin_is_enabled, NotValidPluginError
from ...constants import TOOLDELTA_CLASSIC_PLUGIN, TOOLDELTA_PLUGIN_DATA_DIR

if TYPE_CHECKING:
    # 类型注释
    from ...frame import ToolDelta
    from ...plugin_load.PluginGroup import PluginGroup

__caches__ = {"plugin": None, "api_name": "", "frame": None}


class Plugin:
    "插件信息主类"

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


_PLUGIN_CLS_TYPE = TypeVar("_PLUGIN_CLS_TYPE")


def add_plugin(plugin: type[_PLUGIN_CLS_TYPE]) -> type[_PLUGIN_CLS_TYPE]:
    """添加ToolDelta类式插件的插件主类

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
        Print.clean_print("§d正在以直接运行模式运行插件..")
        return plugin
    plugin_ins = plugin(__caches__["frame"])  # type: ignore
    __caches__["plugin"] = plugin_ins
    return plugin


def add_plugin_as_api(apiName: str):
    """添加 ToolDelta 类式插件主类，同时作为 API 插件提供接口供其他插件进行使用

    Args:
        apiName (str): API 名
    """

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
    """读取插件

    Args:
        plugin_grp (PluginGroup): 插件组
    """
    PLUGIN_PATH = os.path.join("插件文件", TOOLDELTA_CLASSIC_PLUGIN)
    sys.path.append(os.path.join("插件文件", TOOLDELTA_CLASSIC_PLUGIN))
    for plugin_dir in os.listdir(PLUGIN_PATH):
        if not plugin_is_enabled(plugin_dir):
            continue
        if os.path.isdir(os.path.join(PLUGIN_PATH, plugin_dir)):
            sys.path.append(os.path.join(PLUGIN_PATH, plugin_dir))
            load_plugin(plugin_grp, plugin_dir)
            plugin_grp.loaded_plugins_name.append(plugin_dir)


def load_plugin(
    plugin_group: "PluginGroup", plugin_dirname: str
) -> Union[None, Plugin]:
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
            importlib.import_module(plugin_dirname)
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
        for evt_name in (
            "on_def",
            "on_inject",
            "on_player_prejoin",
            "on_player_join",
            "on_player_message",
            "on_player_death",
            "on_player_leave",
            "on_command",
            "on_frame_exit",
        ):
            if hasattr(plugin, evt_name):
                plugin_group.plugins_funcs[evt_name].append(
                    [plugin.name, getattr(plugin, evt_name)]
                )
        Print.print_suc(
            f"成功载入插件 {plugin.name} 版本：{_v0}.{_v1}.{_v2} 作者：{plugin.author}"
        )
        plugin_group.normal_plugin_loaded_num += 1
        if plugin_group.plugin_added_cache["packets"] != []:
            for pktType, func in plugin_group.plugin_added_cache["packets"]:
                ins_func = getattr(plugin, func.__name__)
                if ins_func is None:
                    raise NotValidPluginError("数据包监听不能在主插件类以外定义")
                plugin_group.add_listen_packet_id(pktType)
                plugin_group.add_listen_packet_func(pktType, ins_func)
        if __caches__["api_name"] != "":
            plugin_group.plugins_api[__caches__["api_name"]] = plugin
        if plugin_group.broadcast_evts_cache != {}:
            for evt, funcs in plugin_group.broadcast_evts_cache.items():
                for func in funcs:
                    ins_func = getattr(plugin, func.__name__)
                    if ins_func is None:
                        raise NotValidPluginError("广播事件监听不能在主插件类以外定义")
                    plugin_group.add_broadcast_evt(evt, ins_func)
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
        plugin_group.plugin_added_cache["packets"].clear()
        plugin_group.broadcast_evts_cache.clear()
    return None


def _init_frame(frame: "ToolDelta"):
    __caches__["frame"] = frame
