import re
from tooldelta import Frame, Plugin, plugins, Config, Builtins, Print


@plugins.add_plugin
class CustomChatbarMenu(Plugin):
    name = "自定义聊天栏菜单"
    author = "SuperScript"
    version = (0, 0, 1)
    description = "自定义ToolDelta的聊天栏菜单触发词等"

    match_rule = re.compile(r"(\[参数:([0-9]+)\])")
    _counter = 0

    def __init__(self, frame: Frame):
        self.game_ctrl = frame.get_game_control()
        STD_CFG = {
            "菜单项": [
                r"%list",
                {
                    "触发词": [r"%list", str],
                    "参数提示": str,
                    "功能简介": str,
                    "需要的参数数量": Config.NNInt,
                    "触发后执行的指令": [r"%list", str],
                },
            ]
        }
        DEFAULT_CFG = {
            "菜单项": [
                {
                    "说明": "返回重生点",
                    "触发词": ["kill", "自尽"],
                    "需要的参数数量": 0,
                    "参数提示": "",
                    "功能简介": "返回重生点",
                    "触发后执行的指令": ["/kill [玩家名]", "/title [玩家名] actionbar 自尽成功"],
                },
                {
                    "说明": "一个测试菜单参数项的触发词菜单项",
                    "触发词": ["测试参数"],
                    "需要的参数数量": 2,
                    "参数提示": "[参数1] [参数2]",
                    "功能简介": "测试触发词参数",
                    "触发后执行的指令": ["/w [玩家名] 触发词测试成功: 参数1=[参数:1], 参数2=[参数:2]"],
                },
            ]
        }
        self.cfg, _ = Config.getPluginConfigAndVersion(
            self.name, STD_CFG, DEFAULT_CFG, self.version
        )

    def on_def(self):
        self.chatbar = plugins.get_plugin_api("聊天栏菜单")

    @Builtins.run_as_new_thread
    def on_inject(self):
        for menu in self.cfg["菜单项"]:
            cb = self.make_cb_func(menu)
            self.chatbar.add_trigger(menu["触发词"], menu["参数提示"], menu["功能简介"], cb)

    def make_cb_func(self, menu):
        cmds = menu["触发后执行的指令"]

        @Builtins.run_as_new_thread
        def _menu_cb_func(player, args: list):
            if not self.check_args_len(player, args, menu["需要的参数数量"]):
                return
            for cmd in cmds:
                f_cmd = Builtins.SimpleFmt(
                    {"[玩家名]": player}, self.args_replace(args, cmd)
                )
                self.game_ctrl.sendwscmd(f_cmd)

        return _menu_cb_func

    def args_replace(self, args: list, sub: str):
        res = self.match_rule.findall(sub)
        for varsub, var_arg in res:
            try:
                var_value = args[int(var_arg) - 1]
                sub = sub.replace(varsub, var_value)
            except IndexError:
                Print.print_err("聊天栏菜单: 菜单的参数项提供异常!")
                self.game_ctrl.say_to("@a", "聊天栏菜单: 菜单的参数项提供异常， 请联系管理员以修复")
                raise SystemExit
        return sub

    def check_args_len(self, player, args, need_len):
        if len(args) < need_len:
            self.game_ctrl.say_to(player, f"§c菜单参数太少， 需要 {need_len} 个")
            return False
        return True
