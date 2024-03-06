from tooldelta.plugin_load.classic_plugin import Plugin
from tooldelta.color_print import Print
from tooldelta.plugin_load import plugin_is_enabled
import re
import os
import sys

NOT_IMPORTALL_RULE = re.compile(r"from .* import \*")


def _import_original_dotcs_plugin(
    plugin_code: str, old_dotcs_env: dict, module_env: dict, plugin_group
):
    # dotcs插件太不规范了!!
    plugin_body = Plugin()
    plugin_body.dotcs_old_type = True
    old_dotcs_env.update(module_env)
    runcode_tmp = {}
    plugin_code_lines = plugin_code.split("\n")
    _dotcs_runcode = {}
    evts = {}
    packetFuncs = []
    while 1:
        if "" in plugin_code_lines:
            plugin_code_lines.remove("")
        else:
            break
    plugin_start = -1
    plugin_end = 0
    plugin_prev_type = ""

    for line in range(len(plugin_code_lines)):
        if "import *" in plugin_code_lines[line]:
            Print.print_war(
                f"DotCS插件 存在异常的代码 'import *', 已自动替换为 pass: §7{line} §f|{plugin_code_lines[line]}"
            )
            plugin_code_lines[line] = NOT_IMPORTALL_RULE.sub(
                "pass", plugin_code_lines[line]
            )
        if plugin_code_lines[line].startswith("# PLUGIN TYPE: "):
            if plugin_start + 1:
                plugin_end = line
                runcode_tmp[plugin_prev_type] = "\n".join(
                    plugin_code_lines[plugin_start:plugin_end]
                )
            plugin_start = line + 1
            plugin_prev_type = plugin_code_lines[line].strip("# PLUGIN TYPE: ")
    if plugin_start + 1:
        plugin_end = len(plugin_code_lines)
        runcode_tmp[plugin_prev_type] = "\n".join(
            plugin_code_lines[plugin_start:plugin_end]
        )

    old_dotcs_env.update({"plugin_group": plugin_group})
    fun_exec_code = ""
    for k in runcode_tmp:
        match k:
            case "def":
                fun_exec_code = "def on_def():\n "
            case "init":
                fun_exec_code = "def on_inject():\n "
            case "player prejoin":
                fun_exec_code = "def on_player_prejoin(playername):\n "
            case "player join":
                fun_exec_code = "def on_player_join(playername):\n "
            case "player message":
                fun_exec_code = "def on_player_message(playername, msg):\n "
            case "player leave":
                fun_exec_code = "def on_player_leave(playername):\n "
            case "player death":
                fun_exec_code = "def on_player_death(playername, killer, msg):\n "
            case "repeat 1s":
                fun_exec_code = "def repeat1s():\n "
            case "repeat 10s":
                fun_exec_code = "def repeat10s():\n "
            case "repeat 30s":
                fun_exec_code = "def repeat30s():\n "
            case "repeat 1m":
                fun_exec_code = "def repeat1m():\n "
            case _:
                if k.startswith("packet"):
                    try:
                        pktID = int(k.split()[1])
                        if pktID == -1:
                            Print.print_war("§c无法监听任意数据包, 已跳过")
                        else:
                            fun_exec_code = (
                                f"def packet_{pktID}(jsonPkt):\n packetType={pktID}\n "
                            )
                            plugin_body.add_req_listen_packet(pktID)
                            packetFuncs.append((pktID, f"packet_{pktID}"))
                    except:
                        Print.print_war(f"§c不合法的监听数据包ID： {k}, 已跳过")
                else:
                    raise Exception(f"无法识别的DotCS插件事件样式： {k}")
        # DotCS 有太多的插件都会出现作用域问题, 在此只能这么修复了
        p_code = (
            fun_exec_code
            + """globals().update(plugin_group.dotcs_global_vars)\n """
            + runcode_tmp[k].replace("\n", "\n ")
            + "\n plugin_group.dotcs_global_vars.update(locals())"
        )
        try:
            exec(p_code, old_dotcs_env, _dotcs_runcode)
        except Exception as err:
            Print.print_err(f"DotCS插件 <{plugin_body.name}> 出错: {err}")
            raise
    newPacketFuncs = []
    for pkt, funcname in packetFuncs:
        newPacketFuncs.append((pkt, _dotcs_runcode[funcname]))
    for codetype in [
        "on_def",
        "on_inject",
        "on_player_prejoin",
        "on_player_join",
        "on_player_message",
        "on_player_death",
        "on_player_leave",
    ]:
        if _dotcs_runcode.get(codetype):
            evts[codetype] = [plugin_body.name, _dotcs_runcode[codetype]]
        if _dotcs_runcode.get("repeat1s"):
            evts["repeat1s"] = [plugin_body.name, _dotcs_runcode["repeat1s"]]
        if _dotcs_runcode.get("repeat10s"):
            evts["repeat10s"] = [plugin_body.name, _dotcs_runcode["repeat10s"]]
        if _dotcs_runcode.get("repeat30s"):
            evts["repeat30s"] = [plugin_body.name, _dotcs_runcode["repeat30s"]]
        if _dotcs_runcode.get("repeat1m"):
            evts["repeat1m"] = [plugin_body.name, _dotcs_runcode["repeat1m"]]
    return plugin_body, evts, newPacketFuncs


def read_plugin_from_old(plugin_grp, module_env: dict):
    PLUGIN_PATH = os.path.join(os.getcwd(), "插件文件/原DotCS插件")
    sys.path.append(PLUGIN_PATH)
    dotcs_env = plugin_grp.linked_frame._get_old_dotcs_env()
    files = os.listdir(PLUGIN_PATH)
    files.sort()
    for file in files:
        if not plugin_is_enabled(file):
            continue
        try:
            if file.endswith(".py"):
                Print.print_inf(f"§6载入DotCS插件: {file.strip('.py')}", end="\r")
                with open(os.path.join(PLUGIN_PATH, file), "r", encoding="utf-8") as f:
                    code = f.read()
                plugin, evts, pkfuncs = _import_original_dotcs_plugin(
                    code, dotcs_env, module_env, plugin_grp
                )
                plugin.name = file.strip(".py")
                if (
                    "repeat10s" in evts
                    or "repeat1s" in evts
                    or "repeat30s" in evts
                    or "repeat1m" in evts
                ):
                    evtnew = evts.copy()
                    for i in evtnew:
                        if i.startswith("repeat"):
                            del evts[i]
                            plugin_grp.dotcs_repeat_threadings[
                                i.strip("repeat")
                            ].append(evtnew[i])
                for pkt, func in pkfuncs:
                    plugin_grp.add_listen_packet_id(pkt)
                    plugin_grp.add_listen_packet_func(pkt, func)
                    Print.print_suc(
                        f"[DotCS插件 特殊数据包监听] 添加成功: {plugin.name} <- {func.__name__}"
                    )
                for k, v in evts.items():
                    plugin_grp.plugins_funcs[k].append(v)
                plugin_grp.add_plugin(plugin)
                plugin_grp.dotcs_plugin_loaded_num += 1
                Print.print_suc(f"§a成功载入插件 §2<DotCS> §a{plugin.name}")
        except Exception as err:
            try:
                plugin_name = plugin.name  # type: ignore
            except:
                plugin_name = file
            Print.print_err(f"§c加载插件 {plugin_name} 出现问题: {err}")
            raise
