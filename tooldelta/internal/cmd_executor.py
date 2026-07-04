import traceback
from dataclasses import dataclass
from typing import Any, TYPE_CHECKING
from collections.abc import Callable
import json
import textwrap
from .. import plugin_market
from ..constants import SysStatus
from ..utils import fmts, mc_translator, thread_func, ToolDeltaThread
from .launch_cli import FrameNeOmegaLauncher, FrameNeOmgAccessPoint


if TYPE_CHECKING:
    from tooldelta import ToolDelta


def get_nearest_command(cmd: str, available_commands: list[str]):
    cmd_weights: dict[str, float] = {}
    for char in cmd:
        for _cmd in available_commands:
            if char in _cmd:
                cmd_weights[_cmd] = cmd_weights.get(_cmd, 0) + 1
                if (fc := _cmd.find(char)) != -1:
                    cmd_weights[_cmd] += max(0, 10 - abs(fc - cmd.find(char)))
    cmd_weights = dict(
        sorted(cmd_weights.items(), key=lambda x: x[1], reverse=True)[:5]
    )
    for _cmd, _weight in cmd_weights.copy().items():
        cmd_weights[_cmd] = _weight + max(0, 10 - abs(len(_cmd) - len(cmd))) / 2
    nearest_cmds = sorted(cmd_weights.items(), key=lambda x: x[1], reverse=True)
    if len(nearest_cmds) < 1:
        return None
    return nearest_cmds[0][0]


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
        """
        注册 ToolDelta 控制台的菜单项

        Args:
            triggers (list[str]): 触发词列表
            arg_hint (str | None): 菜单命令参数提示句
            usage (str): 命令说明
            func (Callable[[list[str]], None]): 菜单回调方法
        """
        triggers_copy = triggers.copy()
        trig = CommandTrigger(triggers_copy, arg_hint, usage, func)
        for i, trigger in enumerate(triggers_copy):
            valid_trigger = self.test_duplicate_trigger(trigger, usage)
            self.commands[valid_trigger] = trig
            if valid_trigger != trigger:
                trig.triggers[i] = valid_trigger

    def get_cmd_triggers(self):
        return list(self.commands.values())

    def execute_cmd(self, cmd: str) -> bool:
        cmd = cmd.strip()
        cmd_finded = False
        sorted_prefixes = sorted(self.commands.keys(), key=len, reverse=True)

        for prefix in sorted_prefixes:
            trig = self.commands[prefix]
            if cmd.startswith(prefix):
                cmds = cmd.removeprefix(prefix).split()
                res = trig.cb(cmds)
                cmd_finded = True
                if res is True:
                    return True
                break

        if not cmd_finded and cmd:
            nearest_cmd = get_nearest_command(cmd, list(self.commands.keys()))
            if nearest_cmd is not None:
                fmts.print_war(
                    f"命令 {cmd.split()[0]} 不存在, 你指的是 {nearest_cmd} 吗？\n输入 ? 查看帮助"
                )
            else:
                fmts.print_war(f"命令 {cmd.split()[0]} 不存在, 输入 ? 查看帮助")
        return False

    def test_duplicate_trigger(self, trigger: str, usage: str):
        if trigger not in self.commands:
            return trigger

        origin_trigger = trigger
        counter = 1
        new_trigger = f"{counter}-{origin_trigger}"

        while new_trigger in self.commands:
            counter += 1
            new_trigger = f"{counter}-{origin_trigger}"

        existing_usage = self.commands[origin_trigger].usage
        fmts.print_war(
            f"功能 {usage} 的命令触发词 {origin_trigger} 与已有功能 {existing_usage} 冲突, 已自动更改为 {new_trigger}"
        )
        return new_trigger

    @thread_func("控制台执行命令", ToolDeltaThread.SYSTEM)
    def command_readline_proc(self):
        fmts.print_suc("ToolHack Terminal 进程已注入, 允许开启标准输入")
        while True:
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
        @thread_func("控制台执行WO命令", ToolDeltaThread.SYSTEM)
        def _execute_wo_command(cmds: list[str]) -> None:
            """以控制台身份发送命令。

            Args:
                cmds (list[str]): Minecraft 命令
            """
            if not cmds:
                fmts.print_err("命令参数为空")
                return
            cmd = " ".join(cmds)
            self.frame.get_game_control().sendwocmd(cmd)

        @thread_func("控制台执行WS命令并获取返回", ToolDeltaThread.SYSTEM)
        def _execute_ws_command_and_get_callback(cmds: list[str]) -> None:
            """以 WebSocket 身份发送命令并获取返回。

            Args:
                cmds (list[str]): Minecraft 命令
            """
            if not cmds:
                fmts.print_err("命令参数为空")
                return
            cmd = " ".join(cmds)
            try:
                result = self.frame.get_game_control().sendwscmd_with_resp(cmd, 5)
                msgs_output = [
                    mc_translator.translate(o.Message, o.Parameters)
                    for o in result.OutputMessages
                ]
                pkt_output = json.dumps(result.as_dict, indent=2, ensure_ascii=False)
                msgs_formatted = textwrap.indent("\n".join(msgs_output), "  ")
                pkt_formatted = textwrap.indent(pkt_output, "  ")
                if result.SuccessCount:
                    fmts.print_suc(
                        f"命令执行成功:\n{msgs_formatted}\n\n命令返回数据包:\n{pkt_formatted}"
                    )
                else:
                    if len(result.OutputMessages) > 0 and (
                        result.OutputMessages[0].Message
                        in ("commands.generic.syntax", "commands.generic.unknown")
                    ):
                        fmts.print_err(
                            f"命令执行错误:\n{msgs_formatted}\n\n命令返回数据包:\n{pkt_formatted}"
                        )
                    else:
                        fmts.print_war(
                            f"命令执行失败:\n{msgs_formatted}\n\n命令返回数据包:\n{pkt_formatted}"
                        )
            except TimeoutError:
                fmts.print_err(f"获取命令 {cmd} 返回超时")
            except Exception as err:
                fmts.print_err(f"解析命令 {cmd} 返回时出现未知的错误: {err}")

        @thread_func("控制台执行玩家命令并获取返回", ToolDeltaThread.SYSTEM)
        def _execute_command_and_get_callback(cmds: list[str]) -> None:
            """以机器人玩家身份发送命令并获取返回。

            Args:
                cmds (list[str]): Minecraft 命令
            """
            if not cmds:
                fmts.print_err("命令参数为空")
                return
            cmd = " ".join(cmds)
            try:
                result = self.frame.get_game_control().sendcmd_with_resp(cmd, 5)
                msgs_output = [
                    mc_translator.translate(o.Message, o.Parameters)
                    for o in result.OutputMessages
                ]
                pkt_output = json.dumps(result.as_dict, indent=2, ensure_ascii=False)
                msgs_formatted = textwrap.indent("\n".join(msgs_output), "  ")
                pkt_formatted = textwrap.indent(pkt_output, "  ")
                if result.SuccessCount:
                    fmts.print_suc(
                        f"命令执行成功:\n{msgs_formatted}\n\n命令返回数据包:\n{pkt_formatted}"
                    )
                else:
                    if len(result.OutputMessages) > 0 and (
                        result.OutputMessages[0].Message
                        in ("commands.generic.syntax", "commands.generic.unknown")
                    ):
                        fmts.print_err(
                            f"命令执行错误:\n{msgs_formatted}\n\n命令返回数据包:\n{pkt_formatted}"
                        )
                    else:
                        fmts.print_war(
                            f"命令执行失败:\n{msgs_formatted}\n\n命令返回数据包:\n{pkt_formatted}"
                        )
            except TimeoutError:
                fmts.print_err(f"获取命令 {cmd} 返回超时")
            except Exception as err:
                fmts.print_err(f"解析命令 {cmd} 返回时出现未知的错误: {err}")

        @thread_func("控制台执行魔法命令并获取返回", ToolDeltaThread.SYSTEM)
        def _execute_ai_command_and_get_callback(cmds: list[str]) -> None:
            """发送魔法命令并获取返回。

            Args:
                cmds (list[str]): Minecraft 命令
            """
            if not cmds:
                fmts.print_err("命令参数为空")
                return
            cmd = " ".join(cmds)
            try:
                gc = self.frame.get_game_control()
                if hasattr(gc.launcher, "sendaicmd"):
                    result = gc.sendaicmd_with_resp(cmd, 5)
                else:
                    fmts.print_war(
                        "此接入点尚未实现 sendaicmd_with_resp 方法, 无法获取返回结果"
                    )
                    gc.sendaicmd(cmd)
                    return
                msgs_output = [
                    mc_translator.translate(o.Message, o.Parameters)
                    for o in result.OutputMessages
                ]
                pkt_output = json.dumps(result.as_dict, indent=2, ensure_ascii=False)
                msgs_formatted = textwrap.indent("\n".join(msgs_output), "  ")
                pkt_formatted = textwrap.indent(pkt_output, "  ")
                if result.SuccessCount:
                    fmts.print_suc(
                        f"命令执行成功:\n{msgs_formatted}\n\n命令返回数据包:\n{pkt_formatted}"
                    )
                else:
                    if len(result.OutputMessages) > 0 and (
                        result.OutputMessages[0].Message
                        in ("commands.generic.syntax", "commands.generic.unknown")
                    ):
                        fmts.print_err(
                            f"命令执行错误:\n{msgs_formatted}\n\n命令返回数据包:\n{pkt_formatted}"
                        )
                    else:
                        fmts.print_war(
                            f"命令执行失败:\n{msgs_formatted}\n\n命令返回数据包:\n{pkt_formatted}"
                        )
            except TimeoutError:
                fmts.print_err(f"获取命令 {cmd} 返回超时")
            except Exception as err:
                fmts.print_err(f"解析命令 {cmd} 返回时出现未知的错误: {err}")

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
            ["wo/"],
            "[命令]",
            "以控制台身份发送命令",
            lambda args: _execute_wo_command(args) and None,
        )
        self.add_console_cmd_trigger(
            ["ws/"],
            "[命令]",
            "以 WebSocket 身份发送命令并获取返回",
            lambda args: _execute_ws_command_and_get_callback(args) and None,
        )
        self.add_console_cmd_trigger(
            ["/"],
            "[命令]",
            "以机器人玩家身份发送命令并获取返回",
            lambda args: _execute_command_and_get_callback(args) and None,
        )
        self.add_console_cmd_trigger(
            ["ai/"],
            "[命令]",
            "发送魔法命令并获取返回",
            lambda args: _execute_ai_command_and_get_callback(args) and None,
        )
        self.add_console_cmd_trigger(["list"], None, "查询在线玩家", _list)
        self.add_console_cmd_trigger(
            ["reload"],
            None,
            "浅重载插件 (重载插件的__init__.py, 可能有部分特殊插件无法重载, 建议一般情况时使用)",
            lambda _: self.frame.reload(deep_reload=False),
        )
        self.add_console_cmd_trigger(
            ["deepreload"],
            None,
            "深重载插件 (重载整个插件模块, 可能导致某些进程被强制清除, 建议插件开发时使用)",
            lambda _: self.frame.reload(deep_reload=True),
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
