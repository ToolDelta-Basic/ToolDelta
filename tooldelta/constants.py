from typing import List
from tooldelta.launch_cli import FrameFBConn, FrameNeOmg, FrameNeOmgRemote
from tooldelta.cfg import Cfg

PLUGIN_MARKET_SOURCE_OFFICIAL = "https://mirror.ghproxy.com/raw.githubusercontent.com/ToolDelta/ToolDelta-PluginMarket/main"

LAUNCHERS: List[
    tuple[str, type[FrameFBConn | FrameNeOmg | FrameNeOmgRemote]]
] = [
    (
        "FastBuilder External 模式 (经典模式) §c(已停止维护, 无法适应新版本租赁服!)",
        FrameFBConn,
    ),
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
    "插件市场源": PLUGIN_MARKET_SOURCE_OFFICIAL,
}

LAUNCH_CFG_STD: dict = {
    "服务器号": int,
    "密码": int,
    "启动器启动模式(请不要手动更改此项, 改为0可重置)": Cfg.NNInt,
    "验证服务器地址(更换时记得更改fbtoken)": str,
    "是否记录日志": bool, 
    "插件市场源": str,
}

FB_APIS = [
    "https://api.fastbuilder.pro/api/phoenix/login",
    "https://api.fastbuilder.pro/api/new",
    "https://api.fastbuilder.pro/api/api",
    "https://api.fastbuilder.pro/api/login",
    "https://api.fastbuilder.pro",
]

AUTH_SERVERS = [
    ("FastBuilder 官方验证服务器", "https://api.fastbuilder.pro"),
    ("咕咕酱 FB验证服务器", "https://liliya233.uk"),
]