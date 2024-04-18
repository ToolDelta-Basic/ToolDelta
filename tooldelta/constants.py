" ToolDelta 常量定义 "
from typing import List
from .cfg import Cfg
from .launch_cli import FrameNeOmg, FrameNeOmgRemote
PRG_NAME = "ToolDelta"

PLUGIN_MARKET_SOURCE_OFFICIAL = "https://tdload.tblstudio.cn/https://raw.githubusercontent.com/ToolDelta/ToolDelta-PluginMarket/main"

LAUNCHERS: List[
    tuple[str, type[FrameNeOmg | FrameNeOmgRemote]]
] = [
    ("NeOmega 框架 (NeOmega模式, 租赁服适应性强, 推荐)", FrameNeOmg),
    (
        "NeOmega 框架 (NeOmega连接模式, 需要先启动对应的neOmega接入点)",
        FrameNeOmgRemote,
    ),
]

LAUNCH_CFG: dict = {
    "服务器号": 0,
    "密码": 0,
    "启动器启动模式(请不要手动更改此项, 改为0可重置)": 0,
    "验证服务器地址(更换时记得更改fbtoken)": "",
    "是否记录日志": True,
    "是否使用github镜像": True,
    "插件市场源": PLUGIN_MARKET_SOURCE_OFFICIAL
}

LAUNCH_CFG_STD: dict = {
    "服务器号": int,
    "密码": int,
    "启动器启动模式(请不要手动更改此项, 改为0可重置)": Cfg.NNInt,
    "验证服务器地址(更换时记得更改fbtoken)": str,
    "是否记录日志": bool,
    "是否使用github镜像": bool,
    "插件市场源": str
}

FB_APIS = [
    "https://api.fastbuilder.pro/api/phoenix/login",
    "https://api.fastbuilder.pro/api/new",
    "https://api.fastbuilder.pro/api/api",
    "https://api.fastbuilder.pro/api/login",
    "https://api.fastbuilder.pro",
]


GUGU_APIS = [
    "https://liliya233.uk/api/phoenix/login",
    "https://liliya233.uk/api/new",
    "https://liliya233.uk",
]

AUTH_SERVERS = [
    ("FastBuilder 官方验证服务器", "https://api.fastbuilder.pro"),
    ("咕咕酱 FB验证服务器", "https://liliya233.uk"),
]

TOOLDELTA_PLUGIN_DIR = "插件文件"
TOOLDELTA_CLASSIC_PLUGIN = "ToolDelta类式插件"
TOOLDELTA_INJECTED_PLUGIN = "ToolDelta注入式插件"
