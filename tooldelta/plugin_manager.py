"插件管理器"

import os
import platform
import shlex
import shutil
from typing import Optional

import ujson as json

from .color_print import Print
from .constants import (
    PLUGIN_TYPE_MAPPING,
    TOOLDELTA_CLASSIC_PLUGIN,
    TOOLDELTA_INJECTED_PLUGIN,
    TOOLDELTA_PLUGIN_DIR,
)
from .plugin_load import PluginRegData
from .plugin_market import market
from .utils import Utils

JsonIO = Utils.SimpleJsonDataReader

if platform.system().lower() == "windows":
    CLS_CMD = "cls"
else:
    CLS_CMD = "clear"


def clear_screen() -> None:
    "清空屏幕"
    os.system(shlex.quote(CLS_CMD))


class PluginManager:
    "插件管理器"

    plugin_reg_data_path = "插件注册表"
    default_reg_data = {"classic": {}, "injected": {}, "unknown": {}}
    _plugin_datas_cache = []

    def manage_plugins(self) -> None:
        "插件管理界面"
        clear_screen()
        while 1:
            plugins = self.list_plugins_list()
            Print.clean_print("§f输入§bu§f更新本地所有插件, §f输入§cq§f退出")
            r = input(Print.clean_fmt("§f输入插件关键词进行选择\n(空格可分隔关键词):"))
            r1 = r.strip().lower()
            if r1 == "":
                continue
            if r1 == "q":
                return
            if r1 == "u":
                self.update_all_plugins(self.get_all_plugin_datas())
            else:
                res = self.search_plugin(r, plugins)
                if res is None:
                    input("[Enter 键继续..]")
                else:
                    self.plugin_operation(res)
            clear_screen()

    def plugin_operation(self, plugin: PluginRegData) -> None:
        "插件操作"
        description_fixed = plugin.description.replace("\n", "\n    ")
        clear_screen()
        Print.clean_print(f"§d插件名: §f{plugin.name}")
        Print.clean_print(f" - 版本：{plugin.version_str}")
        Print.clean_print(f" - 作者：{plugin.author}")
        Print.clean_print(f" 描述：{description_fixed}")
        Print.clean_print(
            f"§f1.删除插件  2.检查更新  3.{'禁用插件' if plugin.is_enabled else '启用插件'}  4.查看手册  §c回车退出"
        )
        f_dirname = {
            "classic": TOOLDELTA_CLASSIC_PLUGIN,
            "injected": TOOLDELTA_INJECTED_PLUGIN,
        }[plugin.plugin_type]
        match input(Print.clean_fmt("§f请选择选项: ")):
            case "1":
                r = input(
                    Print.clean_fmt("§c删除插件操作不可逆, 请输入 y, 其他取消：")
                ).lower()
                if r != "y":
                    return
                plugin_dir = os.path.join("插件文件", f_dirname, plugin.name)
                shutil.rmtree(
                    plugin_dir + ("+disabled" if not plugin.is_enabled else "")
                )
                Print.clean_print(f"§a已成功删除插件 {plugin.name}, 回车键继续")
                input("[Enter 键继续..]")
                return
            case "2":
                latest_version = market.get_latest_plugin_version(plugin.plugin_id)
                if latest_version is None:
                    Print.clean_print("§6无法获取其的最新版本, 回车键继续")
                elif latest_version == plugin.version_str:
                    Print.clean_print("§a此插件已经为最新版本, 回车键继续")
                else:
                    Print.clean_print(
                        f"§a插件有新版本可用 ({plugin.version_str} => {latest_version})"
                    )
                    r = input(
                        Print.clean_fmt("输入§a1§f=立刻更新, §62§f=取消更新: ")
                    ).strip()
                    if r == "1":
                        Print.clean_print("§a正在下载新版插件...", end="\r")
                        market.download_plugin(plugin)
                        Print.clean_print("§a插件更新完成, 回车键继续")
                        plugin.version = tuple(
                            int(i) for i in latest_version.split(".")
                        )
                    else:
                        Print.clean_print("§6已取消, 回车键返回")
            case "3":
                if plugin.is_enabled:
                    os.rename(
                        os.path.join("插件文件", f_dirname, plugin.name),
                        os.path.join("插件文件", f_dirname, plugin.name + "+disabled"),
                    )
                else:
                    os.rename(
                        os.path.join("插件文件", f_dirname, plugin.name + "+disabled"),
                        os.path.join("插件文件", f_dirname, plugin.name),
                    )
                plugin.is_enabled = [True, False][plugin.is_enabled]
                Print.clean_print(
                    f"§6当前插件状态为: {['§c禁用', '§a启用'][plugin.is_enabled]}§6, 回车键继续"
                )
            case "4":
                self.lookup_readme(plugin)
            case _:
                return
        self.push_plugin_reg_data(plugin)
        input()

    def update_all_plugins(self, plugins: list[PluginRegData]) -> None:
        """
        更新全部插件

        Args:
            plugins (list[PluginRegData]): 插件注册信息列表
        """
        market_datas = market.get_datas_from_market()["MarketPlugins"]
        need_updates: list[tuple[PluginRegData, str]] = []
        for i in plugins:
            s_data = market_datas.get(i.plugin_id)
            if s_data is None:
                continue
            if i.version_str != s_data["version"]:
                need_updates.append((i, s_data["version"]))
        if need_updates:
            clear_screen()
            Print.clean_print("§f以下插件可进行更新:")
            for plugin, v in need_updates:
                Print.clean_print(f" - {plugin.name} §6{plugin.version_str}§f -> §a{v}")
            r = (
                input(Print.clean_fmt("§f输入§a y §f开始更新, §c n §f取消: "))
                .strip()
                .lower()
            )
            if r == "y":
                for plugin, v in need_updates:
                    self.update_plugin_from_market(plugin)
                Print.clean_print("§a全部插件已更新完成")
            else:
                Print.clean_print("§6已取消插件更新.")
            input("[Enter 键继续...]")
        else:
            input(Print.clean_fmt("§a无可更新的插件. [Enter 键继续]"))

    def update_plugin_from_market(self, plugin: PluginRegData):
        """
        更新单个插件，并且删除旧目录

        Args:
            plugin (PluginRegData): 插件注册信息，新旧皆可
        """
        Print.clean_print(
            f"§6正在获取插件 §f{plugin.name}§6 的在线插件数据..", end="\r"
        )
        old_plugins = self.get_all_plugin_datas()
        new_plugin_datas = market.get_plugin_data_from_market(plugin.plugin_id)
        new_plugins = market.download_plugin(new_plugin_datas, False, plugin.is_enabled)
        for new_plugin in new_plugins:
            for old_plugin in old_plugins:
                if (
                    new_plugin.plugin_id == old_plugin.plugin_id
                    and new_plugin.name != old_plugin.name
                ):
                    shutil.rmtree(old_plugin.dir)

    def search_plugin(self, resp, plugins) -> Optional[PluginRegData]:
        """
        搜索插件

        Returns:
            None: 未找到插件
            PluginRegData: 插件注册信息
        """
        res = self.search_plugin_by_kw(resp.split(), plugins)
        if not res:
            Print.clean_print("§c没有任何已安装插件匹配得上关键词")
            return None
        if len(res) > 1:
            Print.clean_print("§a☑ §f关键词查找到的插件:")
            for i, plugin in enumerate(res):
                Print.clean_print(str(i + 1) + ". " + self.make_plugin_icon(plugin))
            r = Utils.try_int(input(Print.clean_fmt("§f请选择序号: ")))
            if r is None or r not in range(1, len(res) + 1):
                Print.clean_print("§c序号无效, 回车键继续")
                return None
            return res[r - 1]
        return res[0]

    @staticmethod
    def lookup_readme(plugin: PluginRegData):
        """查看插件的 readme.txt 文档"""
        readme_path = os.path.join(
            TOOLDELTA_PLUGIN_DIR,
            PLUGIN_TYPE_MAPPING[plugin.plugin_type],
            plugin.name,
            "readme.txt",
        )
        if os.path.isfile(readme_path):
            with open(readme_path, encoding="utf-8") as f:
                lns = f.read().split("\n")
            counter = 0
            clear_screen()
            Print.clean_print(f"§b文档正文 ({readme_path}):")
            for ln in lns:
                Print.clean_print("  " + ln)
                counter += 1
                if counter > 15:
                    counter = 0
                    input(Print.clean_fmt("§a[按回车键继续阅读..]"))
            Print.clean_print("§a[按回车键退出..]")
        else:
            Print.clean_print("§6此插件没有手册文档 [回车键继续]")

    @staticmethod
    def search_plugin_by_kw(
        kws: list[str], plugins: list[PluginRegData]
    ) -> list[PluginRegData]:
        """根据关键词搜索插件

        Args:
            kws (list[str]): 关键词列表
            plugins (list[PluginRegData]): 插件注册信息列表

        Returns:
            list[PluginRegData]: 插件注册信息列表
        """
        res = [plugin for plugin in plugins if all(kw in plugin.name for kw in kws)]
        return res

    def is_valid_registered(self, plugin_name: str) -> bool:
        """插件是否已有效注册

        Args:
            plugin_name (str): 插件名

        Returns:
            bool: 是否已注册
        """
        if not self._plugin_datas_cache:
            self._plugin_datas_cache = self.get_all_plugin_datas()
        for i in self._plugin_datas_cache:
            if i.name == plugin_name:
                return i.is_registered
        raise ValueError(f"插件 {plugin_name} 不存在")

    @staticmethod
    def get_all_plugin_datas() -> list[PluginRegData]:
        """
        获取所有插件的注册信息 (包括没有正常注册的)

        Returns:
            list[PluginRegData]: 插件数据表
        """
        plugins = []
        for ptype, type_dir in PLUGIN_TYPE_MAPPING.items():
            p_dirs = os.path.join(TOOLDELTA_PLUGIN_DIR, type_dir)
            for fd in os.listdir(p_dirs):
                datpath = os.path.join(p_dirs, fd, "datas.json")
                is_enabled = not fd.endswith("+disabled")
                if os.path.isfile(datpath):
                    with open(datpath, "r", encoding="utf-8") as f:
                        jsdata = json.load(f)
                        plugins.append(
                            PluginRegData(
                                fd.replace("+disabled", ""),
                                jsdata,
                                is_enabled=is_enabled,
                            )
                        )
                else:
                    plugins.append(
                        PluginRegData(
                            fd.replace("+disabled", ""),
                            {"plugin-type": ptype},
                            is_registered=False,
                            is_enabled=is_enabled,
                        )
                    )
        return plugins

    @staticmethod
    def push_plugin_reg_data(plugin_data: PluginRegData) -> None:
        """将插件注册信息推送到插件注册表

        Args:
            plugin_data (PluginRegData): 插件注册信息
        """
        end_str = "" if plugin_data.is_enabled else "+disabled"
        f_dir = os.path.join(
            TOOLDELTA_PLUGIN_DIR,
            PLUGIN_TYPE_MAPPING[plugin_data.plugin_type],
            plugin_data.name + end_str,
        )
        if not os.path.isdir(f_dir):
            os.mkdir(f_dir)
        try:
            old_dat: dict = JsonIO.SafeJsonLoad(
                open(os.path.join(f_dir, "datas.json"), "r", encoding="utf-8")
            )  # type: ignore
        except Exception:
            old_dat = {}
        old_dat.update(plugin_data.dump())
        JsonIO.SafeJsonDump(
            old_dat,
            open(os.path.join(f_dir, "datas.json"), "w", encoding="utf-8"),
        )

    @staticmethod
    def make_plugin_icon(plugin: PluginRegData) -> str:
        """根据插件类型生成插件图标

        Args:
            plugin (PluginRegData): 插件注册信息

        Returns:
            str: 插件图标
        """
        ico_colors = {"classic": "§b", "injected": "§d"}
        return (
            ico_colors.get(plugin.plugin_type, "§7")
            + "■ "
            + (("§a" if plugin.is_enabled else "§7") if plugin.is_registered else "§6")
            + plugin.name
        )

    def make_printable_list(self, plugins: list[PluginRegData]) -> None:
        """生成可打印的插件列表

        Args:
            plugins (list[PluginRegData]): 插件注册信息列表
        """
        texts = []
        for plugin in sorted(plugins, key=lambda x: x.is_registered):
            texts.append(self.make_plugin_icon(plugin))
        lfts = []
        rgts = []
        for i, t in enumerate(texts):
            if (i + 1) % 2 == 1:
                lfts.append(t)
            else:
                rgts.append(t)
        for i, t in enumerate(lfts):
            if i in range(len(rgts)):
                Print.clean_print(
                    "§f" + Print.align(t, 35) + "§f" + Print.align(rgts[i])
                )
            else:
                Print.clean_print("§f" + Print.align(t, 35))

    def list_plugins_list(self) -> list[PluginRegData]:
        """列出插件列表

        Returns:
            list[PluginRegData]: 插件注册信息列表
        """
        Print.clean_print("§a☑ §f目前已安装的插件列表:")
        all_plugins = self.get_all_plugin_datas()
        self.make_printable_list(all_plugins)
        return all_plugins


plugin_manager = PluginManager()
