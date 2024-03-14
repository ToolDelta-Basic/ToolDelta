import requests
import json
import os
import platform
import shutil
import tempfile
import traceback
import time
from tooldelta import urlmethod
from tooldelta.builtins import Builtins
from tooldelta.color_print import Print
from tooldelta.plugin_load import PluginRegData
from tooldelta.cfg import Cfg
from tooldelta.constants import (
    PLUGIN_MARKET_SOURCE_OFFICIAL,
    TOOLDELTA_CLASSIC_PLUGIN,
    TOOLDELTA_DOTCSEMU_PLUGIN,
    TOOLDELTA_INJECTED_PLUGIN
)
from typing import Dict

if platform.system().lower() == "windows":
    CLS_CMD = "cls"
else:
    CLS_CMD = "clear"

clear_screen = lambda: os.system(CLS_CMD)


def _path_dir(path: str):
    if "/" not in path:
        return None
    return "/".join(path.split("/")[:-1])


def _url_join(*urls):
    return "/".join(urls)


def _get_json_from_url(url: str):
    try:
        resp = requests.get(url).text
    except requests.RequestException:
        raise Exception("URL请求失败")
    try:
        return json.loads(resp)
    except json.JSONDecodeError:
        raise Exception(f"服务器返回了不正确的答复: {resp}")


class PluginMarket:
    def enter_plugin_market(self, source_url: str = None, in_game = False):
        Print.clean_print("§6正在连接到插件市场..")
        try:
            market_datas = self.get_datas_from_market(source_url)
            plugins_list = list(market_datas["MarketPlugins"].items())
            all_indexes = len(plugins_list)
            now_index = 0
            sum_pages = int((all_indexes - 1) / 8) + 1
            now_page = 0
            last_operation = ""
            while True:
                clear_screen()
                Print.print_inf(
                    market_datas["SourceName"] + ": " + market_datas["Greetings"],
                    need_log=False
                )
                now_page = int(now_index / 8) + 1
                for i in range(now_index, now_index + 8):
                    if i in range(all_indexes):
                        plugin_data = PluginRegData(
                            plugins_list[i][0], plugins_list[i][1]
                        )
                        Print.print_inf(
                            f" {i + 1}. §e{plugin_data.name} §av{plugin_data.version_str} §b@{plugin_data.author} §d{plugin_data.plugin_type_str}插件",
                            need_log=False
                        )
                    else:
                        Print.print_inf("")
                Print.print_inf(f"§f第 {now_page} / {sum_pages} 页, 输入 §b+§f/§b- §f翻页", need_log=False)
                Print.print_inf("§f输入插件序号选中插件并查看其下载页", need_log=False)
                last_operation = (
                    (
                        input(Print.fmt_info("§f回车键继续上次操作, §bq§f退出, 请输入:", "§f 输入 "))
                        or last_operation
                    )
                    .lower()
                    .strip()
                )
                if last_operation == "+":
                    now_index += 8
                elif last_operation == "-":
                    now_index -= 8
                elif last_operation == "q":
                    break
                else:
                    res = Builtins.try_int(last_operation)
                    if res:
                        if res in range(1, all_indexes + 1):
                            plugin_data = PluginRegData(
                                plugins_list[res - 1][0], plugins_list[res - 1][1]
                            )
                            ok, pres = self.choice_plugin(
                                plugin_data,
                                market_datas["MarketPlugins"],
                            )
                            if ok:
                                if in_game:
                                    from tooldelta.plugin_load.PluginGroup import plugin_group
                                    if plugin_data.name not in plugin_group.loaded_plugins_name:
                                        resp = input(
                                            Print.fmt_info(f"§f可以直接热加载该插件: {plugin_data.name}, 是否加载(§aY§f/§cN§f): ")
                                        ).strip().lower()
                                        if resp == "y":
                                            for i in pres:
                                                if i not in plugin_group.loaded_plugins_name:
                                                    try:
                                                        plugin_group.load_plugin_hot(i.name, i.plugin_type)
                                                    except BaseException as err:
                                                        Print.print_err(f"插件热加载出现问题: {err}")
                                    else:
                                        Print.print_inf("插件已存在, 若要更新版本, 请重启 ToolDelta", need_log=False)
                                        r = input(Print.fmt_info("§f输入 §cq §f退出, 其他则返回插件市场"))
                                else:
                                    Print.print_inf("下载插件后重启ToolDelta才能生效", need_log=False)
                                r = input(Print.fmt_info("§f输入 §cq §f退出, 其他则返回插件市场"))
                                if r.lower() == "q":
                                    break
                            else:
                                Print.print_inf("已取消.", need_log=False)
                                time.sleep(1)
                        else:
                            Print.print_err("超出序号范围")
                if now_index >= all_indexes:
                    now_index = 0
                elif now_index < 0:
                    now_index = max(all_indexes - 8, 0)
        except KeyError as err:
            Print.print_err(f"获取插件市场插件出现问题: 键值对错误: {err}")
            return
        except requests.RequestException as err:
            Print.print_err(f"获取插件市场插件出现问题: {err}")
            return
        except Exception as err:
            Print.print_err(f"获取插件市场插件出现问题")
            Print.print_err(traceback.format_exc())
            return
        clear_screen()
        Print.clean_print("§a已从插件市场返回 ToolDelta 控制台.")

    def get_datas_from_market(self, source_url: str = None):
        if source_url is None:
            source_url = Cfg().get_cfg("ToolDelta基本配置.json", {"插件市场源": str})["插件市场源"]
        market_datas = _get_json_from_url(
            _url_join(source_url, "market_tree.json")
        )
        self.plugins_download_url = market_datas["DownloadRefURL"]
        return market_datas

    def choice_plugin(self, plugin_data: PluginRegData, all_plugins_dict: dict):
        pre_plugins_str = (
            ", ".join([f"{k}§7v{v}" for k, v in plugin_data.pre_plugins.items()]) or "无"
        )
        clear_screen()
        Print.print_inf(
            f"{plugin_data.name} v{plugin_data.version_str}", need_log=False
        )
        Print.print_inf(
            f"作者: §f{plugin_data.author}§7, 版本: §f{plugin_data.version_str} §b{plugin_data.plugin_type_str}",
            need_log=False,
        )
        Print.print_inf(f"前置插件: §f{pre_plugins_str}", need_log=False)
        Print.print_inf(f"介绍: {plugin_data.description}", need_log=False)
        Print.print_inf("", need_log=False)
        res = input(Print.fmt_info("§f下载 = §aY§f, 取消 = §cN§f, 请输入:")).lower().strip()
        if res == "y":
            pres = self.download_plugin(plugin_data, all_plugins_dict)
            pres.reverse()
            return True, pres
        return False, None

    def download_plugin(
        self,
        plugin_data: PluginRegData,
        all_plugins_dict: Dict[str, str],
    ):
        pres = [plugin_data]
        download_paths = self.find_dirs(plugin_data)
        for plugin_name in plugin_data.pre_plugins:
            Print.print_inf(f"正在下载 {plugin_data.name} 的前置插件 {plugin_name}")
            pres += self.download_plugin(
                PluginRegData(plugin_name, all_plugins_dict[plugin_name]),
                all_plugins_dict,
            )
        cache_dir = tempfile.mkdtemp()
        try:
            for paths in download_paths:
                if not paths.strip():
                    # 不可能出现的状况, 出现了证明是你的问题
                    Print.print_war("下载路径为空, 跳过")
                    continue
                url = _url_join(self.plugins_download_url, paths)
                # Determine download path based on plugin type
                match plugin_data.plugin_type:
                    case "classic":
                        download_path = os.path.join(
                            "插件文件", TOOLDELTA_CLASSIC_PLUGIN
                        )
                    case "dotcs":
                        download_path = os.path.join(
                            "插件文件", TOOLDELTA_DOTCSEMU_PLUGIN
                        )
                    case "injected":
                        download_path = os.path.join(
                            "插件文件", TOOLDELTA_INJECTED_PLUGIN
                        )
                    case _:
                        raise Exception(
                            f"未知插件类型: {plugin_data.plugin_type}, 你可能需要通知ToolDelta项目开发组解决"
                        )
                os.makedirs(os.path.join(cache_dir, plugin_data.name), exist_ok=True)
                path_last = _path_dir(paths)
                if path_last is not None:
                    # 自动创建文件夹
                    folder_path = os.path.join(cache_dir, path_last)
                    os.makedirs(folder_path, exist_ok=True)
                urlmethod.download_unknown_file(url, os.path.join(cache_dir, paths))
            # Move downloaded files to target download path
            target_path = download_path
            os.makedirs(target_path, exist_ok=True)
            for root, _, files in os.walk(cache_dir):
                for filename in files:
                    source_file = os.path.join(root, filename)
                    target_file = os.path.join(
                        target_path, os.path.relpath(source_file, cache_dir)
                    )
                    os.makedirs(os.path.dirname(target_file), exist_ok=True)
                    shutil.move(source_file, target_file)
            from tooldelta.plugin_manager import plugin_manager
            # 注册插件
            plugin_manager.push_plugin_reg_data(PluginRegData(
                plugin_data.name, all_plugins_dict[plugin_data.name]
            ))
            Print.clean_print(f"§a成功下载插件 §f{plugin_data.name}§a 至插件文件夹")
        finally:
            shutil.rmtree(cache_dir)
        return pres

    def find_dirs(self, plugin_data: PluginRegData):
        try:
            data = _get_json_from_url(
                _url_join(self.plugins_download_url, "directory.json")
            )
            data_list = []
            for folder, files in data.items():
                if plugin_data.name == folder.split("/")[0]:
                    # 展开
                    for file in files:
                        data_list.append(folder + r"/" + file)
            return data_list
        except KeyError as err:
            Print.print_err(f"获取插件市场插件目录结构出现问题: 无法找到 {err}, 有可能是未来得及更新目录")
            return
        except Exception as err:
            Print.print_err(f"获取插件市场插件目录结构出现问题: {err}")
            return

    @staticmethod
    def get_latest_plugin_version(plugin_type: str, plugin_name: str):
        try:
            src_url = Cfg().get_cfg("ToolDelta基本配置.json", {"插件市场源": str})["插件市场源"]
        except:
            src_url = PLUGIN_MARKET_SOURCE_OFFICIAL
        return _get_json_from_url(
            _url_join(src_url, "latest_versions.json")
        )[plugin_type + "_plugin"].get(plugin_name)

market = PluginMarket()
