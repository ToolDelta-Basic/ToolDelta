import os
import re
from pathlib import Path

FROM_TOOLDELTA_IMPORT_SINGLE_LINE_FINDER = re.compile(
    r"(?P<body>from tooldelta import (?P<module_names>[A-Za-z0-9_, ]+))"
)
FROM_TOOLDELTA_IMPORT_MULTI_LINE_FINDER = re.compile(
    r"(?P<body>from tooldelta import |\((?P<module_names>[A-Za-z0-9_, \n]+)\))"
)
PLUGIN_CLASS_DEF_FINDER = re.compile(
    r"(?P<body>@(|[A-Za-z0-9_一-龥]+\.)plugins\.add_plugin\n)class (?P<class_name>[A-Za-z0-9_一-龥]+)"
)
API_PLUGIN_CLASS_DEF_FINDER = re.compile(
    r"(?P<body>@(|[A-Za-z0-9_一-龥]+\.)plugins\.add_plugin_as_api\((?P<api_name>[^\)]+)\)\n)class (?P<class_name>[A-Za-z0-9_一-龥]+)"
)
PURE_PLUGIN_CLASS_DEF_FINDER = re.compile(
    r"(?P<body>class (?P<class_name>[A-Za-z0-9_一-龥]+)\((|tooldelta\.)Plugin\):\n)"
)
PKT_LISTENER_FUNCTIONS_DEF_FINDER = re.compile(
    r"(?P<body>@(|[A-Za-z0-9_一-龥]+\.)plugins\.add_packet_listener\((?P<listen_packets>[^\)]+)\)\n)"
    r" *"
    r"def (?P<func_name>[A-Za-z0-9_一-龥]+)"
)
GET_PLUGIN_API_FINDER = re.compile(
    r"""(?P<body>(|[A-Za-z0-9_一-龥]+\.)plugins\.get_plugin_api(?P<api_args>[^\n]+)\n)"""
)
INSTANT_PLUGIN_API_FINDER = re.compile(
    r"""(?P<body>(|[A-Za-z0-9_一-龥]+\.)plugins\.instant_plugin_api(?P<api_args>[^\n]+)\n)"""
)
CLASS_INIT_FINDER = re.compile(
    r"""(?P<body>    def __init__\(self, frame(|: ToolDelta|: Frame|: "ToolDelta"|: "Frame")\):\n"""
    r"""((        [^\n]*\n)*)(?=\s{0,7}\S|\Z)"""
    r")"
)
ON_PLAYER_JOIN_FUNC_FINDER = re.compile(
    r"""(?P<body>    def on_player_join"""
    r"""\(self, (?P<player_varname>[A-Za-z0-9_一-龥]+)(|: *["A-Za-z0-9_一-龥]+)\):\n"""
    r"""(?P<code_body>(\n        [^\n]+)*)"""
    r")"
)
ON_PLAYER_LEAVE_FUNC_FINDER = re.compile(
    r"""(?P<body>    def on_player_leave"""
    r"""\(self, (?P<player_varname>[A-Za-z0-9_一-龥]+)(|: *["A-Za-z0-9_一-龥]+)\):\n"""
    r"""(?P<code_body>(\n        [^\n]+)*)"""
    r")"
)
ON_PLAYER_MESSAGE_FUNC_FINDER = re.compile(
    r"""(?P<body>    def on_player_message"""
    r"""\(self, (?P<player_varname>[A-Za-z0-9_一-龥]+)(|: *["'A-Za-z0-9_一-龥]+), *(?P<msg_varname>[A-Za-z0-9_一-龥]+)(|: *["'A-Za-z0-9_一-龥]+)\):"""
    r"""(?P<code_body>(\n        [^\n]+)*)"""
    r")"
)
ON_FRAME_EXIT_FUNC_FINDER = re.compile(
    r"""(?P<body>    def on_frame_exit"""
    r"""\(self, (?P<signal_varname>[A-Za-z0-9_一-龥]+)(|: *["'A-Za-z0-9_一-龥]+), *(?P<reason_varname>[A-Za-z0-9_一-龥]+)(|: *["'A-Za-z0-9_一-龥]+)\):"""
    r"""(?P<code_body>(\n        [^\n]+)*)"""
    r")"
)
VERSION_CHECKER = re.compile(r"plugins.checkSystemVersion\(\([0-9, ]+\)\)")


def remove_version_check(content: str):
    if VERSION_CHECKER.search(content):
        content = VERSION_CHECKER.sub("", content)
    return content

def fix_event_funcs_args(content: str):
    for regex, args, fixer_headargs, fixer_bodyargs in (
        (
            ON_PLAYER_JOIN_FUNC_FINDER,
            ("player",),
            "on_player_join(self, player: Player)",
            ("{player_varname} = player.name",),
        ),
        (
            ON_PLAYER_LEAVE_FUNC_FINDER,
            ("player",),
            "on_player_leave(self, player: Player)",
            ("{player_varname} = player.name",),
        ),
        (
            ON_PLAYER_MESSAGE_FUNC_FINDER,
            ("player", "msg"),
            "on_player_message(self, chat: Chat)",
            ("{player_varname} = chat.player.name", "{msg_varname} = chat.msg"),
        ),
        (
            ON_FRAME_EXIT_FUNC_FINDER,
            ("signal", "reason"),
            "on_frame_exit(self, evt: FrameExit)",
            ("{signal_varname} = evt.signal", "{reason_varname}s = evt.reason"),
        ),
    ):
        if res := regex.search(content):
            kwargs = {(argname := f"{arg}_varname"): res.group(argname) for arg in args}
            new_func_body = (
                "    def "
                + fixer_headargs
                + ":\n        "
                + "\n        ".join(i.format(**kwargs) for i in fixer_bodyargs)
                + "\n"
                + res.group("code_body")
                if fixer_bodyargs
                else "" + res.group("code_body")
            )
            content = content.replace(res.group("body"), new_func_body)
    return content


def replace_plugins_import(content: str, extras: list[str]) -> str:
    plugins_import_find = False
    for multi_modules in [
        *FROM_TOOLDELTA_IMPORT_SINGLE_LINE_FINDER.finditer(content),
        *FROM_TOOLDELTA_IMPORT_SINGLE_LINE_FINDER.finditer(content),
    ]:
        body = multi_modules.group("body")
        modules_raw = multi_modules.group("module_names")
        modules = modules_raw.replace("\n", "").replace(" ", "").split(",")
        if "plugins" in modules:
            modules.remove("plugins")
            plugins_import_find = True
        for attr in [*extras, "plugin_entry"]:
            if attr not in modules:
                modules.append(attr)
        content = content.replace(
            body, "from tooldelta import " + ", ".join(modules) + "\n"
        )
    if not plugins_import_find:
        raise ValueError("此插件文件没有导入 plugins")
    return content


def replace_add_plugin_decorator(content: str):
    if grp := API_PLUGIN_CLASS_DEF_FINDER.search(content):
        body = grp.group("body")
        plugin_cls_name = grp.group("class_name")
        api_name = grp.group("api_name")
    elif grp := PLUGIN_CLASS_DEF_FINDER.search(content):
        body = grp.group("body")
        plugin_cls_name = grp.group("class_name")
        api_name = ""
    else:
        raise ValueError("此插件文件没有注册插件主类")
    content = content.replace(body, "")
    if api_name:
        content += f"\nentry = plugin_entry({plugin_cls_name}, {api_name})"
    else:
        content += f"\nentry = plugin_entry({plugin_cls_name})"
    return content


def replace_get_plugin_api(content: str) -> str:
    for grp in GET_PLUGIN_API_FINDER.finditer(content):
        content = content.replace(
            grp.group("body"),
            f"self.GetPluginAPI{grp.group('api_args')}\n",
        )
    return content


def replace_instant_plugin_api(content: str):
    for grp in INSTANT_PLUGIN_API_FINDER.finditer(content):
        content = content.replace(
            grp.group("body"),
            f"self.get_typecheck_plugin_api{grp.group('api_args')}\n",
        )
    return content


def find_and_replace_packet_listener(content: str):
    func_names_and_listen_packet_args: list[tuple[str, str]] = []
    for grp in PKT_LISTENER_FUNCTIONS_DEF_FINDER.finditer(content):
        func_names_and_listen_packet_args.append(
            (grp.group("func_name"), grp.group("listen_packets"))
        )
        content = content.replace(
            grp.group("body"),
            "\n",
        )
    return content, func_names_and_listen_packet_args


def get_avali_event_funcs(content: str):
    contents = content.split("\n")
    evts = {
        "on_def": False,
        "on_inject": False,
        "on_player_join": False,
        "on_player_leave": False,
        "on_player_message": False,
        "on_frame_exit": False,
    }
    for content in contents:
        content = content.strip()
        if content.startswith("def on_"):
            for evt in evts.copy():
                if content.strip().startswith(f"def {evt}"):
                    evts[evt] = True
    for content in contents:
        content = content.strip().removeprefix("self.")
        if content.startswith("ListenPreload"):
            evts["on_def"] = False
        elif content.startswith("ListenActive"):
            evts["on_inject"] = False
        elif content.startswith("ListenPlayerJoin"):
            evts["on_player_join"] = False
        elif content.startswith("ListenPlayerLeave"):
            evts["on_player_leave"] = False
        elif content.startswith("ListenChat"):
            evts["on_player_message"] = False
        elif content.startswith("ListenFrameExit"):
            evts["on_frame_exit"] = False
    return evts


def make_evts_to_listener_code(evts: dict[str, bool]):
    codes: list[str] = []
    vals = {
        "on_def": "Preload",
        "on_inject": "Active",
        "on_player_join": "PlayerJoin",
        "on_player_leave": "PlayerLeave",
        "on_player_message": "Chat",
        "on_frame_exit": "FrameExit",
    }
    for evt, val in evts.items():
        if val:
            codes.append(f"self.Listen{vals[evt]}(self.{evt})")
    return codes


def evts_to_import_args(evts: dict[str, bool]):
    args: set[str] = set()
    for k, v in {
        "on_def": (),
        "on_inject": (),
        "on_player_join": ("Player",),
        "on_player_leave": ("Player",),
        "on_player_message": ("Chat",),
        "on_frame_exit": ("FrameExit",),
    }.items():
        if evts[k]:
            args = args.union(set(v))
    return list(args)


def make_listen_packet_to_listener_code(
    func_names_and_listen_packet_args: list[tuple[str, str]],
):
    codes: list[str] = []
    for name, args in func_names_and_listen_packet_args:
        codes.append(f"self.ListenPacket({args}, self.{name})")
    return codes


def add_code_to_init(content: str, codes: list[str]):
    if codes:
        init_blk = CLASS_INIT_FINDER.search(content)
        if init_blk is None:
            print("<adding __init__> ", end="")
            content = force_add_init(content)
            init_blk = CLASS_INIT_FINDER.search(content)
            if init_blk is None:
                raise ValueError("???")
        body = init_blk.group("body")
        new_body = body + "        " + "\n        ".join(codes)
        return content.replace(body, new_body + "\n")
    else:
        return content


def force_add_init(content: str):
    class_block = PURE_PLUGIN_CLASS_DEF_FINDER.search(content)
    if class_block is None:
        raise ValueError("此插件没有主类")
    return content.replace(
        body := class_block.group("body"),
        body + "    def __init__(self, frame):\n        super().__init__(frame)\n",
    )


def clean_file(content: str):
    content = content.strip()
    while "\n\n" in content:
        content = content.replace("\n\n", "\n")
    return content


def process_file(content: str):
    content = remove_version_check(content)
    content = clean_file(content)
    content = replace_add_plugin_decorator(content)
    content = replace_get_plugin_api(content)
    content = replace_instant_plugin_api(content)
    content = fix_event_funcs_args(content)
    content, pkt_funcs_and_args = find_and_replace_packet_listener(content)
    evts = get_avali_event_funcs(content)
    evts_codes = make_evts_to_listener_code(evts)
    content = replace_plugins_import(content, evts_to_import_args(evts))
    pkt_codes = make_listen_packet_to_listener_code(pkt_funcs_and_args)
    content = content.replace("    \n", "\n")
    # print(content, CLASS_INIT_FINDER.search(content))
    content = add_code_to_init(content, evts_codes + pkt_codes)
    return content


def process_files():
    basic_path = Path("插件文件/ToolDelta类式插件")
    for plugin_dir in os.listdir(basic_path):
        plugin_file = basic_path / plugin_dir / "__init__.py"
        with open(plugin_file, encoding="utf-8") as f:
            print(plugin_file, end="")
            content = f.read()

        if "plugin_entry" in content:
            print(" -- Its a newest format file, skip.")
            continue

        print(" -- Processing..", end="")
        content = process_file(content)
        print("OK")

        with open(plugin_file, "w", encoding="utf-8") as f:
            f.write(content)


def demo():
    print(
        process_file(
            # ON_PLAYER_MESSAGE_FUNC_FINDER.findall(
            r'''

from tooldelta import plugins, Plugin, Config, Utils

from dataclasses import dataclass
from collections.abc import Callable

from tooldelta.internal import launch_cli


plugins.checkSystemVersion((0, 7, 5))

@dataclass
class ChatbarTriggersSimple:
    triggers: list[str]
    usage: str
    func: Callable
    op_only: bool
    argument_hint = ""
    args_pd = staticmethod(lambda _,: True)

@dataclass
class ChatbarTriggers:
    triggers: list[str]
    argument_hint: str | None
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
    version = (0, 3, 0)
    description = "前置插件, 提供聊天栏菜单功能"

    def __init__(self, frame):
        super().__init__(frame)
        self.chatbar_triggers: list[ChatbarTriggers | ChatbarTriggersSimple] = []
        DEFAULT_CFG = {
            "help菜单样式": {
                "菜单头": "§7>>> §l§bＴｏｏｌＤｅｌｔａ\n§r§l===============================",
                "菜单列表": " - [菜单指令][参数提示] §7§o[菜单功能说明]",
                "菜单尾": "§r§l==========[[当前页数] §7/ [总页数]§f]===========\n§r>>> §7输入 .help <页数> 可以跳转到该页",
            },
            "/help触发词": [".help"],
            "被识别为触发词的前缀(不填则为无命令前缀)": [".", "。", "·"],
            "单页内最多显示数": 6,
        }
        STD_CFG_TYPE = {
            "help菜单样式": {"菜单头": str, "菜单列表": str, "菜单尾": str},
            "/help触发词": Config.JsonList(str),
            "单页内最多显示数": Config.PInt,
            "被识别为触发词的前缀(不填则为无命令前缀)": Config.JsonList(str)
        }
        self.cfg, _ = Config.get_plugin_config_and_version(
            self.name, STD_CFG_TYPE, DEFAULT_CFG, (0, 0, 1)
        )
        self.prefixs = self.cfg["被识别为触发词的前缀(不填则为无命令前缀)"]

    # ----API----
    def add_trigger(
        self,
        triggers: list[str],
        argument_hint: str | None,
        usage: str,
        func: Callable | None,
        args_pd: Callable[[int], bool] = lambda _: True,
        op_only=False,
    ):
        """
        添加菜单触发词项.
        Args:
            triggers (list[str]): 所有命令触发词
            argument_hint (str | None): 提示词(命令参数)
            usage (str): 显示的命令说明
            func (Callable | None): 菜单触发回调, 回调参数为(玩家名: str, 命令参数: list[str])
            args_pd ((int) -> bool): 判断方法 (参数数量:int) -> 参数数量是否合法: bool
            op_only (bool): 是否仅op可触发; 目前认为创造模式的都是OP, 你也可以自行更改并进行PR
        """
        for tri in triggers:
            if tri.startswith("."):
                triggers[triggers.index(tri)] = tri[1:]

        if func is None:

            def call_none(*args):
                return None

            self.chatbar_triggers.append(
                ChatbarTriggers(
                    triggers, argument_hint, usage, call_none, args_pd, op_only
                )
            )
            return
        self.chatbar_triggers.append(
            ChatbarTriggers(triggers, argument_hint, usage, func, args_pd, op_only)
        )

    def add_simple_trigger(
        self,
        triggers: list[str],
        usage: str,
        func: Callable | None,
        op_only=False,
    ):
        """
        添加简单的不需要带参的菜单触发词项.
        Args:
            triggers (list[str]): 所有命令触发词
            usage (str): 显示的命令说明
            func (Callable | None): 菜单触发回调, 回调参数为(玩家名: str, 命令参数: list[str])
            op_only (bool): 是否仅op可触发; 目前认为创造模式的都是OP, 你也可以自行更改并进行PR
        """
        for tri in triggers:
            if tri.startswith("."):
                triggers[triggers.index(tri)] = tri[1:]
        if func is None:

            def call_none(*args):
                return None

            self.chatbar_triggers.append(
                ChatbarTriggersSimple(
                    triggers, usage, call_none, op_only
                )
            )
            return
        self.chatbar_triggers.append(
            ChatbarTriggersSimple(triggers, usage, func, op_only)
        )

    # ------------

    def on_def(self):
        if isinstance(self.frame.launcher, launch_cli.FrameNeOmgAccessPoint):
            self.is_op = lambda player: self.frame.launcher.is_op(player)
        else:

            def get_success_count(player: str) -> bool:
                result = self.game_ctrl.sendcmd(f"/testfor @a[name={player},m=1]", True)
                if result is not None and result.SuccessCount is not None:
                    return bool(result.SuccessCount)
                return False  # 或者任何你认为合适的默认值

            self.is_op = get_success_count

    def show_menu(self, player: str, page: int):
        # page min = 1
        player_is_op = self.is_op(player)
        all_menu_args = self.chatbar_triggers
        if not player_is_op:
            # 仅 OP 可见的部分 过滤掉
            all_menu_args = list(filter(lambda x: not x.op_only, all_menu_args))
        lmt = self.cfg["单页内最多显示数"]
        total = len(all_menu_args)
        max_page = (total + lmt - 1) // lmt
        if page < 1:
            page_split_index = 0
        elif page > max_page:
            page_split_index = max_page - 1
        else:
            page_split_index = page - 1
        diplay_menu_args = all_menu_args[
            page_split_index * lmt : (page_split_index + 1) * lmt
        ]
        self.game_ctrl.say_to(player, self.cfg["help菜单样式"]["菜单头"])
        for tri in diplay_menu_args:
            self.game_ctrl.say_to(
                player,
                Utils.simple_fmt(
                    {
                        "[菜单指令]": ("§e" if tri.op_only else "")
                        + " / ".join(tri.triggers)
                        + "§r",
                        "[参数提示]": (
                            " " + tri.argument_hint if (isinstance(tri, ChatbarTriggers) and tri.argument_hint) else ""
                        ),
                        "[菜单功能说明]": (
                            "" if tri.usage is None else "以" + tri.usage
                        ),
                    },
                    self.cfg["help菜单样式"]["菜单列表"],
                ),
            )
        self.game_ctrl.say_to(
            player,
            Utils.simple_fmt(
                {"[当前页数]": page_split_index + 1, "[总页数]": max_page},
                self.cfg["help菜单样式"]["菜单尾"],
            ),
        )

    @Utils.thread_func("聊天栏菜单执行")
    def on_player_message(self, player: str, msg: str):
        if self.prefixs:
            for prefix in self.prefixs:
                if msg.startswith(prefix):
                    msg = msg[len(prefix):]
                    break
            else:
                return
        player_is_op = self.is_op(player)
        # 这是查看指令帮助的触发词
        for tri in self.cfg["/help触发词"]:
            if msg.startswith(tri):
                with Utils.ChatbarLock(player, self.on_menu_warn):
                    # 这是 help 帮助的触发词
                    m = msg.split()
                    if len(m) == 1:
                        self.show_menu(player, 1)
                    else:
                        if (page_num := Utils.try_int(m[1])) is None:
                            self.game_ctrl.say_to(
                                player, "§chelp 命令应为1个参数: <页数: 正整数>"
                            )
                        else:
                            self.show_menu(player, page_num)
                return
        # 这是一般菜单触发词
        for tri in self.chatbar_triggers:
            for trigger in tri.triggers:
                if msg.startswith(trigger):
                    if (not player_is_op) and tri.op_only:
                        self.game_ctrl.say_to(
                            player, "§c创造模式或者OP才可以使用该菜单项"
                        )
                        return
                    args = msg.removeprefix(trigger).split()
                    if " " in trigger:
                        with Utils.ChatbarLock(player, self.on_menu_warn):
                            tri_split_num = len(trigger.split()) - 1
                            args = args[tri_split_num:]
                            if not tri.args_pd(len(args)):
                                self.game_ctrl.say_to(player, "§c菜单参数数量错误")
                                return
                            tri.func(player, args)
                    else:
                        with Utils.ChatbarLock(player, self.on_menu_warn):
                            if not tri.args_pd(len(args)):
                                self.game_ctrl.say_to(player, "§c菜单参数数量错误")
                                return
                            tri.func(player, args)

    def on_menu_warn(self, player: str):
        self.game_ctrl.say_to(player, "§c退出当前菜单才能继续唤出菜单")



'''
        )
    )


process_files()
