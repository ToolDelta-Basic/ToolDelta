import json
from tooldelta import Plugin, plugins, Frame, Print

plugins.checkSystemVersion((0, 1, 8))


@plugins.add_plugin
class ConsoleCommands(Plugin):
    name = "控制台执行MC指令"
    author = "SuperScript"
    version = (0, 0, 2)

    def __init__(self, frame: Frame):
        self.frame = frame
        self.print = Print
        self.game_ctrl = frame.get_game_control()

    def on_inject(self):
        self.frame.add_console_cmd_trigger(
            ["/"], "[指令]", "执行MC指令", self.SendMCCmdOnConsoleThread
        )
        self.frame.add_console_cmd_trigger(
            ["ws/"], "[指令]", "执行WS指令", self.SendWSCmdOnConsole
        )
        self.frame.add_console_cmd_trigger(
            ["wo/"], "[指令]", "执行控制台权限指令", self.SendWOCmdOnConsole
        )
        self.frame.add_console_cmd_trigger(
            ["fb", "!"], "[指令]", "执行FB指令 (fb + <fb指令>)", self.SendFBCmdOnConsole
        )
        self.frame.add_console_cmd_trigger(
            ["list"],
            None,
            "查询在线玩家",
            lambda _: self.print.print_inf(
                "在线玩家: " + ", ".join(self.game_ctrl.allplayers)
            ),
        )
        self.frame.add_console_cmd_trigger(
            ["bdump"], "-p <文件路径>", "导入bdx文件", self.SendOriginalFBCommand
        )
        self.frame.add_console_cmd_trigger(
            ["schematic"], "-p <文件路径>", "导入bdx文件", self.SendOriginalFBCommand
        )
        self.frame.add_console_cmd_trigger(
            ["plot"], "-p <文件路径>", "导入PNG文件", self.SendOriginalFBCommand
        )
        self.frame.add_console_cmd_trigger(
            ["mapart"],
            "-p <文件路径>",
            "导入图片文件, 且效果更好",
            self.SendOriginalFBCommand,
        )

    def SendMCCmdOnConsoleThread(self, args):
        self.frame.ClassicThread(self.SendMCCmdOnConsole, (args,))

    def SendMCCmdOnConsole(self, cmd):
        cmd = " ".join(cmd)
        try:
            result = self.game_ctrl.sendcmd(cmd, True, 10)
            if (result.OutputMessages[0].Message == "commands.generic.syntax") | (
                result.OutputMessages[0].Message == "commands.generic.unknown"
            ):
                self.print.print_err(f'未知的MC指令， 可能是指令格式有误： "{cmd}"')
            else:
                jso = json.dumps(
                    result.as_dict["OutputMessages"], indent=2, ensure_ascii=False
                )
                if not result.SuccessCount:
                    self.print.print_war(f"指令执行失败: \n{jso}")
                else:
                    self.print.print_suc(f"指令执行成功: \n{jso}")
        except IndexError:
            if result.SuccessCount:
                self.print.print_suc(
                    f"指令执行成功: \n{json.dumps(result.as_dict['OutputMessages'], indent=2, ensure_ascii=False)}"
                )
        except TimeoutError:
            self.print.print_err("[超时] 指令获取结果返回超时")

    def SendWSCmdOnConsole(self, cmd):
        try:
            result = self.game_ctrl.sendwscmd(" ".join(cmd), True, 5)
        except IndexError:
            Print.print_err("缺少指令参数")
            return
        try:
            if (result.OutputMessages[0].Message == "commands.generic.syntax") | (
                result.OutputMessages[0].Message == "commands.generic.unknown"
            ):
                Print.print_err("未知的MC指令， 可能是指令格式有误")
            else:
                jso = json.dumps(
                    result.as_dict["OutputMessages"], indent=2, ensure_ascii=False
                )
                if not result.SuccessCount:
                    self.print.print_war(f"指令执行失败：\n{jso}")
                else:
                    self.print.print_suc(f"指令执行成功： \n{jso}")
        except IndexError:
            if result.SuccessCount:
                jso = json.dumps(
                    result.as_dict["OutputMessages"], indent=2, ensure_ascii=False
                )
                self.print.print_suc(f"指令执行成功： \n{jso}")
        except TimeoutError:
            self.print.print_err("[超时] 指令获取结果返回超时")

    def SendOriginalFBCommand(self, cmd):
        self.game_ctrl.sendfbcmd(" ".join(cmd))

    def SendFBCmdOnConsole(self, cmd):
        self.game_ctrl.sendfbcmd(" ".join(cmd))

    def SendWOCmdOnConsole(self, cmd):
        self.game_ctrl.sendwocmd(" ".join(cmd))
