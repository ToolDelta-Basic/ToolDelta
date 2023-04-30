Plugin: type
add_plugin: type
listen_packet: type
Print: type

import json

@add_plugin
class ConsoleCommands(Plugin):
    name = "控制台执行MC/FB指令"
    author = "SuperScript"
    version = (0, 0, 1)
    def __init__(this, frame):
        this.frame = frame
        this.print = Print
        this.game_ctrl = frame.get_game_control()
        
    def on_inject(this):
        this.frame.add_console_cmd_trigger(["/"], "执行MC指令", this.SendMCCmdOnConsole)
        this.frame.add_console_cmd_trigger(["ws/"], "执行WS指令", this.SendWSCmdOnConsole)
        this.frame.add_console_cmd_trigger(["wo/"], "执行控制台权限指令", this.SendWOCmdOnConsole)
        this.frame.add_console_cmd_trigger(["fb"], "执行FB指令 (fb + <fb指令>)", this.SendFBCmdOnConsole)
        this.frame.add_console_cmd_trigger(["list"], "执行FB指令 (fb + <fb指令>)", lambda _: this.print.print_inf(f"在线玩家: " + ", ".join(this.game_ctrl.allplayers)))
        this.frame.add_console_cmd_trigger(["restplug"], "重载系统插件", this.ReloadPlugins)

    def SendMCCmdOnConsole(this, cmd):
        cmd = " ".join(cmd)
        result = this.game_ctrl.sendcmd(cmd, True, 5)
        try:
            if (result.OutputMessages[0].Message == "commands.generic.syntax") | (result.OutputMessages[0].Message == "commands.generic.unknown"):
                this.print.print_err(f"未知的MC指令， 可能是指令格式有误： \"{cmd}\"")
            else:
                jso = json.dumps(result.as_dict['OutputMessages'], indent=2, ensure_ascii=False)
                if not result.SuccessCount:
                    this.print.print_war(f"指令执行失败：\n{jso}")
                else:
                    this.print.print_suc(f"指令执行成功： \n{jso}")
        except IndexError:
            if result.SuccessCount:
                this.print.print_suc(f"指令执行成功： \n{json.dumps(result.as_dict['OutputMessages'], indent=2, ensure_ascii=False)}")
        except TimeoutError:
            this.print.print_err("[超时] 指令获取结果返回超时")
    
    def SendWSCmdOnConsole(this, cmd):
        try:
            result = this.game_ctrl.sendwscmd(" ".join(cmd), True, 5)
        except IndexError:
            Print.print_err("缺少指令参数")
            return
        try:
            if (result.OutputMessages[0].Message == "commands.generic.syntax") | (result.OutputMessages[0].Message == "commands.generic.unknown"):
                Print.print_err("未知的MC指令， 可能是指令格式有误")
            else:
                jso = json.dumps(result.as_dict['OutputMessages'], indent=2, ensure_ascii=False)
                if not result.SuccessCount:
                    this.print.print_war(f"指令执行失败：\n{jso}")
                else:
                    this.print.print_suc(f"指令执行成功： \n{jso}")
        except IndexError:
            if result.SuccessCount:
                jso = json.dumps(result.as_dict['OutputMessages'], indent=2, ensure_ascii=False)
                this.print.print_suc(f"指令执行成功： \n{jso}")
        except TimeoutError:
            this.print.print_err("[超时] 指令获取结果返回超时")

    def SendFBCmdOnConsole(this, cmd):
        this.game_ctrl.sendfbcmd(" ".join(cmd))

    def SendWOCmdOnConsole(this, cmd):
        this.game_ctrl.sendwocmd(" ".join(cmd), True, 5)

    def ReloadPlugins(this, _):
        this.frame.status = 11
