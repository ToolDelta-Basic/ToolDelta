from typing import Callable
from orjson import JSONDecodeError
from libs.packets import Packet_CommandOutput
from io import TextIOWrapper
import threading

VERSION = tuple[int, int, int]

class _Print:
    def _mccolor_console_st1(this, text: str):...
    def print_with_info(this, text: str, info: str, **print_kwargs):...
    def print_err(this, text: str, **print_kwargs):"输出报错信息"
    def print_inf(this, text: str, **print_kwargs):"输出一般信息"
    def print_suc(this, text: str, **print_kwargs):"输出成功信息"
    def print_war(this, text: str, **print_kwargs):"输出警告信息"
    def fmt_info(this, text: str, info: str) -> str:"按照[INFO]的格式返回PRINT字符串"

class Builtins:
    class SimpleJsonDataReader:
        class DataReadError(JSONDecodeError):...
        @staticmethod
        def SafeOrJsonDump(obj: str | dict | list, fp: TextIOWrapper):...
        @staticmethod
        def SafeOrJsonLoad(fp: TextIOWrapper) -> dict:...
        @staticmethod
        def readFileFrom(plugin_name: str, file: str, default: dict = None) -> any:"读取插件的json数据文件, 如果没有, 则新建一个空的"
        @staticmethod
        def writeFileTo(plugin_name: str, file: str, obj):"写入插件的json数据文件"
    class ArgsReplacement:
        def __init__(this, kw: dict[str, any]):...
        def replaceTo(this, __sub: str) -> str:...

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
    class FrameBasic:
        max_connect_fb_time: int
        connect_fb_start_time: int
        data_path: str
        system_version: VERSION
    def __init__(this):...
    def get_game_control(this):
        return GameManager()
    def getFreePort(this, start = 8080, usage = "none") -> int | None:...
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
    def __init__(this, frame: Frame):
        this.linked_frame = frame
    def sendwocmd(this, cmd: str):...
    def sendcmd(this, cmd: str, waitForResp: bool = False, timeout: int = 30) -> str | Packet_CommandOutput:...
    def sendwscmd(this, cmd: str, waitForResp: bool = False, timeout: int = 30) -> str | Packet_CommandOutput:...
    def sendfbcmd(this, cmd: str):...
    def sendPacket(this, pktType: int, pkt: dict):...
    def say_to(this, target: str, msg: str):
        this.sendwocmd("tellraw " + target + ' {"rawtext":[{"text":"' + msg + '"}]}')
    def player_title(this, target: str, text: str):
        this.sendwocmd(f"title {target} title {text}")
    def player_subtitle(this, target: str, text: str):
        this.sendwocmd(f"title {target} subtitle {text}")
    def player_actionbar(this, target: str, text: str):
        this.sendwocmd(f"title {target} actionbar {text}")

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
        def __init__(this, name):...
    class PluginAPIVersionError(ModuleNotFoundError):
        def __init__(this, name, m_ver, n_ver):...
    plugins: list[Plugin] = []
    plugins_funcs: dict[str, list]
    listen_packets = []
    old_dotcs_env = {}
    linked_frame = None
    packet_funcs: dict[str, list[Callable]] = {}
    plugins_api = {}
    dotcs_global_vars = {}
    excType = 0
    PRG_NAME = ""
    def add_plugin(plugin: Plugin):...
    def getPluginAPI(this, apiName: str, min_version: tuple = None):...
    def checkSystemVersion(this, need_vers: VERSION):...

class Cfg:
    class ConfigError(Exception):
        def __init__(this, errStr: str, errPos: list):
            this.errPos = errPos
            this.args = (errStr,)
    class ConfigKeyError(ConfigError):...
    class ConfigValueError(ConfigError):...
    class VersionLowError(ConfigError):...
    class PInt(int):"正整数"
    class NNInt(int):"非负整数"
    class PFloat(float):"正浮点小数"
    class NNFloat(float):"非负浮点小数"

    def get_cfg(this, path: str, standard_type: dict):...
    def default_cfg(this, path: str, default: dict, force: bool = False):...
    def exists(this, path: str):...
    def checkDict(this, patt: dict, cfg: dict, __nowcheck: list = []):...
    def checkList(this, patt, lst: list, __nowcheck: list = []):...
    def getPluginConfigAndVersion(this, pluginName: str, standardType: dict, default: dict, default_vers: VERSION):...

def add_plugin(plugin: Plugin):...
def addPluginAPI(this, apiName: str, version: tuple):...
def listen_packet(packetID: int):...
plugins: PluginGroup
Config: Cfg
Print: _Print
