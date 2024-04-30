"插件市场客户端"
import os
import platform
import shutil
import tempfile
import traceback
import time
import shlex
import requests
import ujson as json
from tooldelta import urlmethod
from .utils import Utils
from .color_print import Print
from .plugin_load import PluginRegData
from .cfg import Cfg
from .constants import (
    PLUGIN_MARKET_SOURCE_OFFICIAL,
    TOOLDELTA_CLASSIC_PLUGIN,
    TOOLDELTA_INJECTED_PLUGIN
)
from .plugin_load.PluginGroup import plugin_group

if platform.system().lower() == "windows":
    CLS_CMD = "cls"
else:
    CLS_CMD = "clear"


def clear_screen() -> None:
    "清屏"
    os.system(shlex.quote(CLS_CMD))


def path_dir(path: str) -> str | None:
    """获取路径的上一级目录

    Args:
        path (str): 路径

    Returns:
        str|None: 上一级目录
    """
    if "/" not in path:
        return None
    return "/".join(path.split("/")[:-1])


def url_join(*urls) -> str:
    """连接URL

    Returns:
        str: 连接后的URL
    """
    return "/".join(urls)


def get_json_from_url(url: str) -> dict:
    """从URL获取JSON数据

    Args:
        url (str): URL

    Raises:
        requests.RequestException: Url请求失败
        requests.RequestException: 服务器返回了不正确的答复

    Returns:
        dict: JSON数据
    """
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        resptext = resp.text
    except requests.RequestException as exc:
        raise requests.RequestException("URL请求失败") from exc
    try:
        return json.loads(resptext)
    except json.JSONDecodeError as exc:
        raise requests.RequestException(f"服务器返回了不正确的答复: {resptext}") from exc


class PluginMarket:
    "插件市场类"

    def __init__(self):
        try:
            self.plugins_download_url = Cfg().get_cfg(
                "ToolDelta基本配置.json", {"插件市场源": str})["插件市场源"]
        except Exception:
            self.plugins_download_url = PLUGIN_MARKET_SOURCE_OFFICIAL
        self.plugin_id_name_map: dict = self.get_plugin_id_name_map()

    def enter_plugin_market(self, source_url: str | None = None, in_game=False) -> None:
        """进入插件市场

        Args:
            source_url (str | None, optional): 插件市场源
            in_game (bool, optional): 是否在游戏内
        """
        Print.clean_print("§6正在连接到插件市场..")
        CTXS = 12
        try:
            if isinstance(source_url, str):
                market_datas = self.get_datas_from_market(source_url)
            market_datas = self.get_datas_from_market()
            plugin_ids_map = self.plugin_id_name_map
            plugins_list = list(market_datas["MarketPlugins"].items())
            all_indexes = len(plugins_list)
            now_index = 0
            sum_pages = int((all_indexes - 1) / CTXS) + 1
            now_page = 0
            last_operation = ""
            while True:
                clear_screen()
                Print.print_inf(
                    market_datas["SourceName"] + ": " +
                    market_datas["Greetings"],
                    need_log=False
                )
                now_page = int(now_index / CTXS) + 1
                for i in range(now_index, now_index + CTXS):
                    if i in range(all_indexes):
                        plugin_id = plugins_list[i][0]
                        plugin_name = plugin_ids_map[plugin_id]
                        plugin_basic_datas = plugins_list[i][1]
                        if plugin_basic_datas['plugin-type'] == "classic":
                            plugin_type = "类式"
                        elif plugin_basic_datas['plugin-type'] == "injected":
                            plugin_type = "注入式"
                        else:
                            plugin_type = plugin_basic_datas['plugin-type']
                        Print.print_inf(
                            f" {i + 1}. §e{plugin_name} §av{plugin_basic_datas['version']} §b@{plugin_basic_datas['author']} §d{plugin_type}插件",
                            need_log=False
                        )
                    else:
                        Print.print_inf("")
                Print.print_inf(
                    f"§f第 {now_page} / {sum_pages} 页, 输入 §b+§f/§b- §f翻页", need_log=False)
                Print.print_inf("§f输入插件序号选中插件并查看其下载页", need_log=False)
                last_operation = (
                    (
                        input(Print.fmt_info(
                            "§f回车键继续上次操作, §bq§f退出, 请输入:", "§f 输入 "))
                        or last_operation
                    )
                    .lower()
                    .strip()
                )
                if last_operation == "+":
                    now_index += CTXS
                elif last_operation == "-":
                    now_index -= CTXS
                elif last_operation == "q":
                    break
                else:
                    res = Utils.try_int(last_operation)
                    if res:
                        if res in range(1, all_indexes + 1):
                            plugin_data = self.get_plugin_data_from_market(
                                plugins_list[res - 1][0])
                            ok, pres = self.choice_plugin(plugin_data)
                            if ok:
                                if in_game:
                                    if plugin_data.name not in plugin_group.loaded_plugins_name:
                                        resp = input(
                                            Print.fmt_info(
                                                f"§f可以直接热加载该插件: {plugin_data.name}, 是否加载(§aY§f/§cN§f): ")
                                        ).strip().lower()
                                        if resp == "y":
                                            for i in pres:
                                                if i not in plugin_group.loaded_plugins_name:
                                                    try:
                                                        plugin_group.load_plugin_hot(
                                                            i.name, i.plugin_type)
                                                    except BaseException as err:
                                                        Print.print_err(
                                                            f"插件热加载出现问题: {err}")
                                    else:
                                        Print.print_inf(
                                            "插件已存在, 若要更新版本, 请重启 ToolDelta", need_log=False)
                                        r = input(Print.fmt_info(
                                            "§f输入 §cq §f退出, 其他则返回插件市场"))
                                else:
                                    Print.print_inf(
                                        "下载插件后重启ToolDelta才能生效", need_log=False)
                                r = input(Print.fmt_info(
                                    "§f输入 §cq §f退出, 其他则返回插件市场"))
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
                    now_index = max(now_index - CTXS, 0)
        except KeyError as err:
            Print.print_err(f"获取插件市场插件出现问题: 键值对错误: {err}")
            return
        except requests.RequestException as err:
            Print.print_err(f"获取插件市场插件出现问题: {err}")
            return
        except Exception as err:
            Print.print_err("获取插件市场插件出现问题, 报错如下:")
            Print.print_err(traceback.format_exc())
            return
        clear_screen()
        Print.clean_print("§a已从插件市场返回 ToolDelta 控制台.")

    def get_datas_from_market(self, source_url: str | None = None) -> dict:
        """从插件市场获取数据

        Args:
            source_url (str | None, optional): 插件市场源, 默认为None,有则替换整体插件市场源

        Returns:
            dict: 插件市场数据
        """
        if isinstance(source_url, str):
            self.plugins_download_url = self.plugins_download_url
        market_datas = get_json_from_url(
            url_join(self.plugins_download_url, "market_tree.json")
        )
        return market_datas

    def get_plugin_data_from_market(self, plugin_id: str) -> PluginRegData:
        """从插件市场获取插件数据

        Args:
            plugin_id (str): 插件ID

        Raises:
            KeyError: 无法通过ID查找插件

        Returns:
            PluginRegData: 插件注册数据
        """
        plugin_name = self.plugin_id_name_map.get(plugin_id)
        if plugin_name is None:
            raise KeyError(f"无法通过ID: {plugin_id} 查找插件")
        data_url = self.plugins_download_url + "/" + plugin_name + "/datas.json"
        res = requests.get(data_url, timeout=10)
        res.raise_for_status()
        datas = json.loads(res.text)
        return PluginRegData(plugin_name, datas)

    def choice_plugin(self, plugin_data: PluginRegData) -> tuple[bool, list[PluginRegData]]:
        """选中插件进行介绍与操作

        Args:
            plugin_data (PluginRegData): 插件注册数据

        Returns:
            tuple[bool, list[PluginRegData]]: 是否下载, 下载的插件列表
        """
        pre_plugins_str = (
            ", ".join(
                [f"{k}§7v{v}" for k, v in plugin_data.pre_plugins.items()]) or "无"
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
        res = input(Print.fmt_info(
            "§f下载 = §aY§f, 取消 = §cN§f, 请输入:")).lower().strip()
        if res == "y":
            Print.clean_print(f"§6正在下载插件: §f{plugin_data.name}", end="\r")
            pres = self.download_plugin(plugin_data)
            pres.reverse()
            return True, pres
        return False, []

    def get_plugin_id_name_map(self) -> dict:
        """获取插件ID与插件名的映射

        Returns:
            dict: 插件ID与插件名的映射
        """
        res = requests.get(self.plugins_download_url +
                           "/plugin_ids_map.json", timeout=5)
        res.raise_for_status()
        res1: dict = json.loads(res.text)
        self.plugin_id_name_map = res1
        return res1

    def download_plugin(
        self,
        plugin_data: PluginRegData
    ) -> list[PluginRegData]:
        """下载插件

        Args:
            plugin_data (PluginRegData): 插件注册数据

        Raises:
            ValueError: 未知插件类型

        Returns:
            list[PluginRegData]: 插件注册数据列表
        """
        if self.plugin_id_name_map is None:
            self.plugin_id_name_map = self.get_plugin_id_name_map()
        pres = [plugin_data]
        download_paths = self.find_dirs(plugin_data)
        for plugin_id in plugin_data.pre_plugins:
            plugin_name = self.plugin_id_name_map[plugin_id]
            Print.clean_print(f"正在下载 {plugin_data.name} 的前置插件 {plugin_name}")
            plugin_datas = self.get_plugin_data_from_market(plugin_id)
            pres += self.download_plugin(plugin_datas)
        cache_dir = tempfile.mkdtemp()
        try:
            for paths in download_paths:
                if not paths.strip():
                    Print.print_war("下载路径为空, 跳过")
                    continue
                url = url_join(self.plugins_download_url, paths)
                # Determine download path based on plugin type
                match plugin_data.plugin_type:
                    case "classic":
                        download_path = os.path.join(
                            "插件文件", TOOLDELTA_CLASSIC_PLUGIN
                        )
                    case "injected":
                        download_path = os.path.join(
                            "插件文件", TOOLDELTA_INJECTED_PLUGIN
                        )
                    case _:
                        raise ValueError(
                            f"未知插件类型: {plugin_data.plugin_type}, 你可能需要通知ToolDelta项目开发组解决"
                        )
                os.makedirs(os.path.join(
                    cache_dir, plugin_data.name), exist_ok=True)
                path_last = path_dir(paths)
                if path_last is not None:
                    # 自动创建文件夹
                    folder_path = os.path.join(cache_dir, path_last)
                    os.makedirs(folder_path, exist_ok=True)
                urlmethod.download_unknown_file(
                    url, os.path.join(cache_dir, paths))
            # Move downloaded files to target download path
            target_path = download_path
            os.makedirs(target_path, exist_ok=True)
            # 制作所需的目录结构
            for root, _, files in os.walk(cache_dir):
                for filename in files:
                    source_file = os.path.join(root, filename)
                    target_file = os.path.join(
                        target_path, os.path.relpath(source_file, cache_dir)
                    )
                    os.makedirs(os.path.dirname(target_file), exist_ok=True)
                    shutil.move(source_file, target_file)
            from .plugin_manager import plugin_manager
            plugin_manager.push_plugin_reg_data(
                self.get_plugin_data_from_market(plugin_data.plugin_id))
            Print.clean_print(f"§a成功下载插件 §f{plugin_data.name}§a 至插件文件夹")
        finally:
            shutil.rmtree(cache_dir)
        return pres

    def find_dirs(self, plugin_data: PluginRegData) -> list[str]:
        """查找插件目录

        Args:
            plugin_data (PluginRegData): 插件注册数据

        Raises:
            KeyError: 目录结构错误
            eExceptionrr: 获取插件市场插件目录结构出现问题

        Returns:
            list[str]: 插件目录列表
        """
        try:
            data = get_json_from_url(
                url_join(self.plugins_download_url, "directory.json")
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
            raise KeyError(f"无法找到 {err}, 有可能是未来得及更新目录") from err
        except Exception as err:
            Print.print_err(f"获取插件市场插件目录结构出现问题: {err}")
            raise KeyError(f"获取插件市场插件目录结构出现问题: {err}")from err

    def get_latest_plugin_version(self, plugin_id: str) -> str:
        """获取最新插件版本

        Args:
            plugin_id (str): 插件ID

        Raises:
            KeyError: 无法通过ID获取最新插件版本

        Returns:
            str: 最新插件版本
        """
        result = get_json_from_url(
            url_join(self.plugins_download_url, "latest_versions.json")
        ).get(plugin_id)
        if isinstance(result, str):
            return result
        raise KeyError(f"无法通过ID: {plugin_id} 获取最新插件版本")


market = PluginMarket()
