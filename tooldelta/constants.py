"ToolDelta 常量定义"

PRG_NAME = "ToolDelta"
"程序名"

PLUGIN_MARKET_SOURCE_OFFICIAL = (
    "https://tdload.tblstudio.cn/"
    "https://raw.githubusercontent.com/ToolDelta/ToolDelta-PluginMarket/main"
)
"插件市场源"

LAUNCH_CFG: dict = {
    "启动器启动模式(请不要手动更改此项, 改为0可重置)": 0,
    "验证服务器地址(更换时记得更改fbtoken)": "",
    "是否记录日志": True,
    "是否使用github镜像": True,
    "插件市场源": PLUGIN_MARKET_SOURCE_OFFICIAL,
}
"默认登录配置"

LAUNCH_CFG_STD: dict = {
    "启动器启动模式(请不要手动更改此项, 改为0可重置)": int,
    "验证服务器地址(更换时记得更改fbtoken)": str,
    "是否记录日志": bool,
    "是否使用github镜像": bool,
    "插件市场源": str,
}
"默认登录配置标准验证格式"

LAUNCHER_NEOMEGA_STD: dict = {
    "服务器号": int,
    "密码": int,
    "验证服务器地址(更换时记得更改fbtoken)": str,
}
"启动器：NeOmega 启动配置验证格式"

LAUNCHER_NEOMEGA_DEFAULT: dict = {
    "服务器号": 0,
    "密码": 0,
    "验证服务器地址(更换时记得更改fbtoken)": "",
}
"启动器：NeOmega 默认启动配置"

LAUNCHER_BEWS_STD: dict = {"服务端开放地址": str}
"启动器：BEWSServer 启动配置验证格式"

LAUNCHER_BEWS_DEFAULT: dict = {"服务端开放地址": ""}
"启动器：BEWSServer 默认启动配置"

FB_APIS = [
    "https://api.fastbuilder.pro/api/phoenix/login",
    "https://api.fastbuilder.pro/api/new",
    "https://api.fastbuilder.pro/api/api",
    "https://api.fastbuilder.pro/api/login",
    "https://api.fastbuilder.pro",
]
"验证服务器：FastBuilder API 列表"


GUGU_APIS = [
    "https://liliya233.uk/api/phoenix/login",
    "https://liliya233.uk/api/new",
    "https://liliya233.uk",
]
"验证服务器：Liliya API 列表"

AUTH_SERVERS = [
    ("FastBuilder 官方验证服务器", "https://api.fastbuilder.pro"),
    ("咕咕酱 FB验证服务器", "https://liliya233.uk"),
]
"验证服务器列表"

TOOLDELTA_PLUGIN_DIR = "插件文件"
"插件文件路径"

TOOLDELTA_CLASSIC_PLUGIN = "ToolDelta类式插件"
"插件文件：ToolDelta 类式插件 路径"

TOOLDELTA_INJECTED_PLUGIN = "ToolDelta注入式插件"
"插件文件：ToolDelta 注入式插件 路径"

TOOLDELTA_PLUGIN_DATA_DIR = "插件数据文件"
"插件数据文件文件夹路径"

PLUGIN_TYPE_MAPPING = {
    "classic": TOOLDELTA_CLASSIC_PLUGIN,
    "injected": TOOLDELTA_INJECTED_PLUGIN,
}
"插件属性名映射"

TDSPECIFIC_MIRROR = "https://tdload.tblstudio.cn"
"ToolDelta专用镜像"
