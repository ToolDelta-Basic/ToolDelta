import json
import traceback
from dataclasses import dataclass
from typing import Any, TYPE_CHECKING
from collections.abc import Callable
from .. import plugin_market
from ..constants import SysStatus
from ..utils import fmts, thread_func, ToolDeltaThread
from .launch_cli import FrameNeOmegaLauncher, FrameNeOmgAccessPoint


if TYPE_CHECKING:
    from tooldelta import ToolDelta


@dataclass
class CommandTrigger:
    triggers: list[str]
    argument_hint: str | None
    usage: str
    cb: Callable[[list[str]], Any]

    def __hash__(self):
        return id(self)


class ConsoleCmdManager:
    def __init__(self, frame: "ToolDelta") -> None:
        self.frame = frame
        self.commands: dict[str, CommandTrigger] = {}

    def add_console_cmd_trigger(
        self,
        triggers: list[str],
        arg_hint: str | None,
        usage: str,
        func: Callable[[list[str]], Any],
    ):
        """注册 ToolDelta 控制台的菜单项

        Args:
            triggers (list[str]): 触发词列表
            arg_hint (str | None): 菜单命令参数提示句
            usage (str): 命令说明
            func (Callable[[list[str]], None]): 菜单回调方法
        """
        trig = CommandTrigger(triggers, arg_hint, usage, func)
        for trigger in triggers:
            self.commands[self.test_duplicate_trigger(trigger)] = trig

    def get_cmd_triggers(self):
        return list(self.commands.values())

    def execute_cmd(self, cmd: str) -> bool:
        cmd = cmd.strip()
        cmd_finded = False
        for prefix, trig in self.commands.copy().items():
            if cmd.startswith(prefix):
                cmds = cmd.removeprefix(prefix).split()
                res = trig.cb(cmds)
                cmd_finded = True
                if res is True:
                    return True
        if not cmd_finded and cmd:
            fmts.print_war(f"命令 {cmd.split()[0]} 不存在, 输入 ? 查看帮助")
        return False

    def test_duplicate_trigger(self, trigger: str):
        for exists_trigger in self.commands.keys():
            counter = 0
            invalid = False
            origin_trigger = trigger
            while 1:
                if not (trigger.startswith(exists_trigger) or exists_trigger.startswith(trigger)):
                    if invalid:
                        fmts.print_war(
                            f"命令 {origin_trigger} 与 {exists_trigger} 冲突, 已更改为 {trigger}"
                        )
                        return trigger
                    break
                invalid = True
                counter += 1
                trigger = f"{counter}-{trigger}"
        return trigger

    @thread_func("控制台执行命令", ToolDeltaThread.SYSTEM)
    def command_readline_proc(self):
        fmts.print_suc("ToolHack Terminal 进程已注入, 允许开启标准输入")
        while 1:
            try:
                try:
                    rsp = input().encode(errors="ignore").decode("utf-8")
                    if rsp in ("^C", "^D"):
                        raise KeyboardInterrupt
                except (KeyboardInterrupt, EOFError):
                    fmts.print_inf("按退出键退出中...")
                    self.frame.launcher.update_status(SysStatus.NORMAL_EXIT)
                    return
                self.execute_cmd(rsp)
            except (EOFError, KeyboardInterrupt):
                fmts.print_war("命令执行被中止")
            except Exception:
                fmts.print_err(f"控制台指令执行出现问题: {traceback.format_exc()}")
                fmts.print_err("§6虽然出现了问题, 但是您仍然可以继续使用控制台菜单")

    def prepare_internal_cmds(self):
        @thread_func("控制台执行指令并获取回调", ToolDeltaThread.SYSTEM)
        def _execute_mc_command_and_get_callback(cmds: list[str]) -> None:
            """执行 Minecraft 指令并获取回调结果。

            Args:
                cmd (str): 要执行的 Minecraft 指令。

            Raises:
                ValueError: 当指令执行失败时抛出。
            """
            cmd = " ".join(cmds)
            try:
                result = self.frame.get_game_control().sendcmd_with_resp(cmd, 10)
                if (result.OutputMessages[0].Message == "commands.generic.syntax") | (
                    result.OutputMessages[0].Message == "commands.generic.unknown"
                ):
                    fmts.print_err(f'未知的 MC 指令, 可能是指令格式有误: "{cmd}"')
                else:
                    if (
                        game_text_handler
                        := self.frame.get_game_control().game_data_handler
                    ):
                        msgs_output = " ".join(
                            json.loads(i)
                            for i in game_text_handler.Handle_Text_Class1(
                                result.as_dict["OutputMessages"]
                            )
                        )
                    else:
                        msgs_output = json.dumps(
                            result.as_dict["OutputMessages"],
                            indent=2,
                            ensure_ascii=False,
                        )
                    desc = json.dumps(
                        result.OutputMessages[0].Parameters,
                        indent=2,
                        ensure_ascii=False,
                    )
                    if result.SuccessCount:
                        fmts.print_suc("指令执行成功: " + msgs_output)
                        fmts.print_suc(desc)
                    else:
                        fmts.print_war("指令执行失败: " + msgs_output)
                        fmts.print_war(desc)
            except IndexError as exec_err:
                if isinstance(result, type(None)):
                    raise ValueError("指令执行失败") from exec_err
                if result.SuccessCount:
                    fmts.print_suc(
                        f"指令执行成功, 详细返回结果:\n{json.dumps(result.as_dict['OutputMessages'], indent=2, ensure_ascii=False)}"
                    )
            except TimeoutError:
                fmts.print_err(f"[超时] 指令获取结果返回超时: {cmd}")

        def _send_to_neomega(cmds: list[str]):
            # 仅当启动模式为 neomega 并行模式才生效
            assert isinstance(self.frame.launcher, FrameNeOmgAccessPoint)
            assert self.frame.launcher.neomg_proc
            assert self.frame.launcher.neomg_proc.stdin
            self.frame.launcher.neomg_proc.stdin.write(" ".join(cmds) + "\n")
            self.frame.launcher.neomg_proc.stdin.flush()

        def say(msgs: list[str]):
            self.frame.get_game_control().say_to(
                "@a", f"[§b控制台§r] §3{' '.join(msgs)}"
            )

        def _basic_help(_):
            menu = self.get_cmd_triggers()
            fmts.print_inf("§a以下是可选的菜单指令项: ")
            for cmd_trigger in set(menu):
                if cmd_trigger.argument_hint:
                    fmts.print_inf(
                        f" §e{' 或 '.join(cmd_trigger.triggers)} §b{cmd_trigger.argument_hint} §f->  {cmd_trigger.usage}"
                    )
                else:
                    fmts.print_inf(
                        f" §e{' 或 '.join(cmd_trigger.triggers)}  §f->  {cmd_trigger.usage}"
                    )

        def _list(_):
            players = self.frame.game_ctrl.players
            players_format = ", ".join(p.name for p in players)
            fmts.print_inf(f"在线玩家 {len(list(players))} 人: {players_format}")

        def _exit(_):
            fmts.print_inf("准备退出..")
            self.frame.launcher.update_status(SysStatus.NORMAL_EXIT)

        self.add_console_cmd_trigger(
            ["?", "help", "帮助", "？"],
            None,
            "查询可用菜单指令",
            _basic_help,
        )
        self.add_console_cmd_trigger(
            ["exit"],
            None,
            "退出并关闭ToolDelta",
            _exit,
        )
        self.add_console_cmd_trigger(
            ["插件市场"],
            None,
            "进入插件市场",
            lambda _: plugin_market.market.enter_plugin_market(in_game=True),
        )
        self.add_console_cmd_trigger(
            ["/"], "[指令]", "执行 MC 指令", lambda args: _execute_mc_command_and_get_callback(args) and None
        )
        self.add_console_cmd_trigger(
            ["list"],
            None,
            "查询在线玩家",
            _list
        )
        self.add_console_cmd_trigger(
            ["reload"],
            None,
            "重载插件 (可能有部分特殊插件无法重载)",
            lambda _: self.frame.reload(),
        )
        if isinstance(self.frame.launcher, FrameNeOmegaLauncher):
            self.add_console_cmd_trigger(
                ["o"], "neomega命令", "执行neomega控制台命令", _send_to_neomega
            )
        self.add_console_cmd_trigger(["!"], "[消息]", "在游戏内广播消息", say)

    def reset_cmds(self):
        self.commands.clear()
        self.prepare_internal_cmds()

    def start_proc_thread(self):
        self.prepare_internal_cmds()
        self.command_readline_proc()
