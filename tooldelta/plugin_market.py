import requests, json, os, platform, shutil
import tempfile
from . import urlmethod
from .builtins import Builtins
from .color_print import Print
from typing import Dict

if platform.system().lower() == "windows":
    CLS_CMD = "cls"
else:
    CLS_CMD = "clear"

def _path_dir(path: str):
    if "/" not in path:
        return None
    else:
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

class PluginMaketPluginData:
    def __init__(self, name: str, plugin_data: dict):
        self.name: str = name
        self.version: tuple = tuple(int(i) for i in plugin_data["version"].split("."))
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
            "classic": "组合式",
            "injected": "注入式",
            "dotcs": "DotCS",
            "unknown": "未知类型"
        }.get(self.plugin_type, "unknown")

class PluginMarket:
    def enter_plugin_market(self, source_url: str):
        test_mode = False
        Print.print_inf("正在连接到插件市场..")
        try:
            if not test_mode:
                market_datas = _get_json_from_url(
                    _url_join(source_url, "market_tree.json")
                )
            else:
                with open("plugin_market/market_tree.json", "r", encoding="utf-8") as f:
                    market_datas = json.load(f)
            plugins_list: list = list(market_datas["MarketPlugins"].items())
            self.plugins_download_url = market_datas["DownloadRefURL"]
            all_indexes = len(plugins_list)
            now_index = 0
            sum_pages = int((all_indexes - 1) / 8) + 1
            now_page = 0
            last_operation = ""
            while True:
                os.system(CLS_CMD)
                Print.print_inf(market_datas["SourceName"] + ": " + market_datas["Greetings"])
                now_page = int(now_index / 8) + 1
                for i in range(now_index, now_index + 8):
                    if i in range(all_indexes):
                        plugin_data = PluginMaketPluginData(plugins_list[i][0], plugins_list[i][1])
                        Print.print_inf(f" {i + 1}. §e{plugin_data.name} §av{plugin_data.version_str} §b@{plugin_data.author} §d{plugin_data.plugin_type_str}插件", need_log=False)
                    else:
                        Print.print_inf("")
                Print.print_inf(f"§f第 {now_page} / {sum_pages} 页, 输入 §b+§f/§b- §f翻页")
                Print.print_inf("§f输入插件序号选择插件, 以查看详情", need_log=False)
                last_operation = (input(Print.fmt_info("回车键继续上次操作, §bq§f 退出, 请输入:", "§f 输入 ")) or last_operation).lower().strip()
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
                            r = self.choice_plugin(PluginMaketPluginData(plugins_list[res - 1][0], plugins_list[res - 1][1]), market_datas["MarketPlugins"])
                            if r:
                                Print.print_inf("下载插件后重启ToolDelta才能生效", need_log=False)
                                r = input(Print.fmt_info("§f输入 §cq §f退出, 其他则返回插件市场"))
                                if r.lower() == "q":
                                    break
                        else:
                            Print.print_err("超出序号范围")
                if now_index >= all_indexes:
                    now_index = 0
                elif now_index < 0:
                    now_index = max(all_indexes - 8, 0)
        except KeyError as err:
            Print.print_err(f"获取插件市场插件出现问题: 键值对错误: {err}")
            return
        except Exception as err:
            Print.print_err(f"获取插件市场插件出现问题: {err}")
            return
        os.system(CLS_CMD)
        Print.print_suc("已从插件市场返回 ToolDelta 控制台.")

    def choice_plugin(self, plugin_data: PluginMaketPluginData, all_plugins_dict: dict):
        pre_plugins_str = ', '.join([f'{k}§7v{v}' for k, v in plugin_data.pre_plugins.items()]) or "无"
        os.system(CLS_CMD)
        Print.print_inf(f"{plugin_data.name} v{plugin_data.version_str}", need_log = False)
        Print.print_inf(f"作者: §f{plugin_data.author}§7, 版本: §f{plugin_data.version_str} §b{plugin_data.plugin_type_str}", need_log = False)
        Print.print_inf(f"前置插件: §f{pre_plugins_str}", need_log = False)
        Print.print_inf(f"介绍: {plugin_data.description}", need_log = False)
        Print.print_inf("", need_log = False)
        res = input(Print.fmt_info("§f下载 = §aY§f, 取消 = §cN§f, 请输入:")).lower().strip()
        if res == "y":
            self.download_plugin(plugin_data, all_plugins_dict)
            return True
        else:
            return False

    def download_plugin(
        self,
        plugin_data: PluginMaketPluginData,
        all_plugins_dict: Dict[str, PluginMaketPluginData],
    ):
        download_paths = self.find_dirs(plugin_data)
        for plugin_name, _ in plugin_data.pre_plugins.items():
            Print.print_inf(f"正在下载 {plugin_data.name} 的前置插件 {plugin_name}")
            self.download_plugin(
                PluginMaketPluginData(plugin_name, all_plugins_dict[plugin_name]),
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
                            os.getcwd(), "插件文件", "ToolDelta组合式插件"
                        )
                    case "dotcs":
                        download_path = os.path.join(
                            os.getcwd(), "插件文件", "原DotCS插件"
                        )
                    case "injected":
                        download_path = os.path.join(
                            os.getcwd(), "插件文件", "ToolDelta注入式插件"
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
            os.makedirs(target_path, exist_ok = True)
            for root, _, files in os.walk(cache_dir):
                for filename in files:
                    source_file = os.path.join(root, filename)
                    target_file = os.path.join(
                        target_path, os.path.relpath(source_file, cache_dir)
                    )
                    os.makedirs(os.path.dirname(target_file), exist_ok=True)
                    shutil.move(source_file, target_file)
            Print.print_suc(f"成功下载插件 §f{plugin_data.name}§a 至插件文件夹")
        finally:
            # Clean up cache directory
            shutil.rmtree(cache_dir)

    def find_dirs(self, plugin_data: PluginMaketPluginData):
        try:
            data = _get_json_from_url(
                _url_join(self.plugins_download_url, "directory.json")
            )
            data_list = []
            for folder, files in data.items():
                if plugin_data.name == folder.split("/")[0]:
                    # 展开
                    for file in files:
                        data_list.append(folder + r"/"+file)
            return data_list
        except KeyError as err:
            Print.print_err(f"获取插件市场插件目录结构出现问题: 无法找到 {err}, 有可能是未来得及更新目录")
            return
        except Exception as err:
            Print.print_err(f"获取插件市场插件目录结构出现问题: {err}")
            return


market = PluginMarket()
