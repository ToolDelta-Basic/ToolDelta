import importlib
import os
import sys
import traceback
from tooldelta.color_print import Print
from tooldelta.builtins import Builtins
from tooldelta.cfg import Cfg
from tooldelta.plugin_manager import plugin_manager
from tooldelta.plugin_load.funcs import unzip_plugin
from tooldelta.plugin_load import plugin_is_enabled


class Plugin:
    name = None
    version = (0, 0, 1)
    author = "?"
    description = "..."
    
    @property
    def data_path(self):
        return os.path.join("插件数据文件", self.name)

def read_plugin_from_new(plugin_grp, root_env: dict):
    PLUGIN_PATH = os.path.join(os.getcwd(), "插件文件/ToolDelta组合式插件")
    for plugin_dir in os.listdir(PLUGIN_PATH):
        if not plugin_is_enabled(plugin_dir):
            continue
        if (
            not os.path.isdir(os.path.join(PLUGIN_PATH, plugin_dir.strip(".zip")))
            and os.path.isfile(os.path.join(PLUGIN_PATH, plugin_dir))
            and plugin_dir.endswith(".zip")
        ):
            Print.print_with_info(f"§6正在解压插件{plugin_dir}, 请稍后", "§6 解压 ")
            unzip_plugin(
                os.path.join(PLUGIN_PATH, plugin_dir),
                os.path.join("插件文件/ToolDelta组合式插件", plugin_dir.strip(".zip")),
            )
            Print.print_suc(f"§a成功解压插件{plugin_dir} -> 插件目录")
            plugin_dir = plugin_dir.strip(".zip")
        if os.path.isdir(os.path.join(PLUGIN_PATH, plugin_dir)):
            sys.path.append(os.path.join(PLUGIN_PATH, plugin_dir))
            plugin_grp.plugin_added_cache["plugin"] = None
            plugin_grp.plugin_added_cache["packets"].clear()
            plugin_grp.pluginAPI_added_cache.clear()
            try:
                if os.path.isfile(
                    os.path.join("插件文件/ToolDelta组合式插件", plugin_dir, "__init__.py")
                ):
                    sys.path.append(os.path.join(os.getcwd(), "插件文件", "ToolDelta组合式插件"))
                    # 理论上所有插件共享一个整体环境
                    importlib.__import__(plugin_dir, root_env)
                else:
                    Print.print_war(f"{plugin_dir} 文件夹 未发现插件文件, 跳过加载")
                    continue
                assert plugin_grp.plugin_added_cache["plugin"] is not None, 2
                plugin = plugin_grp.plugin_added_cache["plugin"]
                if plugin.name == None:
                    raise ValueError(f"插件主类 {plugin.__name__} 需要作者名")
                plugin_body: Plugin = plugin(plugin_grp.linked_frame)
                plugin_grp.plugins.append([plugin_body.name, plugin_body])
                _v0, _v1, _v2 = plugin_body.version  # type: ignore
                if hasattr(plugin_body, "on_def"):
                    plugin_grp.plugins_funcs["on_def"].append(
                        [plugin_body.name, plugin_body.on_def]
                    )
                if hasattr(plugin_body, "on_inject"):
                    plugin_grp.plugins_funcs["on_inject"].append(
                        [plugin_body.name, plugin_body.on_inject]
                    )
                if hasattr(plugin_body, "on_player_prejoin"):
                    plugin_grp.plugins_funcs["on_player_prejoin"].append(
                        [plugin_body.name, plugin_body.on_player_prejoin]
                    )
                if hasattr(plugin_body, "on_player_join"):
                    plugin_grp.plugins_funcs["on_player_join"].append(
                        [plugin_body.name, plugin_body.on_player_join]
                    )
                if hasattr(plugin_body, "on_player_message"):
                    plugin_grp.plugins_funcs["on_player_message"].append(
                        [plugin_body.name, plugin_body.on_player_message]
                    )
                if hasattr(plugin_body, "on_player_death"):
                    plugin_grp.plugins_funcs["on_player_death"].append(
                        [plugin_body.name, plugin_body.on_player_death]
                    )
                if hasattr(plugin_body, "on_player_leave"):
                    plugin_grp.plugins_funcs["on_player_leave"].append(
                        [plugin_body.name, plugin_body.on_player_leave]
                    )
                Print.print_suc(
                    f"成功载入插件 {plugin_body.name} 版本: {_v0}.{_v1}.{_v2} 作者：{plugin_body.author}"
                )
                plugin_grp.normal_plugin_loaded_num += 1
                if plugin_grp.plugin_added_cache["packets"] != []:
                    for pktType, func in plugin_grp.plugin_added_cache["packets"]:  # type: ignore
                        plugin_grp.add_listen_packet_id(pktType)
                        plugin_grp.add_listen_packet_func(
                            pktType, getattr(plugin_body, func.__name__)
                        )
                if plugin_grp.pluginAPI_added_cache is not None:
                    for _api in plugin_grp.pluginAPI_added_cache:
                        if isinstance(_api, str):
                            plugin_grp.plugins_api[_api] = plugin_body
                        else:
                            (apiName, api) = _api
                            plugin_grp.plugins_api[apiName] = api(
                                plugin_grp.linked_frame
                            )
                # 自动注册插件到插件管理器
                plugin_manager.test_name_same(plugin_body.name, plugin_dir)
                if not plugin_manager.plugin_is_registered("classic", plugin_body.name):
                    plugin_manager.auto_register_plugin("classic", plugin_body)
            except AssertionError as err:
                if err.args[0] == 2:
                    Print.print_err(
                        f"插件 {plugin_dir} 不合法: 只能调用一次 @plugins.add_plugin, 实际调用了0次或多次"
                    )
                    raise SystemExit
                elif isinstance(err.args[0], int):
                    Print.print_err(f"插件 {plugin_dir} 不合法: {err.args[1]}")
                    raise SystemExit
                if len(err.args[0]) == 2:
                    Print.print_err(f"插件 {plugin_dir} 不合法: {err.args[0][1]}")
                    raise SystemExit
                raise
            except Cfg.ConfigError as err:
                Print.print_err(f"插件 {plugin_dir} 配置文件报错：{err}")
                Print.print_err("你也可以直接删除配置文件, 重新启动ToolDelta以自动生成配置文件")
                raise SystemExit
            except Builtins.SimpleJsonDataReader.DataReadError as err:
                Print.print_err(f"插件 {plugin_dir} 读取数据失败: {err}")
            except plugin_grp.linked_frame.SystemVersionException:
                Print.print_err(f"插件 {plugin_dir} 需要更高版本的ToolDelta加载: {err}")
            except Exception as err:
                if "() takes no arguments" in str(err):
                    Print.print_err(f"插件 {plugin_dir} 不合法： 主类初始化时应接受 1 个参数: Frame")
                else:
                    Print.print_err(f"加载插件 {plugin_dir} 出现问题, 报错如下: ")
                    Print.print_err("§c" + traceback.format_exc())
                    raise SystemExit
