import requests, json, os
from . import urlmethod
from .builtins import Builtins
from .color_print import Print

class PluginMaketPluginData:
    def __init__(self, name: str, plugin_data: dict):
        self.name: str = name
        self.version: str = tuple(int(i) for i in plugin_data["version"].strip("."))
        self.author: str = plugin_data["author"]
        self.plugin_type: str = plugin_data["plugin-type"]
        self.description: str = plugin_data["description"]
        self.pre_plugins: dict[str, str] = plugin_data["pre-plugins"]

    @property
    def version_str(self):
        return ".".join(str(i) for i in self.version)
    
    @property
    def plugin_type_str(self):
        return {
            "classic": "组合式插件",
            "injected": "注入式插件",
            "dotcs": "DotCS插件",
            "unknown": "未知插件类型"
        }.get(self.plugin_type, "unknown")

class PluginMarket:
    def list_and_find_url(self):
        try:
            res = json.loads(requests.get(
                "https://mirror.ghproxy.com/https://raw.githubusercontent.com/SuperScript-PRC/ToolDelta/main/plugin_market/market_tree.json"
            ).text)
            plugins_list: list = list(res["MarketPlugins"].values())
            all_indexes = len(plugins_list)
            now_index = 0
            while 1:
                os.system("cls")
                res = ""
                for i in range(now_index, now_index + 8):
                    if i in range(all_indexes):
                        plugin_data = PluginMaketPluginData(plugins_list[i][0], plugins_list[i][1])
                        Print.print_inf(f" {i + 1}. {plugin_data.name} v{plugin_data.version_str} @{plugin_data.author} §b{plugin_data.plugin_type_str}插件", need_log = False)
                    else:
                        print()
                Print.print_inf("§f输入 §b+§f/§b- §f翻页, 输入插件序号选择插件", need_log = False)
                res = input(Print.fmt_info("回车键继续上次操作, §bq§f 退出, 请输入:", "输入")).lower().strip() or res
                if res == "+":
                    i += 8
                elif res == "-":
                    i -= 8
                elif res == "q":
                    return
                res = Builtins.try_int(res)
                if res:
                    if res in range(1, all_indexes + 1):
                        self.choice_plugin(PluginMaketPluginData(plugins_list[res - 1][0], plugins_list[res - 1][1]), res["MarketPlugins"])
                    else:
                        Print.print_err("超出序号范围")
                if i > all_indexes:
                    i = 0
                elif i < 0:
                    i = all_indexes

        except Exception as err:
            Print.print_err(f"获取插件市场插件出现问题: {err}")

    def choice_plugin(self, plugin_data: PluginMaketPluginData, all_plugins_dict: dict):
        pre_plugins_str = ', '.join([f'{k}:{v}' for k, v in plugin_data.pre_plugins.items()]) or "无"
        os.system("cls")
        Print.print_inf(f"{plugin_data.name} v{plugin_data.version}", need_log = False)
        Print.print_inf(f"§7作者: §f{plugin_data.author}§7, 版本: §f{plugin_data.version_str} §b{plugin_data.plugin_type_str}", need_log = False)
        Print.print_inf(f"前置插件: {pre_plugins_str}", need_log = False)
        Print.print_inf(f"介绍: {plugin_data.description}", need_log = False)
        res = input(Print.fmt_info("§f下载=§aY§f, 取消=§cN§f, 请输入:","输入")).lower().strip()
        if res == "y":
            self.download_plugin(all_plugins_dict[plugin_data.name], all_plugins_dict)
        else:
            return
        
    def download_plugin(self, plugin_data: PluginMaketPluginData, all_plugins_dict):
        download_paths = plugin_data["dirs"] + ["__init__.py"]
        for path in download_paths:
            if not path.strip():
                Print.print_war("下载路径为空, 跳过")
                continue
            for plugin_name, _ in plugin_data.pre_plugins:
                # 下载前置插件
                self.download_plugin(PluginMaketPluginData(plugin_name, all_plugins_dict[plugin_name]))
            url = (
                "https://mirror.ghproxy.com/https://raw.githubusercontent.com/SuperScript-PRC/ToolDelta/main/plugin_market/"
                 + plugin_data.name + "/" + path
            )
            match plugin_data.plugin_type:
                case "classic":
                    download_path = os.path.join(os.getcwd(), "插件文件", "ToolDelta组合式插件")
                case "dotcs":
                    download_path = os.path.join(os.getcwd(), "插件文件", "原DotCS插件")
                case "injected":
                    download_path = os.path.join(os.getcwd(), "插件文件", "ToolDelta注入式插件")
                case _:
                    raise Exception(f"未知插件类型: {plugin_data.plugin_type}, 你可能需要通知ToolDelta项目开发组解决")
            if "." in path.split("/")[-1]:
                # 这应该是个文件了, 有文件后缀名
                urlmethod.download_file(url, os.path.join(download_path, plugin_data.name, path))
            else:
                os.makedirs(download_path)