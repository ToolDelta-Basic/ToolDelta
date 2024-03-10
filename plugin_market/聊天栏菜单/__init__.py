from tooldelta import plugins, Plugin, Frame, Builtins, Config

from dataclasses import dataclass
from typing import Callable

plugins.checkSystemVersion((0, 3, 20))


@dataclass
class ChatbarTriggers:
    triggers: list
    argument_hint: str
    usage: str
    func: Callable
    args_pd: Callable
    op_only: bool


# 使用 api = plugins.get_plugin_api("聊天栏菜单") 来获取到这个api
@plugins.add_plugin_as_api("聊天栏菜单")
class ChatbarMenu(Plugin):
    """
    使用如下方法对接到这个组件:

    >>> menu = plugins.get_plugin_api("聊天栏菜单")

    你可以用它来添加菜单触发词, 像这样:
    menu.add_trigger(["触发词1", "触发词2..."], "功能提示", "<参数提示>", 监听方法[, 参数判定方法(传入参数列表的长度)])

    >>> def MoYu(args):
            print("你摸了: ", " 和 ".join(args))
    >>> menu.add_trigger(["摸鱼", "摸鱼鱼"], "<鱼的名字>", "随便摸一下鱼", MoYu, lambda a: a >= 1)
    """

    name = "聊天栏菜单"
    author = "SuperScript"
    version = (0, 1, 11)
    description = "前置插件, 提供聊天栏菜单功能"
    DEFAULT_CFG = {
        "help菜单样式": {
            "菜单头": "§7>>> §l§bＴｏｏｌＤｅｌｔａ\n§r§l===============================",
            "菜单列表": " - [菜单指令][参数提示] §7§o[菜单功能说明]",
            "菜单尾": "§r§l=============================\n§r>>> §7Producted by §fToolDelta",
        },
        "/help触发词": [".help"],
    }
    STD_CFG_TYPE = {
        "help菜单样式": {"菜单头": str, "菜单列表": str, "菜单尾": str},
        "/help触发词": [r"%list", str],
    }
    chatbar_triggers: list[ChatbarTriggers] = []

    def __init__(self, frame: Frame):
        self.game_ctrl = frame.get_game_control()
        self.cfg, _ = Config.getPluginConfigAndVersion(
            self.name, self.STD_CFG_TYPE, self.DEFAULT_CFG, (0, 0, 1)
        )

    # ----API----
    def add_trigger(
        self,
        triggers: list[str],
        argument_hint: str,
        usage: str,
        func,
        args_pd=lambda _: True,
        op_only=False,
    ):
        # triggers: 所有命令触发词
        # arg_hint: 提示词(命令参数)
        # usage: 显示的命令说明
        # func: 菜单触发回调, 回调参数为(玩家名: str, 命令参数: list[str])
        # args_pd: 判断方法 (参数数量:int) -> 参数数量是否合法: bool
        # op_only: 是否仅op可触发; 目前认为创造模式的都是OP, 你也可以自行更改并进行PR
        if not isinstance(triggers, list):
            raise TypeError
        for tri in triggers:
            if not tri.startswith("."):
                triggers[triggers.index(tri)] = "." + tri
        self.chatbar_triggers.append(
            ChatbarTriggers(triggers, argument_hint, usage, func, args_pd, op_only)
        )

    # ------------
    def on_player_message(self, player: str, msg: str):
        if msg in self.cfg["/help触发词"]:
            is_op_mode = bool(
                self.game_ctrl.sendcmd(
                    "/testfor @a[name=" + player + ",m=1]", True
                ).SuccessCount
            )
            self.game_ctrl.say_to(player, self.cfg["help菜单样式"]["菜单头"])
            for tri in self.chatbar_triggers:
                if not tri.op_only or (is_op_mode and tri.op_only):
                    self.game_ctrl.say_to(
                        player,
                        Builtins.ArgsReplacement(
                            {
                                "[菜单指令]": " / ".join(tri.triggers),
                                "[参数提示]": " " + tri.argument_hint
                                if tri.argument_hint
                                else "",
                                "[菜单功能说明]": ""
                                if tri.usage is None
                                else "以" + tri.usage,
                            }
                        ).replaceTo(self.cfg["help菜单样式"]["菜单列表"]),
                    )
            self.game_ctrl.say_to(player, self.cfg["help菜单样式"]["菜单尾"])
        elif msg.startswith("."):
            for tri in self.chatbar_triggers:
                for trigger in tri.triggers:
                    if msg.startswith(trigger):
                        is_op_mode = bool(
                            self.game_ctrl.sendcmd(
                                "/testfor @a[name=" + player + ",m=1]", True
                            ).SuccessCount
                        )
                        if (not is_op_mode) and tri.op_only:
                            self.game_ctrl.say_to(player, "§c创造模式下才可以使用该菜单项")
                            return
                        args = msg.split()
                        if len(args) == 1:
                            args = []
                        else:
                            args = args[1:]
                        if not tri.args_pd(len(args)):
                            self.game_ctrl.say_to(player, "§c菜单参数数量错误")
                            return
                        tri.func(player, args)
