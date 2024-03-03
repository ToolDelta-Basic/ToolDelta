import os

from .builtins import Builtins
from .color_print import Print

JsonIO = Builtins.SimpleJsonDataReader


class PluginRegData:
    def __init__(self, name: str, plugin_data: dict = {}, is_registered=True):
        self.name: str = name
        self.version: tuple = tuple(
            int(i) for i in plugin_data.get("version", "0.0.0").split(".")
        )
        self.author: str = plugin_data.get("author")
        self.plugin_type: str = plugin_data.get("plugin-type")
        self.description: str = plugin_data.get("description")
        self.pre_plugins: dict[str, str] = plugin_data.get("pre-plugins")
        self.is_registered = is_registered

    def dump(self):
        return {
            "author": self.author,
            "version": ".".join([str(i) for i in self.version]),
            "plugin-type": self.plugin_type,
            "description": self.description,
            "pre-plugins": self.pre_plugins,
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
        }.get(self.plugin_type, "unknown")


class PluginManager:
    plugin_reg_data_path = "插件注册表"
    default_reg_data = {"dotcs": {}, "classic": {}, "injected": {}}

    def push_plugin_reg_data(self, plugin_data: PluginRegData):
        r = JsonIO.readFileFrom(
            "主系统核心数据", self.plugin_reg_data_path, self.default_reg_data
        )
        r[plugin_data.name] = plugin_data.dump()
        JsonIO.writeFileTo("主系统核心数据", self.plugin_reg_data_path, r)

    def pop_plugin_reg_data(self, plugin_data: PluginRegData):
        r = JsonIO.readFileFrom("主系统核心数据", self.plugin_reg_data_path)
        del r[plugin_data.name]
        JsonIO.writeFileTo("主系统核心数据", self.plugin_reg_data_path, r)

    def get_plugin_reg_datas(self):
        r = JsonIO.readFileFrom(
            "主系统核心数据", self.plugin_reg_data_path, self.default_reg_data
        )
        res: list[PluginRegData] = []
        for _, r1 in r.items():
            for k, v in r1.items():
                res.append(PluginRegData(k, v.update({"name": k})))
        return res

    def get_2_compare_plugins_reg(self):
        r0: dict[str, list[str]] = {"dotcs": [], "classic": [], "injected": []}
        r1 = self.get_plugin_reg_datas()
        for p, k in {
            "原DotCS插件": "dotcs",
            "ToolDelta组合式插件": "classic",
            "ToolDelta注入式插件": "injected",
        }.items():
            for i in os.listdir(os.path.join("插件文件", p)):
                r0[k].append(PluginRegData(i, {"plugin-type": k}, False))
        return r0, r1

    def make_plugin_icon(self, plugin: PluginRegData | str, plugin_type="dotcs"):
        is_reg = plugin.is_registered
        ico_colors = {"dotcs": "§6", "classic": "§b", "injected": "§d"}
        return (
            ico_colors.get(plugin_type, "§7")
            + "■ "
            + ("§a" if is_reg else "§6")
            + plugin.name
        )

    def make_printable_list(self, texts: list[str]):
        slen = len(texts)
        for i in range(slen // 2):
            text1 = texts[i]
            text2 = texts[i + slen // 2]
            Print.clean_print("§f" + Print.align(text1, 25) + "§f" + Print.align(text2))

    def list_plugins_list(self):
        Print.clean_print("§a☑ §f目前已安装的插件列表:")
        r0, r1 = self.get_2_compare_plugins_reg()
        txts = []
        lefts = r0.copy()
        for plugin in r1:
            lefts[plugin.plugin_type].remove(plugin.name)
            txts.append(self.make_plugin_icon(plugin))
        for ptype, plugins in lefts.items():
            for plugin_name in plugins:
                txts.append(self.make_plugin_icon(plugin_name, ptype))
        self.make_printable_list(txts)
