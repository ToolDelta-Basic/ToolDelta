"插件市场客户端"

import asyncio
import os
import platform
import shlex
import time
import traceback

import requests
import ujson as json

from . import urlmethod
from .cfg import Cfg
from .color_print import Print
from .constants import (
    PLUGIN_MARKET_SOURCE_OFFICIAL,
    TOOLDELTA_CLASSIC_PLUGIN,
    TOOLDELTA_INJECTED_PLUGIN,
)
from .plugin_load import PluginRegData
from .utils import Utils

if platform.system().lower() == "windows":
    CLS_CMD = "cls"
else:
    CLS_CMD = "clear"


def clear_screen() -> None:
    "清屏"
    os.system(shlex.quote(CLS_CMD))


def url_join(*urls) -> str:
    """连接 URL

    Returns:
        str: 连接后的 URL
    """
    return "/".join(urls)


def get_json_from_url(url: str) -> dict:
    """从 URL 获取 JSON 数据

    Args:
        url (str): URL

    Raises:
        requests.RequestException: Url 请求失败
        requests.RequestException: 服务器返回了不正确的答复

    Returns:
        dict: JSON 数据
    """
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        raise requests.RequestException(
            f"URL 请求失败: {url} \n§6(看起来您要更改配置文件中的链接)"
        ) from exc
    except json.JSONDecodeError as exc:
        raise requests.RequestException(
            f"服务器返回了不正确的答复：{resp.text}"
        ) from exc


class PluginMarket:
    "插件市场类"

    def __init__(self):
        self.plugin_id_name_map: dict | None = None
        try:
            self.plugins_download_url = Cfg().get_cfg(
                "ToolDelta基本配置.json", {"插件市场源": str}
            )["插件市场源"]
        except Exception:
            self.plugins_download_url = PLUGIN_MARKET_SOURCE_OFFICIAL

    def enter_plugin_market(self, source_url: str | None = None, in_game=False) -> None:
        """进入插件市场

        Args:
            source_url (str | None, optional): 插件市场源
            in_game (bool, optional): 是否在游戏内
        """
        Print.clean_print("§6正在连接到插件市场..")
        self.plugin_id_name_map = self.get_plugin_id_name_map()
        CTXS = 12

        def display_plugins(start_index: int, total_pages: int):
            """显示插件列表

            Args:
                start_index (int): 起始索引
                total_pages (int): 总页数
            """
            clear_screen()
            Print.print_inf(
                f"{market_datas['SourceName']}: {market_datas['Greetings']}",
                need_log=False,
            )
            for i in range(start_index, min(start_index + CTXS, all_indexes)):
                plugin_id = plugins_list[i][0]
                plugin_name = plugin_ids_map[plugin_id]
                plugin_basic_datas = plugins_list[i][1]
                plugin_type = {"classic": "类式", "injected": "注入式"}.get(
                    plugin_basic_datas.get("plugin-type", "unknown"),
                    plugin_basic_datas.get("plugin-type", "unknown"),
                )
                Print.print_inf(
                    f" {i + 1}. §e{plugin_name} §av{plugin_basic_datas['version']} "
                    f"§b@{plugin_basic_datas['author']} §d{plugin_type}插件",
                    need_log=False,
                )
            Print.print_inf(
                f"§f第 {start_index // CTXS + 1} / {total_pages} 页，输入 §b+§f/§b- §f翻页",
                need_log=False,
            )
            Print.print_inf("§f输入插件序号选中插件并查看其下载页", need_log=False)

        def handle_plugin_selection(plugin_data: PluginRegData):
            """处理插件选择

            Args:
                plugin_data (dict): 插件数据

            Returns:
                bool: 是否退出
            """
            ok, pres = self.choice_plugin(plugin_data)
            if ok:
                Print.print_inf("可以输入 reload 使这个插件生效哦")
                return (
                    input(
                        Print.fmt_info("§f输入 §cq §f退出, 其他则返回插件市场")
                    ).lower()
                    == "q"
                )
            else:
                Print.print_inf("已取消。", need_log=False)
                time.sleep(1)
            return False

        try:
            market_datas = self.get_datas_from_market(source_url or "")
            plugin_ids_map = self.plugin_id_name_map
            plugins_list = list(market_datas["MarketPlugins"].items())
            all_indexes = len(plugins_list)
            now_index = 0
            sum_pages = (all_indexes - 1) // CTXS + 1
            last_operation = ""

            while True:
                display_plugins(now_index, sum_pages)

                last_operation = (
                    input(
                        Print.fmt_info(
                            "§f回车键继续上次操作，§bq§f 退出，请输入：", "§f 输入 "
                        )
                    )
                    or last_operation
                )
                last_operation = last_operation.lower().strip()

                # 翻页操作
                if last_operation in ["+", "-"]:
                    now_index = max(
                        0,
                        min(
                            now_index + (CTXS if last_operation == "+" else -CTXS),
                            all_indexes - 1,
                        ),
                    )
                elif last_operation == "q":  # 退出操作
                    break
                else:
                    res = Utils.try_int(last_operation)
                    if res and 1 <= res <= all_indexes:  # 插件选择操作
                        plugin_data = self.get_plugin_data_from_market(
                            plugins_list[res - 1][0]
                        )
                        if handle_plugin_selection(plugin_data):
                            break
                    else:  # 超出序号范围
                        Print.print_err("超出序号范围")

        except (KeyError, requests.RequestException) as err:
            Print.print_err(f"获取插件市场插件出现问题：{err}")
            input(Print.fmt_info("按回车键继续.."))
        except Exception:
            Print.print_err("获取插件市场插件出现问题，报错如下：")
            Print.print_err(traceback.format_exc())
            input(Print.fmt_info("按回车键继续.."))
        finally:
            clear_screen()
            Print.clean_print("§a已从插件市场返回 ToolDelta 控制台。")

    def get_datas_from_market(self, source_url: str | None = None) -> dict:
        """
        从插件市场的 market_tree.json 获取数据

        Args:
            source_url (str | None, optional): 插件市场源，默认为 None, 有则替换整体插件市场源

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
        """从插件市场获取单个插件数据

        Args:
            plugin_id (str): 插件 ID

        Raises:
            KeyError: 无法通过 ID 查找插件

        Returns:
            PluginRegData: 插件注册数据
        """
        if self.plugin_id_name_map is None:
            self.plugin_id_name_map = self.get_plugin_id_name_map()
        plugin_name = self.plugin_id_name_map.get(plugin_id)
        if plugin_name is None:
            raise requests.RequestException(
                f"无法通过 ID: {plugin_id} 查找插件, 你可能需要反馈此问题至开发者"
            )
        data_url = self.plugins_download_url + "/" + plugin_name + "/datas.json"
        datas = get_json_from_url(data_url)
        return PluginRegData(plugin_name, datas)

    def choice_plugin(
        self, plugin_data: PluginRegData
    ) -> tuple[bool, list[PluginRegData]]:
        """选中插件进行介绍与操作

        Args:
            plugin_data (PluginRegData): 插件注册数据

        Returns:
            tuple[bool, list[PluginRegData]]: 是否下载，下载的插件列表
        """
        pre_plugins_str = (
            ", ".join([f"{k}§7v{v}" for k, v in plugin_data.pre_plugins.items()])
            or "无"
        )
        clear_screen()
        Print.print_inf(
            f"{plugin_data.name} v{plugin_data.version_str}", need_log=False
        )
        Print.print_inf(
            f"作者：§f{plugin_data.author}§7, 版本：§f{plugin_data.version_str} §b{plugin_data.plugin_type_str}",
            need_log=False,
        )
        Print.print_inf(f"前置插件：§f{pre_plugins_str}", need_log=False)
        Print.print_inf(f"介绍：{plugin_data.description}", need_log=False)
        Print.print_inf("", need_log=False)
        res = (
            input(Print.fmt_info("§f下载 = §aY§f, 取消 = §cN§f, 请输入："))
            .lower()
            .strip()
        )
        if res == "y":
            Print.clean_print(f"§6正在下载插件：§f{plugin_data.name}", end="\r")
            pres = self.download_plugin(plugin_data)
            pres.reverse()
            return True, pres
        return False, []

    def get_plugin_id_name_map(self) -> dict:
        """获取插件 ID 与插件名的映射

        Returns:
            dict: 插件 ID 与插件名的映射
        """
        try:
            res = requests.get(
                self.plugins_download_url + "/plugin_ids_map.json", timeout=5
            )
            res.raise_for_status()
            res1: dict = json.loads(res.text)
        except Exception as err:
            Print.print_err(
                f"从 {self.plugins_download_url} 获取插件信息遇到问题: {err}"
            )
            raise SystemExit
        self.plugin_id_name_map = res1
        return res1

    def get_download_list(self, plugin_data: PluginRegData) -> dict[str, PluginRegData]:
        """
        获取一个插件的下载列表

        Args:
            plugin_data (PluginRegData): 插件注册数据

        Returns:
            list[str]: 下载列表
        """
        if self.plugin_id_name_map is None:
            self.plugin_id_name_map = self.get_plugin_id_name_map()
        download_paths = {}
        stack = [plugin_data]
        while stack:
            current_plugin = stack.pop()
            download_paths[current_plugin.name] = current_plugin
            for plugin_id in current_plugin.pre_plugins:
                plugin_datas = self.get_plugin_data_from_market(plugin_id)
                stack.append(plugin_datas)
        return download_paths

    def download_plugin(
        self, plugin_data: PluginRegData, with_pres=True, is_enabled=True
    ) -> list[PluginRegData]:
        """
        下载插件
        注意：只能传入由 `get_plugin_data_from_market()` 生成的数据

        Args:
            plugin_data (PluginRegData): 插件注册数据
            with_pres (bool): 是否一同下载前置插件
            is_enabled (bool): 下载的插件是否要自动禁用

        Raises:
            ValueError: 未知插件类型

        Returns:
            list[PluginRegData]: 本插件和其前置插件的注册数据列表
        """
        if self.plugin_id_name_map is None:
            self.plugin_id_name_map = self.get_plugin_id_name_map()
        # 打印正在获取的插件下载树
        Print.clean_print(
            f"§6正在获取插件下载树 §f{plugin_data.name}§6.." + " " * 15, end="\r"
        )
        plugin_list = self.get_download_list(plugin_data)
        plugin_filepaths_dict = {}
        for k, v in plugin_list.items():
            plugin_filepaths_dict[k] = self.find_dirs(v)
        Print.clean_print(f"§a成功获取插件下载树 §f{plugin_data.name}§a" + " " * 15)
        plugins_url2dst_solve: list[tuple[str, str]] = []
        for plugin_name, pluginInfo in plugin_list.items():
            match pluginInfo.plugin_type:
                case "classic":
                    plugintype_path = os.path.join("插件文件", TOOLDELTA_CLASSIC_PLUGIN)
                case "injected":
                    plugintype_path = os.path.join(
                        "插件文件", TOOLDELTA_INJECTED_PLUGIN
                    )
                case _:
                    raise ValueError(
                        f"未知插件类型：{pluginInfo.plugin_type}, 你可能需要通知 ToolDelta 项目开发组解决"
                    )
            for path in plugin_filepaths_dict[plugin_name]:
                plugins_url2dst_solve.append(
                    (
                        url_join(self.plugins_download_url, path),
                        os.path.join(plugintype_path, path),
                    )
                )
        Print.clean_print(
            f"§bTD下载管理器: §7需要下载 §c{len(plugins_url2dst_solve)} §7个文件"
        )
        asyncio.run(urlmethod.download_file_urls(plugins_url2dst_solve))
        Print.clean_print("§a• 插件安装已完成")
        return list(plugin_list.values())

    def find_dirs(self, plugin_data: PluginRegData) -> list[str]:
        """
        查找插件目录

        Args:
            plugin_data (PluginRegData): 插件注册数据

        Raises:
            KeyError: 目录结构错误
            Exception: 获取插件市场插件目录结构出现问题

        Returns:
            list[str]: 插件目录列表
        """
        try:
            data = get_json_from_url(
                url_join(self.plugins_download_url, "directory.json")
            )
            data_list = []
            for folder, files in data.items():
                if plugin_data.name == folder.split(r"/")[0]:
                    # 展开
                    for file in files:
                        data_list.append(folder + r"/" + file)
            return data_list
        except KeyError as err:
            Print.print_err(
                f"获取插件市场插件目录结构出现问题：无法找到 {err}, 有可能是未来得及更新目录"
            )
            raise KeyError(f"无法找到 {err}, 有可能是未来得及更新目录") from err
        except Exception as err:
            Print.print_err(f"获取插件市场插件目录结构出现问题：{err}")
            raise KeyError(f"获取插件市场插件目录结构出现问题：{err}") from err

    def get_latest_plugin_version(self, plugin_id: str) -> str:
        """获取最新插件版本

        Args:
            plugin_id (str): 插件 ID

        Raises:
            KeyError: 无法通过 ID 获取最新插件版本

        Returns:
            str: 最新插件版本
        """
        result = get_json_from_url(
            url_join(self.plugins_download_url, "latest_versions.json")
        ).get(plugin_id)
        if isinstance(result, str):
            return result
        raise KeyError(f"无法通过 ID: {plugin_id} 获取最新插件版本")


market = PluginMarket()
