from typing import Callable, TypeVar, Any, Tuple
from ujson import JSONDecodeError
from libs.packets import Packet_CommandOutput
from io import TextIOWrapper
import threading

VERSION = tuple[int, int, int]
Receiver = TypeVar("Receiver")

class _Print:
    def _mccolor_console_st1(self, text: str):...
    def print_with_info(self, text: str, info: str, **print_kwargs):...
    def print_err(self, text: str, **print_kwargs):"输出报错信息"
    def print_inf(self, text: str, **print_kwargs):"输出一般信息"
    def print_suc(self, text: str, **print_kwargs):"输出成功信息"
    def print_war(self, text: str, **print_kwargs):"输出警告信息"
    def fmt_info(self, text: str, info: str) -> str:...;"按照[INFO]的格式返回PRINT字符串"

class Builtins:
    class SimpleJsonDataReader:
        class DataReadError(JSONDecodeError):...
        @staticmethod
        def SafeJsonDump(obj: str | dict | list, fp: TextIOWrapper):...
        @staticmethod
        def SafeJsonLoad(fp: TextIOWrapper) -> dict:...
        @staticmethod
        def readFileFrom(plugin_name: str, file: str, default: dict | None = None) -> Any:...;"读取插件的json数据文件, 如果没有, 则新建一个空的"
        @staticmethod
        def writeFileTo(plugin_name: str, file: str, obj):"写入插件的json数据文件"
    class ArgsReplacement:
        def __init__(self, kw: dict[str, Any]):...
        def replaceTo(self, __sub: str) -> str:...
    class TMPJson:
        @staticmethod
        def loadPathJson(path: str, needFileExists: bool = True):"初始化一个json文件路径, 之后可对其进行读取和写入, 速度快"
        @staticmethod
        def unloadPathJson(path: str):"卸载一个json文件路径, 之后不可对其进行读取和写入"
        @staticmethod
        def read(path: str):"读取json文件路径缓存的信息"
        @staticmethod
        def write(path: str, obj: Any):"向该json文件路径写入信息并缓存, 一段时间或系统关闭时会将其写入磁盘内"
    @staticmethod
    def SimpleFmt(kw: dict[str, Any], __sub: str) -> str:...
    @staticmethod
    def simpleAssert(cond: Any, exc):...
    @staticmethod
    def try_int(arg) -> int | None:...

class Frame:
    class ThreadExit(SystemExit):...
    class SystemVersionException(OSError):...
    class FrameBasic:
        system_version: VERSION
        max_connect_fb_time: int
        connect_fb_start_time: int
        data_path: str
    class ClassicThread(threading.Thread):
        def __init__(self, func: Callable, args: tuple = (), **kwargs):...
        def run(self):...
        def get_id(self):...
        def stop(self):...
    def __init__(self):...
    def get_game_control(self):
        return GameManager(Frame())
    def getFreePort(self, start = 8080, usage = "none") -> int | None:...
    sys_data: FrameBasic
    
class GameManager:
    command_req = []
    command_resp = {}
    players_uuid = {}
    allplayers = []
    bot_name = ""
    linked_frame: Frame
    pkt_unique_id: int = 0
    pkt_cache: list = []
    require_listen_packet_list = [9, 79, 63]
    store_uuid_pkt = None
    requireUUIDPacket = True
    def __init__(self, frame: Frame):
        self.linked_frame = frame
    def sendwocmd(self, cmd: str):...
    def sendcmd(self, cmd: str, waitForResp: bool = False, timeout: int = 30) -> str | Packet_CommandOutput:...
    def sendwscmd(self, cmd: str, waitForResp: bool = False, timeout: int = 30) -> str | Packet_CommandOutput:...
    def sendfbcmd(self, cmd: str):...
    def sendPacket(self, pktType: int, pkt: dict):...
    def say_to(self, target: str, msg: str):
        self.sendwocmd("tellraw " + target + ' {"rawtext":[{"text":"' + msg + '"}]}')
    def player_title(self, target: str, text: str):
        self.sendwocmd(f"title {target} title {text}")
    def player_subtitle(self, target: str, text: str):
        self.sendwocmd(f"title {target} subtitle {text}")
    def player_actionbar(self, target: str, text: str):
        self.sendwocmd(f"title {target} actionbar {text}")

class Plugin:
    name = "<未命名插件>"
    version = (0, 0, 1)
    author = "?"
    require_listen_packets = []
    dotcs_old_type = False

class PluginAPI:
    name = "<未命名api>"
    version = (0, 0, 1)

class PluginGroup:
    class PluginAPINotFoundError(ModuleNotFoundError):
        def __init__(self, name):...
    class PluginAPIVersionError(ModuleNotFoundError):
        def __init__(self, name, m_ver, n_ver):...
    plugins: list[Plugin] = []
    plugins_funcs: dict[str, list]
    listen_packet_ids = []
    old_dotcs_env = {}
    linked_frame = None
    packet_funcs: dict[str, list[Callable]] = {}
    plugins_api = {}
    dotcs_global_vars = {}
    excType = 0
    PRG_NAME = ""
    @staticmethod
    def get_plugin_api(apiName: str, min_version: tuple | None = None) -> Tuple[dict, VERSION]:...
    def add_plugin(self, plugin: Plugin) -> Receiver:... # type: ignore
    def add_plugin_api(self, apiName: str) -> Receiver:... # type: ignore
    def add_packet_listener(self, pktID) -> Receiver:... # type: ignore
    @staticmethod
    def checkSystemVersion(need_vers: VERSION):...

class Cfg:
    "配置文件检测类"
    class Group:
        "json键组"
        def __init__(self, *keys):...
        def __repr__(self) -> str:...
    class UnneccessaryKey:
        "非必须的json键"
        def __init__(self, key):...
        def __repr__(self) -> str:...
    class ConfigError(Exception):
        def __init__(self, errStr: str, errPos: list):
            self.errPos = errPos
            self.args = (errStr,)
    class ConfigKeyError(ConfigError):...
    class ConfigValueError(ConfigError):...
    class VersionLowError(ConfigError):...
    class PInt(int):"正整数"
    class NNInt(int):"非负整数"
    class PFloat(float):"正浮点小数"
    class NNFloat(float):"非负浮点小数"

    def get_cfg(self, path: str, standard_type: dict):...
    def default_cfg(self, path: str, default: dict, force: bool = False):...
    def exists(self, path: str):...
    def checkDict(self, patt: dict, cfg: dict, __nowcheck: list = []):...
    def checkList(self, patt, lst: list, __nowcheck: list = []):...
    def getPluginConfigAndVersion(self, pluginName: str, standardType: dict, default: dict, default_vers: VERSION) -> Tuple[VERSION, dict]:...

plugins: PluginGroup
Config: Cfg
Print: _Print
