"启动页面"

import os
import time
import traceback

from random import choice
from .utils import fmts, sys_args
from .constants import TOOLDELTA_LOGO_mode
from .internal.config_loader import ConfigLoader
from .plugin_manager import plugin_manager
from .plugin_market import market
from .starter import start_tool_delta, init_cfg_only
from .version import get_tool_delta_version


def client_title() -> None:
    """选择启动模式"""
    try:
        launch_args = sys_args.sys_args_to_dict()
        if opt_str := launch_args.get("optadd"):
            more_opts = {
                str(i + 7): (k, v)
                for (i, (k, v)) in enumerate(sys_args.parse_addopt(opt_str).items())
            }
        else:
            more_opts = {}
        if "h" in launch_args or "help" in launch_args:
            sys_args.print_help()
            return
        elif "v" in launch_args or "version" in launch_args:
            print(".".join(str(i) for i in get_tool_delta_version()))
            return
        is_faststart = os.path.isfile("快速启动.sig")
        launch_section = ""
        if launch_args.get("l"):
            if not isinstance(launch_args["l"], str):
                raise ValueError("启动模式参数不合法")
            launch_section = launch_args["l"]
        elif is_faststart:
            fmts.clean_print("§a快速启动功能已打开, 将跳过选择界面")
            fmts.clean_print("删除本地的 §f快速启动.sig§r 文件即可取消快速启动功能")
            time.sleep(0.5)
            start_tool_delta()
            return
        while 1:
            if launch_section:
                r = launch_section
            else:
                text = choice(TOOLDELTA_LOGO_mode)
                if text[0] == 0:
                    print(fmts.clean_fmt(text[1]))
                elif text[0] == 1:
                    print(fmts.print_gradient(text[1], text[2], text[3]))
                if "title" in sys_args.sys_args_to_dict():
                    fmts.clean_print(launch_args["title"] or "")
                fmts.clean_print(
                    "§a请选择启动模式§6(使用启动参数 -l <启动模式> 可以跳过该页面):"
                )
                fmts.clean_print("1 - §b启动 ToolDelta")
                fmts.clean_print("2 - §d打开插件管理器")
                fmts.clean_print("3 - §d打开插件市场")
                fmts.clean_print("4 - §6初始化所有插件配置")
                fmts.clean_print("5 - §a修改启动配置")
                fmts.clean_print("6 - §c开启直接启动模式")
                for i, (opt_name, _) in enumerate(more_opts.values()):
                    fmts.clean_print(f"{i + 7} - {opt_name}")
                fmts.clean_print("q - §7退出")
                r = input("请选择: ").strip()
            launch_section = ""
            match r:
                case "1":
                    start_tool_delta()
                    return
                case "2":
                    plugin_manager.manage_plugins()
                case "3":
                    market.enter_plugin_market()
                case "4":
                    init_cfg_only()
                case "5":
                    ConfigLoader.change_config()
                case "6":
                    open("快速启动.sig", "wb").close()
                    fmts.clean_print("§a快速启动模式已开启")
                    fmts.clean_print(
                        "§6删除本地的 §f快速启动.sig§6 文件即可取消快速启动功能"
                    )
                    time.sleep(1)
                case "q":
                    fmts.clean_print("§aToolDelta 已退出.")
                    return
                case _:
                    if r in more_opts.keys():
                        os.system(more_opts[r][1])
                    else:
                        fmts.clean_print("§c不合法的启动模式: " + r)
                    return
    except (EOFError, SystemExit):
        pass
    except Exception:
        fmts.print_err("ToolDelta 运行过程中出现问题：" + traceback.format_exc())
