"插件市场客户端"

import asyncio
import os
import time
import traceback
import requests
import json

from .utils import cfg, fmts
from .constants import (
    TOOLDELTA_CLASSIC_PLUGIN,
    TOOLDELTA_PLUGIN_CFG_DIR,
    TOOLDELTA_PLUGIN_DATA_DIR,
    PLUGIN_MARKET_SOURCE_OFFICIAL,
)
from .plugin_load import PluginRegData, PluginsPackage
from .utils import try_int, thread_gather, urlmethod


FILETREE = dict[str, "int | FILETREE"]

def url_join(*urls: str) -> str:
    return "/".join(url.strip("/") for url in urls).strip("/")


def unfold_directory_dict(dirs: FILETREE, base_path: str = "", sep: str = "/"):
    unfolded: list[str] = []
    for dirname, dir_or_file in dirs.items():
        dirpath = sep.join((base_path, dirname)).strip("/")
        if isinstance(dir_or_file, dict):
            unfolded.extend(unfold_directory_dict(dir_or_file, dirpath, sep))
        else:
            unfolded.append(dirpath)
    return unfolded

def get_json_from_url(url: str):
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        raise requests.RequestException(
            f"URL 请求失败: {url} \n§6(看起来您要更改配置文件中的链接)\n报错: {exc}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise requests.RequestException(
            f"服务器返回了不正确的答复：{resp.text}"
        ) from exc


class PluginMarket:
    "插件市场类"

    def __init__(self):
        self._cached_market_tree = {}
        self._cached_plugins_id_map = {}
        self._cached_market_filetree: FILETREE = {}
        try:
            self.plugin_market_content_url = cfg.get_cfg(
                "ToolDelta基本配置.json", {"插件市场源": str}
            )["插件市场源"]
        except Exception:
            self.plugin_market_content_url = PLUGIN_MARKET_SOURCE_OFFICIAL

    def enter_plugin_market(self, source_url: str | None = None, in_game=False) -> None:
        """
        进入插件市场

        Args:
            source_url (str | None, optional): 插件市场源
            in_game (bool, optional): 是否在游戏内调用的插件市场命令
        """
        if source_url:
            self.plugin_market_content_url = source_url

        fmts.ansi_save_screen()
        fmts.clean_print("§6正在连接到插件市场..")
        CONTENT_LENGTH = 15

        try:
            market_datas = self.get_market_tree()
            plugin_ids_map = self.get_plugin_id_name_map()
            show_list = [
                (i, j) if i.startswith("[pkg]") else ("[pkg]" + i, j)
                for i, j in market_datas["Packages"].items()
            ] + list(market_datas["MarketPlugins"].items())

            while 1:
                fmts.ansi_cls()
                valid_show_list = self.search_by_rule(market_datas, show_list)
                if valid_show_list is None:
                    fmts.clean_print("§6已退出。")
                    return
                elif valid_show_list == []:
                    input(fmts.clean_fmt("§c未找到匹配的插件; 回车键继续"))
                    continue

                total_indexes = len(valid_show_list)
                now_index = 0
                sum_pages = (total_indexes - 1) // CONTENT_LENGTH + 1
                last_operation = ""

                while 1:
                    self.display_plugins_and_packages(
                        market_datas,
                        plugin_ids_map,
                        valid_show_list,
                        now_index,
                        sum_pages,
                        CONTENT_LENGTH,
                    )

                    last_operation = (
                        input(
                            fmts.clean_fmt("§f回车键继续上次操作, §bq§f 退出，请输入: ")
                        )
                        or last_operation
                    )
                    last_operation = last_operation.lower().strip()
                    if last_operation in ["+", "-"]:
                        now_index = max(
                            0,
                            min(
                                now_index
                                + (
                                    CONTENT_LENGTH
                                    if last_operation == "+"
                                    else -CONTENT_LENGTH
                                ),
                                total_indexes - 1,
                            ),
                        )
                    elif last_operation == "q":
                        break
                    else:
                        res = try_int(last_operation)
                        if res and 1 <= res <= total_indexes:
                            result = valid_show_list[res - 1]
                            if not result[0].startswith("[pkg]"):
                                # 这是插件
                                plugin_data = self.get_plugin_data_from_market(
                                    result[0]
                                )
                                if self.handle_plugin_selection(plugin_data):
                                    break
                            else:
                                # 这是整合包
                                package_data = self.get_package_data_from_market(
                                    result[0]
                                )
                                if self.handle_package_selection(package_data):
                                    break
                        else:
                            fmts.clean_print("§c超出序号范围")

        except (KeyError, requests.RequestException) as err:
            fmts.clean_print(
                f"§c获取插件市场插件出现问题({err.__class__.__name__}): {err}"
            )
            input(fmts.clean_fmt("§6按回车键继续.."))
        except Exception:
            fmts.clean_print("§c获取插件市场插件出现问题, 报错如下:")
            fmts.clean_print("§c" + traceback.format_exc().replace("\n", "\n§c"))
            input(fmts.clean_fmt("§6按回车键继续.."))
        finally:
            fmts.ansi_load_screen()
            fmts.clean_print("§a已从插件市场返回 ToolDelta 控制台。")

    @staticmethod
    def search_by_rule(
        market_datas, show_list: list[tuple[str, dict]]
    ) -> list[tuple[str, dict]] | None:
        fmts.clean_print(f"{market_datas['SourceName']}: {market_datas['Greetings']}")
        fmts.clean_print("§a------------------------------")
        fmts.clean_print("§6请选择搜索方式: ")
        fmts.clean_print("  1 -     §b按插件名")
        fmts.clean_print("  2 -     §d按插件作者名")
        fmts.clean_print("  3 -     §e按插件 ID")
        fmts.clean_print("  4 -     §a随便逛逛")
        fmts.clean_print("  其它    §c退出")
        resp = input(fmts.clean_fmt("请输入选项: ")).strip().strip("[]")
        output_show_list: list[tuple[str, dict]] = []
        match resp:
            case "1":
                plugin_name_kw = (
                    input(fmts.clean_fmt("§6请输入插件名(中的关键词): "))
                    .strip()
                    .lower()
                )
                if plugin_name_kw == "":
                    return []
                for plugin_id, plugin_data in show_list:
                    pname = (
                        plugin_id
                        if plugin_id.startswith("[pkg]")
                        else plugin_data["name"]
                    )
                    if plugin_name_kw in pname.lower():
                        output_show_list.append((plugin_id, plugin_data))
                return output_show_list
            case "2":
                plugin_author_kw = (
                    input(fmts.clean_fmt("§6请输入插件作者名(中的关键词): "))
                    .strip()
                    .lower()
                )
                if plugin_author_kw == "":
                    return []
                for plugin_name, plugin_data in show_list:
                    if plugin_author_kw in plugin_data["author"].lower():
                        output_show_list.append((plugin_name, plugin_data))
                return output_show_list
            case "3":
                plugin_id_kw = (
                    input(fmts.clean_fmt("§6请输入插件ID(中的关键词): "))
                    .strip()
                    .lower()
                )
                if plugin_id_kw == "":
                    return []
                for plugin_id, plugin_data in show_list:
                    if plugin_id_kw in plugin_id:
                        output_show_list.append((plugin_id, plugin_data))
                        break
                return output_show_list
            case "4":
                return show_list
            case _:
                return None

    def display_plugins_and_packages(
        self,
        market_datas: dict,
        plugin_ids_map: dict[str, str],
        show_list: list[tuple[str, dict]],
        start_index: int,
        total_pages: int,
        content_length: int = 15,
    ):
        """
        显示插件列表

        Args:
            start_index (int): 起始索引
            total_pages (int): 总页数
        """
        fmts.ansi_cls()
        fmts.clean_print(f"{market_datas['SourceName']}: {market_datas['Greetings']}")
        for i in range(start_index, min(start_index + content_length, len(show_list))):
            show_name, description = show_list[i]
            if show_name.startswith("[pkg]"):
                pkg_name = show_name
                fmts.clean_print(f" {i + 1}. §c[整合包]§e{pkg_name[5:]}")
            else:
                plugin_id = show_name
                plugin_name = plugin_ids_map[plugin_id]
                plugin_type = {"classic": "类式"}.get(
                    description.get("plugin-type", "unknown"),
                    description.get("plugin-type", "unknown"),
                )
                fmts.clean_print(
                    f" {i + 1}. §e{plugin_name} §av{description['version']} "
                    f"§b@{description['author']} §d{plugin_type}插件"
                )
        fmts.clean_print(
            f"§f第§a{start_index // content_length + 1}§f/§a{total_pages}§f页, 输入§b+§f/§b-§f翻页"
        )
        fmts.clean_print("§f输入插件序号选中插件并查看其下载页")

    def handle_package_selection(self, pack: PluginsPackage):
        ok = self.skim_package(pack)
        if ok:
            fmts.clean_print("可以输入 §breload§r 使这个整合包生效哦")
            return (
                input(fmts.clean_fmt("§f输入 §cq §f退出, 其他则返回插件市场")).lower()
                == "q"
            )
        else:
            fmts.clean_print("已取消。")
            time.sleep(1)
        return False

    def handle_plugin_selection(self, plugin_data: PluginRegData):
        ok, pres = self.skim_plugin(plugin_data)
        if ok:
            fmts.clean_print("可以输入 §breload§r 使这个插件生效哦")
            return (
                input(fmts.clean_fmt("输入 §cq §r退出, 其他则返回插件市场")).lower()
                == "q"
            )
        else:
            fmts.clean_print("已取消。")
            time.sleep(1)
        return False

    # 从插件市场的 market_tree.json 获取数据
    def get_market_tree(self) -> dict:
        if self._cached_market_tree != {}:
            return self._cached_market_tree
        market_datas = self._cached_market_tree = get_json_from_url(
            url_join(self.plugin_market_content_url, "market_tree.json")
        )
        return market_datas

    # 从插件市场获取单个插件数据
    def get_plugin_data_from_market(self, plugin_id: str) -> PluginRegData:
        plugin_name = self.get_plugin_id_name_map().get(plugin_id)
        if plugin_name is None:
            raise requests.RequestException(
                f"无法通过 ID: {plugin_id} 查找插件, 你可能需要反馈此问题至开发者"
            )
        data_url = url_join(self.plugin_market_content_url, plugin_name, "datas.json")
        datas = get_json_from_url(data_url)
        return PluginRegData(plugin_name, datas)

    # 从插件市场获取单个整合包数据
    def get_package_data_from_market(self, name: str) -> PluginsPackage:
        target_data_url = url_join(self.plugin_market_content_url, name, "datas.json")
        content = requests.get(target_data_url).json()
        return PluginsPackage(name, content)

    def skim_plugin(
        self, plugin_data: PluginRegData
    ) -> tuple[bool, list[PluginRegData]]:
        """
        选中插件进行介绍与操作

        Args:
            plugin_data (PluginRegData): 插件注册数据

        Returns:
            tuple[bool, list[PluginRegData]]: 是否下载，下载的插件列表
        """
        pre_plugins_str = (
            ", ".join([f"{k}§7v{v}" for k, v in plugin_data.pre_plugins.items()])
            or "无"
        )
        has_doc = self.get_plugin_filetree(plugin_data.name).get("readme.txt") is not None
        while True:
            fmts.ansi_cls()
            fmts.clean_print(f"{plugin_data.name} v{plugin_data.version_str}")
            fmts.clean_print(
                f"作者: §f{plugin_data.author}§7, 版本: §f{plugin_data.version_str} §b{plugin_data.plugin_type_str}"
            )
            fmts.clean_print(f"前置插件：§f{pre_plugins_str}")
            fmts.clean_print(f"介绍：{plugin_data.description}")
            fmts.clean_print("")
            prompt = f"§f下载 = §aY§f, 取消 = §cN§f{', 查看文档 = §dD§f ' if has_doc else ''} 请输入: "
            res = (
                input(fmts.clean_fmt(prompt))
                .lower()
                .strip()
            )
            if res == "y":
                fmts.clean_print(f"§6正在下载插件：§f{plugin_data.name}", end="\r")
                pres = self.download_plugin(plugin_data)
                pres.reverse()
                return True, pres
            elif res == "d":
                if has_doc:
                    fmts.clean_print("§6正在读取文档..")
                    self.lookup_plugin_doc(plugin_data)
                else:
                    fmts.clean_print("§c该插件没有文档..")
                return False, []
            else:
                return False, []

    def skim_package(self, pack: PluginsPackage) -> bool:
        """
        选中整合包进行介绍与操作

        Args:
            pack (PluginsPackage): 整合包数据类

        Returns:
            bool: 是否下载安装
        """
        fmts.ansi_cls()
        inc_plugins_name: list[str] = []
        for pid in pack.plugin_ids:
            if pname := self.get_plugin_id_name_map().get(pid):
                inc_plugins_name.append(pname)
            else:
                fmts.clean_print(f"§c无法通过ID {pid} 查找插件, 有可能是插件市场出错")
                return True
        fmts.clean_print(f"§f整合包 §b{pack.name[5:]} §7(v{pack.version})§r:")
        fmts.clean_print(f"作者: §b{pack.author}")
        fmts.clean_print("介绍: §f" + pack.description.replace("\n", "\n      "))
        fmts.clean_print("§d包含的插件的列表:")
        for pname in inc_plugins_name:
            fmts.clean_print(f" §7- §r{pname}")
        # 显示其他文件数量
        ftree = self.get_market_filetree()
        dirdata = ftree.get(pack.name)
        if dirdata is None:
            raise ValueError(f"插件市场内不存在整合包 {pack.name}")
        plugin_config_files = ftree.get(url_join(pack.name, "插件配置文件"), {})
        assert not isinstance(plugin_config_files, int)
        # 计算插件配置文件数量
        config_files_num = len(unfold_directory_dict(plugin_config_files))
        # 计算插件数据文件数量
        data_file_dir = ftree.get(url_join(pack.name, "插件数据文件"), {})
        assert not isinstance(data_file_dir, int)
        data_files_num = len(unfold_directory_dict(data_file_dir))
        fmts.clean_print(
            f"§2并包含§r{config_files_num}§2个插件配置文件, §r{data_files_num}§2个插件数据文件"
        )
        if (
            input(fmts.clean_fmt("§f下载安装 = §aY§f, 取消 = §cN§f, 请输入："))
            .lower()
            .strip()
        ) == "y":
            self.download_plugin_package(pack)
            return True
        else:
            return False

    def download_plugin_package(self, pack: PluginsPackage):
        fmts.clean_print("§6获取插件数据中...", end="\r")
        find_plugins = thread_gather(
            [(self.get_plugin_data_from_market, (i,)) for i in pack.plugin_ids]
        )
        ftree = self.get_market_filetree()
        dirdata = ftree.get(pack.name)
        if dirdata is None:
            raise ValueError(f"插件市场内不存在整合包 {pack.name}")
        plugin_config_files = ftree.get(url_join(pack.name, "插件配置文件"), {})
        plugin_data_files = ftree.get(url_join(pack.name, "插件数据文件"), {})
        assert not isinstance(plugin_config_files, int)
        assert not isinstance(plugin_data_files, int)
        download_url_dirs: list[tuple[str, str]] = []
        # 插件配置文件
        for cfgfile_path in unfold_directory_dict(plugin_config_files):
            f_url = url_join(
                self.plugin_market_content_url,
                pack.name,
                "插件配置文件",
                cfgfile_path,
            )
            f_local = os.path.join(TOOLDELTA_PLUGIN_CFG_DIR, cfgfile_path)
            if os.path.isfile(f_local) and (
                input(
                    fmts.clean_fmt(
                        f"§6配置文件 §r{cfgfile_path}§6 已存在, 是否替换§r(§a[默认]y§r/§cn§r)§6: "
                    )
                )
                .strip()
                .lower()
                != "n"
            ):
                download_url_dirs.append((f_url, f_local))
        # 插件数据文件
        for inc_file_path in unfold_directory_dict(plugin_data_files):
            # url: [pkg]pkg_name/插件数据文件/anydir/...
            # local: 插件数据文件/anydir/...
            f_url = url_join(
                self.plugin_market_content_url, pack.name, "插件数据文件", inc_file_path
            )
            f_local = os.path.join(
                TOOLDELTA_PLUGIN_DATA_DIR, inc_file_path
            )
            if not os.path.isfile(f_local) or (
                input(
                    fmts.clean_fmt(
                        f"§6数据文件 §r{f_local}§6 已存在, 是否替换§r(§ay§r/§cn[默认]§r)§6: "
                    )
                )
                .strip()
                .lower()
                == "y"
            ):
                download_url_dirs.append((f_url, f_local))
        fmts.clean_print(f"§6开始下载整合包 {pack.name.replace('[pkg]', '')}")
        for _, fpath in download_url_dirs:
            # 初始化需要的文件夹路径
            os.makedirs(os.path.dirname(fpath), exist_ok=True)
        asyncio.run(urlmethod.download_file_urls(download_url_dirs))
        # 下载插件主体
        for plugin in find_plugins:
            self.download_plugin(plugin)
        fmts.clean_print("整合包下载完成")

    # 下载插件
    def download_plugin(
        self, plugin_data: PluginRegData, with_pres=True, is_enabled=False
    ) -> list[PluginRegData]:
        fmts.clean_print(
            f"§6正在获取 §f{plugin_data.name} §6插件的下载任务清单.." + " " * 15,
            end="\r",
        )
        if with_pres:
            plugin_list = self.get_plugin_download_list(plugin_data)
        else:
            plugin_list = {plugin_data.name: plugin_data}
        plugin_filepaths_dict: dict[str, list[str]] = {}
        for plugin_name, plugin_data in plugin_list.items():
            plugin_filepaths_dict[plugin_name] = unfold_directory_dict(
                self.get_plugin_filetree(plugin_data.name)
            )
        fmts.clean_print(f"§a已获取插件下载清单 §f{plugin_data.name}§a" + " " * 15)
        plugin_remote_to_local_path: list[tuple[str, str]] = []
        for plugin_name, this_plugin_info in plugin_list.items():
            match this_plugin_info.plugin_type:
                case "classic":
                    plugintype_path = os.path.join("插件文件", TOOLDELTA_CLASSIC_PLUGIN)
                case _:
                    raise ValueError(
                        f"未知插件类型：{this_plugin_info.plugin_type}, 你可能需要通知 ToolDelta 项目开发组解决"
                    )
            for filepath in plugin_filepaths_dict[plugin_name]:
                plugin_remote_to_local_path.append(
                    (
                        url_join(self.plugin_market_content_url, this_plugin_info.name, filepath),
                        os.path.join(plugintype_path, this_plugin_info.name, filepath),
                    )
                )
        fmts.clean_print(
            f"§bTD下载管理器: §7需要下载 §c{len(plugin_remote_to_local_path)} §7个文件"
        )
        asyncio.run(urlmethod.download_file_urls(plugin_remote_to_local_path))
        fmts.clean_print("§a• 插件安装已完成")
        return list(plugin_list.values())

    def lookup_plugin_doc(self, plugin: PluginRegData):
        url = url_join(self.plugin_market_content_url, plugin.name, "readme.txt")
        resp = requests.get(url)
        if resp.status_code != 200:
            fmts.clean_print("§c无法获取插件文档")
            return
        counter = 0
        fmts.ansi_cls()
        fmts.clean_print("§b文档正文:")
        for ln in resp.text.split("\n"):
            fmts.clean_print("  " + ln)
            counter += 1
            MAX_LINES = 15
            if counter > MAX_LINES:
                counter = 0
                input(fmts.clean_fmt("§a[按回车键继续阅读..]"))
        input(fmts.clean_fmt("§a已经读完正文了 [Enter]"))

    # 获取插件 ID 到插件名的映射
    def get_plugin_id_name_map(self) -> dict[str, str]:
        if self._cached_plugins_id_map == {}:
            try:
                res = get_json_from_url(
                    url_join(self.plugin_market_content_url, "plugin_ids_map.json")
                )
            except Exception as err:
                fmts.clean_print(
                    f"§c从 {self.plugin_market_content_url} 获取插件信息遇到问题: {err}"
                )
                raise SystemExit
            self._cached_plugins_id_map = res
            return res
        else:
            return self._cached_plugins_id_map

    # 获取一个插件所需下载的所有插件 -> dict[插件名, 插件数据]
    def get_plugin_download_list(
        self, plugin_data: PluginRegData
    ) -> dict[str, PluginRegData]:
        download_paths: dict[str, PluginRegData] = {}
        stack = [plugin_data]
        while stack:
            current_plugin = stack.pop()
            download_paths[current_plugin.name] = current_plugin
            for plugin_id in current_plugin.pre_plugins:
                plugin_datas = self.get_plugin_data_from_market(plugin_id)
                stack.append(plugin_datas)
        return download_paths

    # 获取插件市场的文件目录结构
    def get_market_filetree(self) -> FILETREE:
        if self._cached_market_filetree == {}:
            self._cached_market_filetree = get_json_from_url(
                url_join(self.plugin_market_content_url, "directory_tree.json")
            )
        return self._cached_market_filetree

    # 获取单个插件的插件文件夹目录结构
    def get_plugin_filetree(self, plugin_name: str) -> FILETREE:
        tree = self.get_market_filetree().get(plugin_name)
        if tree is None:
            raise KeyError(f"无法通过名称: {plugin_name} 获取此插件下载项")
        if isinstance(tree, dict):
            return tree
        else:
            raise ValueError(f"名称 {plugin_name} 是文件而非目录")

    # 根据插件 ID 获取插件的最新版本号
    def get_latest_plugin_version(self, plugin_id: str) -> tuple[int, int, int]:
        result = get_json_from_url(
            url_join(self.plugin_market_content_url, "latest_versions.json")
        ).get(plugin_id)
        if result is None:
            raise KeyError(f"无法通过 ID: {plugin_id} 获取最新插件版本")
        try:
            ver = tuple(int(i) for i in result.split("."))
            assert len(ver) == 3
        except Exception:
            raise ValueError(f"插件版本号字符串 {result!r} 不正确")
        return ver[0], ver[1], ver[2]


market = PluginMarket()
