from enum import IntEnum
from .packets import PacketIDs


class SysStatus(IntEnum):
    """系统状态码

    LOADING: 启动器正在加载
    LAUNCHING: 启动器正在启动
    RUNNING: 启动器正在运行
    NORMAL_EXIT: 正常退出
    FB_LAUNCH_EXC: FastBuilder 启动异常
    CRASHED_EXIT: 启动器崩溃退出
    NEED_RESTART: 需要重启
    """

    LOADING = 100
    LAUNCHING = 101
    RUNNING = 102
    NORMAL_EXIT = 103
    FB_LAUNCH_EXC = 104
    CRASHED_EXIT = 105
    NEED_RESTART = 106


TOOLDELTA_LOGO = """╔═════════════════════════════════════════════════════════════════════════╗
║§9████████╗ ██████╗  ██████╗ ██╗     §b██████╗ ███████╗██╗  ████████╗ █████╗ §r║
║§9╚══██╔══╝██╔═══██╗██╔═══██╗██║     §b██╔══██╗██╔════╝██║  ╚══██╔══╝██╔══██╗§r║
║§9   ██║   ██║   ██║██║   ██║██║     §b██║  ██║█████╗  ██║     ██║   ███████║§r║
║§9   ██║   ██║   ██║██║   ██║██║     §b██║  ██║██╔══╝  ██║     ██║   ██╔══██║§r║
║§9   ██║   ╚██████╔╝╚██████╔╝███████╗§b██████╔╝███████╗███████╗██║   ██║  ██║§r║
║§9   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝§b╚═════╝ ╚══════╝╚══════╝╚═╝   ╚═╝  ╚═╝§r║
╚═════════════════════════════════════════════════════════════════════════╝§r"""
"ToolDelta标志"

TOOLDELTA_LOGO_witout_colors = """╔═════════════════════════════════════════════════════════════════════════╗
║████████╗ ██████╗  ██████╗ ██╗     ██████╗ ███████╗██╗  ████████╗ █████╗ ║
║╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██╔══██╗██╔════╝██║  ╚══██╔══╝██╔══██╗║
║   ██║   ██║   ██║██║   ██║██║     ██║  ██║█████╗  ██║     ██║   ███████║║
║   ██║   ██║   ██║██║   ██║██║     ██║  ██║██╔══╝  ██║     ██║   ██╔══██║║
║   ██║   ╚██████╔╝╚██████╔╝███████╗██████╔╝███████╗███████╗██║   ██║  ██║║
║   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚═════╝ ╚══════╝╚══════╝╚═╝   ╚═╝  ╚═╝║
╚═════════════════════════════════════════════════════════════════════════╝"""
"无颜色的ToolDelta标志"
TOOLDELTA_LOGO_mode = [
    [0, TOOLDELTA_LOGO],
    [1, TOOLDELTA_LOGO_witout_colors, (0, 100, 255), (138, 43, 226)],
    [1, TOOLDELTA_LOGO_witout_colors, (34, 139, 34), (144, 238, 144)],
    [1, TOOLDELTA_LOGO_witout_colors, (255, 165, 0), (128, 0, 128)],
    [1, TOOLDELTA_LOGO_witout_colors, (255, 182, 193), (221, 160, 221)],
]
FBLIKE_APIS = [
    "%s/api/phoenix/login",
    "%s/api/new",
    "%s",
]
"验证服务器: FastBuilder API 列表"

AUTH_SERVERS = [
    ("§7FastBuilder 官方验证服务器 §c✘不再可用", "https://user.fastbuilder.pro"),
    ("§7咕咕酱 FB验证服务器 §c✘不再可用", "https://liliya233.uk"),
    ("NetHard 验证服务器 §a✔可用", "https://nv1.nethard.pro")
]
"验证服务器列表"

TOOLDELTA_PLUGIN_DIR = "插件文件"
"插件文件路径"

TOOLDELTA_CLASSIC_PLUGIN = "ToolDelta类式插件"
"插件文件: ToolDelta 类式插件 路径"

TOOLDELTA_PLUGIN_CFG_DIR = "插件配置文件"
"插件配置文件文件夹路径"

TOOLDELTA_PLUGIN_DATA_DIR = "插件数据文件"
"插件数据文件文件夹路径"

PLUGIN_TYPE_MAPPING = {
    "classic": TOOLDELTA_CLASSIC_PLUGIN,
}
"插件属性名映射"

TDSPECIFIC_MIRROR = "https://github.tooldelta.top"
"ToolDelta的github镜像"

TDSPECIFIC_GITHUB_DOWNLOAD_URL = (
    TDSPECIFIC_MIRROR + "/https://raw.githubusercontent.com"
)
"ToolDelta镜像: github文件下载"

TDREPO_URL = (
    f"{TDSPECIFIC_MIRROR}/https://api.github.com/repos/ToolDelta-Basic/ToolDelta"
)
"ToolDelta镜像: github项目仓库"

TDDEPENDENCY_REPO_RAW = "ToolDelta-Basic/DependencyLibrary"
TDDEPENDENCY_REPO = "https://raw.githubusercontent.com/" + TDDEPENDENCY_REPO_RAW

PLUGIN_MARKET_SOURCE_OFFICIAL = "https://github.tooldelta.top/https://raw.githubusercontent.com/ToolDelta-Basic/PluginMarket/main"


class LaunchMode(IntEnum):
    LAUNCH_MODE_NEOMG_ACCESS_POINT = 1
    LAUNCH_MODE_NEOMG_ACCESS_POINT_REMOTE = 2
    LAUNCH_MODE_NEOMG_LAUNCH = 3
    LAUNCH_MODE_EULOGIST = 4


INTERNAL_LISTEN_PACKETS: set[PacketIDs] = {
    PacketIDs.Text,
    PacketIDs.PlayerList,
    PacketIDs.CommandOutput,
    PacketIDs.UpdateAbilities,
}
