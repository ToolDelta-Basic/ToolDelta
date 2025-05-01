import importlib
import os
import sys
import traceback
from typing import TYPE_CHECKING, TypeVar

from ... import utils
from ...utils import cfg, fmts
from ...constants import (
    TOOLDELTA_PLUGIN_DIR,
    TOOLDELTA_CLASSIC_PLUGIN,
)
from ...version import SystemVersionException
from ..basic import plugin_is_enabled
from ..exceptions import NotValidPluginError
from . import event_cbs
from .plugin_cls import Plugin

if TYPE_CHECKING:
    from ... import ToolDelta
    from ...plugin_load.plugins import PluginGroup

loaded_plugin_modules = []
__cached_frame: "ToolDelta | None" = None

PLUGIN_CLS = TypeVar("PLUGIN_CLS", bound=Plugin)


# TODO: 会存储已删除的插件模块, 可能导致内存泄漏
def plugin_entry(
    plugin_cls: type[PLUGIN_CLS],
    api_name: str | list[str] = [],
    api_version: cfg.VERSION | None = None,
) -> PLUGIN_CLS:
    """
    实例化 ToolDelta 类式插件的主类

    Args:
        plugin_cls (type[Plugin]): 插件主类
        api_name (str | list[str], optional): 如果将插件作为 API 插件, 该参数为 API 名, 可以有多个
        api_version (VERSION, optional): 插件的 API 版本

    Raises:
        NotValidPluginError: 插件主类必须继承 Plugin 类

    Returns:
        Plugin: 插件主类
    """
    global __cached_frame
    try:
        if not Plugin.__subclasscheck__(plugin_cls):
            raise NotValidPluginError(f"插件主类必须继承 Plugin 类 而不是 {plugin_cls}")
    except TypeError as exc:
        raise NotValidPluginError(
            f"插件主类必须继承 Plugin 类 而不是 {plugin_cls.__class__}"
        ) from exc
    if __cached_frame is None:
        help(plugin_cls)
        exit()
    plugin_ins = plugin_cls(__cached_frame)
    if api_name:
        if isinstance(api_name, str):
            plugin_ins._api_names = [api_name]
        else:
            plugin_ins._api_names = api_name
        if api_version:
            plugin_ins._api_ver = api_version
        else:
            plugin_ins._api_ver = plugin_cls.version
    return plugin_ins


def help(plugin: type[Plugin]) -> None:
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


def read_plugins(plugin_grp: "PluginGroup") -> None:
    """
    读取插件

    Args:
        plugin_grp (PluginGroup): 插件组
    """
    PLUGIN_PATH = os.path.join(TOOLDELTA_PLUGIN_DIR, TOOLDELTA_CLASSIC_PLUGIN)
    if PLUGIN_PATH not in sys.path:
        sys.path.append(PLUGIN_PATH)
    event_cbs.broadcast_listener.clear()
    event_cbs.dict_packet_funcs.clear()
    event_cbs.bytes_packet_funcs.clear()
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
                plugin_data = utils.safe_json.safe_json_load(data_path)
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
    global __cached_frame
    if isinstance(plugin_group, type(None)):
        raise ValueError("插件组未初始化读取")
    if isinstance(plugin_group.linked_frame, type(None)):
        raise ValueError("插件组未绑定框架")
    __cached_frame = plugin_group.linked_frame
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
        plugin: Plugin | None = plugin_module.__dict__.get("entry")
        if not isinstance(plugin, Plugin):
            raise NotValidPluginError(
                "没有在最外层代码使用 entry = plugin_entry(YourPlugin) 语句注册插件"
            )
        if plugin.name is None or plugin.name == "":
            raise ValueError(f"插件主类 {plugin.__class__.__name__} 需要插件名")
        if len(plugin.version) != 3:
            raise NotValidPluginError(
                f"插件主类 {plugin.__class__.__name__} 的 version 属性需要是长度为 3 的元组, 如 (0, 0, 1)"
            )
        if plugin._api_names:
            # 此插件应该作为 API 插件
            for api_name in plugin._api_names:
                plugin_group.plugins_api[api_name] = plugin
        version_str = ".".join(map(str, plugin.version))
        plugin._plugin_group = plugin_group
        fmts.print_suc(
            f"已{mode_str}插件 §f{plugin.name}§b@{version_str} §a作者: §r{plugin.author}"
        )
        plugin_group.normal_plugin_loaded_num += 1
        return plugin
    except NotValidPluginError as err:
        fmts.print_err(f"插件 {plugin_dirname} 不合法：{err.args[0]}")
        raise SystemExit from err
    except cfg.ConfigError as err:
        fmts.print_err(f"插件 {plugin_dirname} 配置文件报错：{err}")
        fmts.print_err(
            "你也可以直接删除配置文件，重新启动 ToolDelta 以自动生成配置文件"
        )
        raise SystemExit from err
    except utils.safe_json.DataReadError as err:
        fmts.print_err(f"插件 {plugin_dirname} 读取数据失败：{err}")
    except SystemVersionException as err:
        fmts.print_err(f"插件 {plugin_dirname} 需要更高版本的 ToolDelta 加载：{err}")
        raise SystemExit
    except Exception as err:
        fmts.print_err(f"加载插件 {plugin_dirname} 出现问题，报错如下：")
        fmts.print_err("§c" + traceback.format_exc())
        raise SystemExit from err
    return None
