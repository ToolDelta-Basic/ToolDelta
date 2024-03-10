from tooldelta.color_print import Print
from tooldelta.starter import start_tool_delta
from tooldelta.plugin_manager import plugin_manager
from tooldelta.plugin_market import market
from tooldelta.sys_args import sys_args_to_dict

# TODO: 这是启动界面, 在此方法下写启动选项(启动ToolDelta, 插件管理, 插件市场)
def client_title():
    launch_mode = sys_args_to_dict()
    if launch_mode.get("l"):
        r = launch_mode["l"]
    else:
        Print.clean_print("§b请选择启动模式(使用启动参数 -l <启动模式> 可以跳过该页面):")
        Print.clean_print("1 - 启动 ToolDelta")
        Print.clean_print("2 - 打开 ToolDelta 插件管理器")
        Print.clean_print("3 - 打开 ToolDelta 插件市场")
        r = input("请选择:").strip()
    match r:
        case "1":
            start_tool_delta()
        case "2":
            plugin_manager.manage_plugins()
        case "3":
            market.enter_plugin_market()
        case _:
            Print.clean_print("§c不合法的模式: " + r)