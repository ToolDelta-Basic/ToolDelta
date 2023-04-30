from typing import Callable, overload

class _Print:
    std_color_list: list[list[str]]
    @overload
    def _mccolor_console_common(this, text: str) -> str:...
    @overload
    def _mccolor_console_st1(this, text: str) -> str:...
    @overload
    def print_with_info(this, text: str, info: str) -> None:...
    @overload
    def print_err(this, text: str) -> None:...
    @overload
    def print_inf(this, text: str) -> None:...
    @overload
    def print_suc(this, text: str) -> None:...
    @overload
    def print_war(this, text: str) -> None:...

class Frame:
    class FrameBasic:
        max_connect_fb_time: int
        connect_fb_start_time: float

    sys = FrameBasic()
    Print: _Print
    con: int
    serverNumber: str
    serverPasswd: str
    consoleMenu: list
    @overload
    def add_console_cmd_trigger(this, triggers: list[str], usage: str, func: Callable[[str], None]) -> None:...
    @overload
    def init_basic_help_menu(this, cmd_str) -> None:...
    @overload   
    def get_console_menus(this) -> list:...
    # Can custom
    @overload
    def on_plugin_err(this, pluginName: str, exc: Exception, trace: str) -> None:...

class Plugin:
    runcode: dict[str, str]
    name: str
    dotcs_old_type: bool

class PluginGroup:
    plugins: list[Plugin] = []
    @overload
    def add_plugin(this, plugin: Plugin) -> None:...
    @overload
    def listen_packet():...

plugin_group: PluginGroup
frame: Frame