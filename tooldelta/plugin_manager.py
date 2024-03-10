import os, platform, shutil

from tooldelta.builtins import Builtins
from tooldelta.color_print import Print
from tooldelta.plugin_market import market

JsonIO = Builtins.SimpleJsonDataReader

if platform.system().lower() == "windows":
    CLS_CMD = "cls"
else:
    CLS_CMD = "clear"

clear_screen = lambda: os.system(CLS_CMD)

class PluginRegData:
    # 插件注册信息类
    def __init__(self, name: str, plugin_data: dict = None, is_registered=True, is_enabled=True):
        if plugin_data is None:
            plugin_data = {}
        self.name: str = name
        if isinstance(plugin_data.get("version"), str):
            self.version: tuple = tuple(
                int(i) for i in plugin_data.get("version", "0.0.0").split(".")
            )
        else:
            self.version = plugin_data.get("version", (0, 0, 0))
        self.author: str = plugin_data.get("author", "unknown")
        self.plugin_type: str = plugin_data.get("plugin-type", "unknown")
        self.description: str = plugin_data.get("description", "")
        self.pre_plugins: dict[str, str] = plugin_data.get("pre-plugins", [])
        self.is_registered = is_registered
        if plugin_data.get("enabled") is not None:
            self.is_enabled = plugin_data["enabled"]
        else:
            self.is_enabled = is_enabled

    def dump(self):
        return {
            "author": self.author,
            "version": ".".join([str(i) for i in self.version]),
            "plugin-type": self.plugin_type,
            "description": self.description,
            "pre-plugins": self.pre_plugins,
            "enabled": self.is_enabled
        }

    @property
    def version_str(self):
        return ".".join(str(i) for i in self.version)

    @property
    def plugin_type_str(self):
        return {
            "classic": "组合式",
            "injected": "注入式",
            "dotcs": "DotCS",
            "unknown": "未知类型",
        }.get(self.plugin_type, "未知类型")


class PluginManager:
    plugin_reg_data_path = "插件注册表"
    default_reg_data = {"dotcs": {}, "classic": {}, "injected": {}, "unknown": {}}
    _plugin_datas_cache = []

    def manage_plugins(self):
        # 进入插件管理界面
        while 1:
            clear_screen()
            plugins = self.list_plugins_list()
            Print.clean_print("§f输入§bu§f更新本地所有插件, §f输入§cq§f退出")
            r = input(Print.clean_fmt("§f输入插件关键词进行选择\n(空格可分隔关键词):"))
            if r.strip() == "":
                continue
            elif r.lower() == "q":
                return
            elif r.lower() == "u":
                self.update_all_plugins(
                    self.get_plugin_reg_name_dict_and_datas()[1]
                )
            else:
                res = self.search_plugin(r, plugins)
                if res is None:
                    input()
                else:
                    self.plugin_operation(res)

    def plugin_operation(self, plugin: PluginRegData):
        # 对插件进行操作
        description_fixed = plugin.description.replace('\n', '\n    ')
        clear_screen()
        Print.clean_print(f"§d插件名: §f{plugin.name}")
        Print.clean_print(f" - 版本: {plugin.version_str}")
        Print.clean_print(f" - 作者: {plugin.author}")
        Print.clean_print(f" 描述: {description_fixed}")
        Print.clean_print(f"§f1.删除插件  2.检查更新  3.{'禁用插件' if plugin.is_enabled else '启用插件'}")
        f_dirname = {
            "dotcs": "原DotCS插件",
            "classic": "ToolDelta组合式插件",
            "injected": "ToolDelta注入式插件"
        }[plugin.plugin_type]
        match input(Print.clean_fmt("§f请选择选项: ")):
            case "1":
                r = input(
                    Print.clean_fmt("§c删除插件操作不可逆, 请输入y, 其他取消: ")
                ).lower()
                if r != "y":
                    return
                else:
                    plugin_dir = os.path.join("插件文件", f_dirname, plugin.name)
                    shutil.rmtree(
                        plugin_dir + ("+disabled" if not plugin.is_enabled else "")
                    )
                    Print.clean_print(f"§a已成功删除插件 {plugin.name}, 回车键继续")
                    self.pop_plugin_reg_data(plugin)
                    input()
                    return
            case "2":
                latest_version = market.get_latest_plugin_version(plugin.plugin_type, plugin.name)
                if latest_version is None:
                    Print.clean_print("§6无法获取其的最新版本, 回车键继续")
                elif latest_version == plugin.version_str:
                    Print.clean_print("§a此插件已经为最新版本, 回车键继续")
                else:
                    Print.clean_print(f"§a插件有新版本可用 ({plugin.version_str} => {latest_version})")
                    r = input(Print.clean_fmt("输入§a1§f=立刻更新, §62§f=取消更新: ")).strip()
                    if r == "1":
                        Print.clean_print("§a正在下载新版插件...", end = "\r")
                        market.download_plugin(plugin, market.get_datas_from_market())
                        Print.clean_print("§a插件更新完成, 回车键继续")
                        plugin.version = (int(i) for i in latest_version.split("."))
                    else:
                        Print.clean_print("§6已取消, 回车键返回")
            case "3":
                if plugin.is_enabled:
                    os.rename(
                        os.path.join("插件文件", f_dirname, plugin.name),
                        os.path.join("插件文件", f_dirname, plugin.name + "+disabled")
                    )
                else:
                    os.rename(
                        os.path.join("插件文件", f_dirname, plugin.name + "+disabled"),
                        os.path.join("插件文件", f_dirname, plugin.name)
                    )
                plugin.is_enabled = [True, False][plugin.is_enabled]
                Print.clean_print(f"§6当前插件状态为: {['§c禁用', '§a启用'][plugin.is_enabled]}")
        self.push_plugin_reg_data(plugin)
        input()

    def update_all_plugins(self, plugins: list[PluginRegData]):
        market_datas = self.latest_version = market.get_datas_from_market()["MarketPlugins"]
        need_updates: list[tuple[PluginRegData, str]] = []
        for i in plugins:
            s_data = market_datas.get(i.name)
            if s_data is None:
                continue
            elif i.version_str != s_data["version"]:
                need_updates.append((i, s_data["version"]))
        if need_updates:
            clear_screen()
            Print.clean_print("§f以下插件可进行更新:")
            for plugin, v in need_updates:
                Print.clean_print(f" - {plugin.name} §6{i.version_str}§f -> §a{v}")
            r = input(Print.clean_fmt("§f输入§a y §f开始更新, §c n §f取消: ")).strip().lower()
            if r == "y":
                for plugin, v in need_updates:
                    market.download_plugin(plugin, market_datas)
                Print.clean_print("§a全部插件已更新完成")
            else:
                Print.clean_print("§6已取消插件更新.")
            input("[Enter键继续...]")
        else:
            input(Print.clean_fmt("§a无可更新的插件. [Enter键继续]"))

    def search_plugin(self, resp, plugins):
        res = self.search_plugin_by_kw(resp.split(" "), plugins)
        if res == []:
            Print.clean_print("§c没有任何已安装插件匹配得上关键词")
            return None
        elif len(res) > 1:
            Print.clean_print("§a☑ §f关键词查找到的插件:")
            for i, plugin in enumerate(res):
                Print.clean_print(str(i + 1) + ". " + self.make_plugin_icon(plugin))
            r = Builtins.try_int(input(Print.clean_fmt("§f请选择序号: ")))
            if r is None or r not in range(1, len(res) + 1):
                Print.clean_print("§c序号无效, 回车键继续")
                return None
            else:
                return res[r - 1]
        else:
            return res[0]

    @staticmethod
    def search_plugin_by_kw(kws: list[str], plugins: list[PluginRegData]):
        res = []
        for plugin in plugins:
            if all(kw in plugin.name for kw in kws):
                res.append(plugin)
        return res

    def plugin_is_registered(self, plugin_type: str, plugin_name: str):
        if not self._plugin_datas_cache:
            _, self._plugin_datas_cache = self.get_plugin_reg_name_dict_and_datas()
        for i in self._plugin_datas_cache:
            if i.name == plugin_name and i.plugin_type == plugin_type:
                return True
        return False

    def auto_register_plugin(self, plugin_type, p_data):
        # 自动注册插件信息, 不允许直接调用
        match plugin_type:
            case "classic":
                self.push_plugin_reg_data(
                    PluginRegData(
                        p_data.name,
                        {
                            "name": p_data.name,
                            "author": p_data.author,
                            "version": p_data.version,
                            "plugin-type": "classic",
                        },
                    )
                )
            case "injected":
                self.push_plugin_reg_data(
                    PluginRegData(
                        p_data.name,
                        {
                            "name": p_data.name,
                            "author": p_data.author,
                            "version": p_data.version,
                            "description": p_data.description,
                            "plugin-type": "injected",
                        },
                    )
                )
            case "dotcs":
                assert isinstance(p_data, dict), "Not a valid dotcs plugin"
                self.push_plugin_reg_data(
                    PluginRegData(
                        p_data.get("name", "未命名插件"),
                        {
                            "name": p_data.get("name", "未命名插件"),
                            "author": p_data.get("author", "unknown"),
                            "plugin-type": "dotcs",
                        },
                    )
                )
            case _:
                Print.print_err("不合法的注册插件: " + plugin_type)

    def push_plugin_reg_data(self, plugin_data: PluginRegData):
        # 向插件注册表推送插件注册信息
        r = JsonIO.readFileFrom(
            "主系统核心数据", self.plugin_reg_data_path, self.default_reg_data
        )
        r[plugin_data.plugin_type][plugin_data.name] = plugin_data.dump()
        JsonIO.writeFileTo("主系统核心数据", self.plugin_reg_data_path, r)

    def pop_plugin_reg_data(self, plugin_data: PluginRegData):
        # 从插件注册表删除插件注册信息
        r = JsonIO.readFileFrom("主系统核心数据", self.plugin_reg_data_path)
        del r[plugin_data.plugin_type][plugin_data.name]
        JsonIO.writeFileTo("主系统核心数据", self.plugin_reg_data_path, r)

    def get_plugin_reg_name_dict_and_datas(self):
        # 返回一个表示插件所在类别下的全部已注册插件的列表, 和全部已注册插件的插件注册信息列表
        r0: dict[str, list[str]] = {"dotcs": [], "classic": [], "injected": []}
        r = JsonIO.readFileFrom(
            "主系统核心数据", self.plugin_reg_data_path, self.default_reg_data
        )
        res: list[PluginRegData] = []
        for _, r1 in r.items():
            for k, v in r1.items():
                if not isinstance(k, str) or not isinstance(v, dict):
                    raise ValueError(
                        f"获取插件注册表出现问题: 类型出错: {k.__class__.__name__}, {v.__class__.__name__}"
                    )
                v.update({"name": k})
                p = PluginRegData(k, v)
                res.append(p)
                r0[p.plugin_type].append(p.name)
        return r0, res

    def get_2_compare_plugins_reg(self):
        # 返回一个全注册插件的列表
        f_plugins: list[PluginRegData] = []
        reg_dict, reg_list = self.get_plugin_reg_name_dict_and_datas()
        for p, k in {
            "原DotCS插件": "dotcs",
            "ToolDelta组合式插件": "classic",
            "ToolDelta注入式插件": "injected",
        }.items():
            for i in os.listdir(os.path.join("插件文件", p)):
                if i.replace("+disabled", "") not in reg_dict[k]:
                    f_plugins.append(PluginRegData(i, {"plugin-type": k}, False))
        return f_plugins + reg_list
    @staticmethod
    def make_plugin_icon(plugin: PluginRegData):
        ico_colors = {"dotcs": "§6", "classic": "§b", "injected": "§d"}
        return (
            ico_colors.get(plugin.plugin_type, "§7")
            + "■ "
            + (("§a"if plugin.is_enabled else "§7") if plugin.is_registered else "§6")
            + plugin.name
        )

    def make_printable_list(self, plugins: list[PluginRegData]):
        texts = []
        for plugin in plugins:
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
                Print.clean_print("§f" + Print.align(t, 35) + "§f" + Print.align(rgts[i]))
            else:
                Print.clean_print("§f" + Print.align(t, 35))

    @staticmethod
    def test_name_same(name: str, dirname: str):
        if name != dirname:
            raise AssertionError(f"插件名: {name} 与文件夹名({dirname}) 不一致") from None

    def list_plugins_list(self):
        Print.clean_print("§a☑ §f目前已安装的插件列表:")
        all_plugins = self.get_2_compare_plugins_reg()
        self.make_printable_list(all_plugins)
        return all_plugins


plugin_manager = PluginManager()
