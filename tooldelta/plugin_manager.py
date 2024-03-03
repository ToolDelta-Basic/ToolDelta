import os

from .builtins import Builtins
from .color_print import Print

JsonIO = Builtins.SimpleJsonDataReader


class PluginRegData:
    def __init__(self, name: str, plugin_data: dict = {}, is_registered=True):
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
        }.get(self.plugin_type, "未知类型")


class PluginManager:
    plugin_reg_data_path = "插件注册表"
    default_reg_data = {"dotcs": {}, "classic": {}, "injected": {}, "unknown": {}}
    _plugin_datas_cache = []

    def plugin_is_registered(self, plugin_type: str, plugin_name: str):
        if not self._plugin_datas_cache:
            _, self._plugin_datas_cache = self.get_plugin_reg_name_dict_and_datas()
        for i in self._plugin_datas_cache:
            if i.name == plugin_name and i.plugin_type == plugin_type:
                return True
        return False

    def auto_register_plugin(self, plugin_type, p_data):
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
        r = JsonIO.readFileFrom(
            "主系统核心数据", self.plugin_reg_data_path, self.default_reg_data
        )
        r[plugin_data.plugin_type][plugin_data.name] = plugin_data.dump()
        JsonIO.writeFileTo("主系统核心数据", self.plugin_reg_data_path, r)

    def pop_plugin_reg_data(self, plugin_data: PluginRegData):
        r = JsonIO.readFileFrom("主系统核心数据", self.plugin_reg_data_path)
        del r[plugin_data.name]
        JsonIO.writeFileTo("主系统核心数据", self.plugin_reg_data_path, r)

    def get_plugin_reg_name_dict_and_datas(self):
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
        "返回一个全注册插件的列表"
        f_plugins: list[PluginRegData] = []
        reg_dict, reg_list = self.get_plugin_reg_name_dict_and_datas()
        for p, k in {
            "原DotCS插件": "dotcs",
            "ToolDelta组合式插件": "classic",
            "ToolDelta注入式插件": "injected",
        }.items():
            for i in os.listdir(os.path.join("插件文件", p)):
                if i not in reg_dict[k]:
                    f_plugins.append(PluginRegData(i, {"plugin-type": k}, False))
        return f_plugins + reg_list

    def make_plugin_icon(self, plugin: PluginRegData | str):
        is_reg = plugin.is_registered
        ico_colors = {"dotcs": "§6", "classic": "§b", "injected": "§d"}
        return (
            ico_colors.get(plugin.plugin_type, "§7")
            + "■ "
            + ("§a" if is_reg else "§6")
            + plugin.name
        )

    def make_printable_list(self, texts: list[str]):
        slen = len(texts)
        for i in range(slen // 2):
            text1 = texts[i]
            text2 = texts[i + slen // 2]
            Print.clean_print("§f" + Print.align(text1, 35) + "§f" + Print.align(text2))
        if slen // 2:
            text1 = texts[slen // 2 + 1]
            Print.clean_print("§f" + Print.align(text1, 35))

    def list_plugins_list(self):
        Print.clean_print("§a☑ §f目前已安装的插件列表:")
        all_plugins = self.get_2_compare_plugins_reg()
        txts = []
        for plugin in all_plugins:
            txts.append(self.make_plugin_icon(plugin))
        print(txts)
        self.make_printable_list(txts)

    @staticmethod
    def test_name_same(name: str, dirname: str):
        if name != dirname:
            raise AssertionError(f"插件名: {name} 与文件夹名({dirname}) 不一致") from None


plugin_manager = PluginManager()
