"ToolDelta类式插件"
import importlib
import os
import sys
import traceback
import zipfile
from typing import TYPE_CHECKING, Callable, Union
from ...color_print import Print
from ...utils import Utils
from ...cfg import Cfg
from ...plugin_load import plugin_is_enabled, NotValidPluginError
from ...constants import TOOLDELTA_CLASSIC_PLUGIN

if TYPE_CHECKING:
    # 类型注释
    from ...frame import Frame
    from ...plugin_load.PluginGroup import PluginGroup

class Plugin:
    "插件信息主类"
    name: str = ""
    version = (0, 0, 1)
    author = "?"
    description = "..."

    def __init__(self, frame: "Frame"):
        self.frame = frame
        self.game_ctrl = frame.get_game_control()

    @property
    def data_path(self) -> str:
        "该插件的数据文件夹路径 (调用时直接创建数据文件夹)"
        path = os.path.join("插件数据文件", self.name)
        os.makedirs(path, exist_ok=True)
        return path

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
        if (
            not os.path.isdir(os.path.join(
                PLUGIN_PATH, plugin_dir.strip(".zip")))
            and os.path.isfile(os.path.join(PLUGIN_PATH, plugin_dir))
            and plugin_dir.endswith(".zip")
        ):
            Print.print_with_info(f"§6正在解压插件{plugin_dir}, 请稍后", "§6 解压 ")
            _unzip_plugin(
                os.path.join(PLUGIN_PATH, plugin_dir),
                os.path.join(PLUGIN_PATH, plugin_dir.strip(".zip")),
            )
            Print.print_suc(f"§a成功解压插件{plugin_dir} -> 插件目录")
            plugin_dir = plugin_dir.strip(".zip")
        if os.path.isdir(os.path.join(PLUGIN_PATH, plugin_dir)):
            sys.path.append(os.path.join(PLUGIN_PATH, plugin_dir))
            load_plugin(plugin_grp, plugin_dir)
            plugin_grp.loaded_plugins_name.append(plugin_dir)


def load_plugin(plugin_group: "PluginGroup", plugin_dirname: str) -> Union[None, Plugin]:
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
    plugin_grp = plugin_group
    if isinstance(plugin_grp, type(None)):
        raise ValueError("插件组未初始化读取")
    if isinstance(plugin_grp.linked_frame, type(None)):
        raise ValueError("插件组未绑定框架")
    try:
        if os.path.isfile(
            os.path.join(
                "插件文件", TOOLDELTA_CLASSIC_PLUGIN, plugin_dirname, "__init__.py"
            )
        ):
            importlib.__import__(plugin_dirname)
        else:
            Print.print_war(f"{plugin_dirname} 文件夹 未发现插件文件, 跳过加载")
            return
        Utils.simpleAssert(
            plugin_grp.plugin_added_cache["plugin"] is not None,
            NotValidPluginError(
                "需要调用1次 @plugins.add_plugin 以注册插件主类, 然而没有调用"
            ),
        )
        plugin: type[Plugin] = plugin_grp.plugin_added_cache["plugin"]
        if plugin.name is None:
            raise ValueError(f"插件主类 {plugin.__name__} 需要作者名")
        plugin_ins = plugin(plugin_grp.linked_frame)
        if isinstance(plugin_ins, type(None)) or plugin_ins.name == "":
            raise ValueError(f"插件主类 {plugin.__name__} 需要作者名")
        plugin_grp.plugins.append([plugin_ins.name, plugin_ins])
        _v0, _v1, _v2 = plugin_ins.version
        for evt_name in (
            "on_def",
            "on_inject",
            "on_player_prejoin",
            "on_player_join",
            "on_player_message",
            "on_player_death",
            "on_player_leave",
            "on_frame_exit"
        ):
            if hasattr(plugin_ins, evt_name):
                plugin_grp.plugins_funcs[evt_name].append(
                    [plugin_ins.name, getattr(plugin_ins, evt_name)]
                )
        Print.print_suc(
            f"成功载入插件 {plugin_ins.name} 版本: {_v0}.{_v1}.{_v2} 作者：{plugin_ins.author}"
        )
        plugin_grp.normal_plugin_loaded_num += 1
        if plugin_grp.plugin_added_cache["packets"] != []:
            for pktType, func in plugin_grp.plugin_added_cache["packets"]:
                pfunc = getattr(plugin_ins, func.__name__)
                if pfunc is None:
                    raise NotValidPluginError("数据包监听不能在主插件类以外定义")
                plugin_grp._add_listen_packet_id(pktType)
                plugin_grp._add_listen_packet_func(
                    pktType, pfunc
                )
        if plugin_grp.pluginAPI_added_cache is not None:
            for _api in plugin_grp.pluginAPI_added_cache:
                if isinstance(_api, str):
                    plugin_grp.plugins_api[_api] = plugin_ins
                else:
                    (apiName, api) = _api
                    plugin_grp.plugins_api[apiName] = api(
                        plugin_grp.linked_frame)
        if plugin_grp.broadcast_evts_cache != {}:
            for evt, funcs in plugin_grp.broadcast_evts_cache.items():
                for func in funcs:
                    bfunc = getattr(plugin_ins, func.__name__)
                    if bfunc is not None:
                        # 在插件主类以内定义了广播接收器
                        func = bfunc
                    plugin_grp._add_broadcast_evt(evt, func)
        return plugin_ins
    except NotValidPluginError as err:
        Print.print_err(f"插件 {plugin_dirname} 不合法: {err.args[0]}")
        raise SystemExit from err
    except Cfg.ConfigError as err:
        Print.print_err(f"插件 {plugin_dirname} 配置文件报错：{err}")
        Print.print_err("你也可以直接删除配置文件, 重新启动ToolDelta以自动生成配置文件")
        raise SystemExit from err
    except Utils.SimpleJsonDataReader.DataReadError as err:
        Print.print_err(f"插件 {plugin_dirname} 读取数据失败: {err}")
    except plugin_grp.linked_frame.SystemVersionException as err:
        Print.print_err(f"插件 {plugin_dirname} 需要更高版本的ToolDelta加载: {err}")
    except Exception as err:
        Print.print_err(f"加载插件 {plugin_dirname} 出现问题, 报错如下: ")
        Print.print_err("§c" + traceback.format_exc())
        raise SystemExit from err
    finally:
        plugin_grp.plugin_added_cache["plugin"] = None
        plugin_grp.plugin_added_cache["packets"].clear()
        plugin_grp.pluginAPI_added_cache.clear()
        plugin_grp.broadcast_evts_cache.clear()
    return None

def _unzip_plugin(zip_dir: str, exp_dir: str) -> None:
    """解压插件ZIP包

    Args:
        zip_dir (str): 压缩文件路径
        exp_dir (str): 解压目录
    """
    try:
        f = zipfile.ZipFile(zip_dir, "r")
        f.extractall(exp_dir)
    except Exception as err:
        Print.print_err(f"zipfile: 解压失败: {err}")
        raise EOFError("解压失败") from err