import traceback
from collections.abc import Callable

from tooldelta.color_print import Print
from tooldelta.internal.types import Player, Chat
from ..exceptions import (
    PluginAPINotFoundError,
    PluginAPIVersionError,
)


ON_ERROR_CB = Callable[[str, Exception, str], None]
plugins_funcs: dict[str, list[tuple[str, Callable]]] = {
    "on_def": [],
    "on_inject": [],
    "on_player_prejoin": [],
    "on_player_join": [],
    "on_player_message": [],
    "on_player_death": [],
    "on_player_leave": [],
    "on_frame_exit": [],
    "on_reload": [],
}
# 新版的 cbs
on_preload_cbs: list[Callable[[], None]] = []
on_active_cbs: list[Callable[[], None]] = []
on_player_join_cbs: list[Callable[[Player], None]] = []
on_player_leave_cbs: list[Callable[[Player], None]] = []
on_player_message: list[Callable[[Chat], None]] = []

packet_funcs: dict[int, list[Callable]] = {}
broadcast_evts_listener: dict[str, list[Callable]] = {}
loaded_plugin_modules = []


def reload():
    """系统调用, 重置所有处理函数"""
    for v in plugins_funcs.values():
        v.clear()
    for v in plugins_funcs.values():
        v.clear()
    for v in packet_funcs.values():
        v.clear()


def execute_def(onerr: ON_ERROR_CB) -> None:
    """执行插件的二次初始化方法

    Args:
        onerr (Callable[[str, Exception, str], None], optional): 插件出错时的处理方法。Defaults to NON_FUNC.

    Raises:
        SystemExit: 缺少前置
        SystemExit: 前置版本过低
    """
    try:
        for name, func in plugins_funcs["on_def"]:
            func()
    except PluginAPINotFoundError as err:
        Print.print_err(f"插件 {name} 需要包含该种接口的前置组件：{err.name}")
        raise SystemExit from err
    except PluginAPIVersionError as err:
        Print.print_err(
            f"插件 {name} 需要该前置组件 {err.name} 版本：{err.m_ver}, 但是现有版本过低：{err.n_ver}"
        )
        raise SystemExit from err
    except Exception as err:
        onerr(name, err, traceback.format_exc())
        raise SystemExit


def execute_init(onerr: ON_ERROR_CB) -> None:
    """执行插件的连接游戏后初始化方法

    Args:
        onerr (Callable[[str, Exception, str], None], optional): 插件出错时的处理方法
    """
    for name, func in plugins_funcs["on_inject"]:
        try:
            func()
        except Exception as err:
            onerr(name, err, traceback.format_exc())


def execute_player_prejoin(player, onerr: ON_ERROR_CB) -> None:
    """执行玩家加入前的方法

    Args:
        player (_type_): 玩家
        onerr (Callable[[str, Exception, str], None], optional): 插件出错时的处理方法
    """
    for name, func in plugins_funcs["on_player_prejoin"]:
        try:
            func(player)
        except Exception as err:
            onerr(name, err, traceback.format_exc())


def execute_player_join(player: Player, onerr: ON_ERROR_CB) -> None:
    """执行玩家加入的方法

    Args:
        player (str): 玩家
        onerr (Callable[[str, Exception, str], None], optional): q 插件出错时的处理方法
    """
    for name, func in plugins_funcs["on_player_join"]:
        try:
            func(player.name)
        except Exception as err:
            onerr(name, err, traceback.format_exc())


def execute_chat(
    chat: Chat,
    onerr: ON_ERROR_CB,
) -> None:
    """执行玩家消息的方法

    Args:
        player (str): 玩家
        msg (str): 消息
        onerr (Callable[[str, Exception, str], None], optional): 插件出错时的处理方法
    """
    for name, func in plugins_funcs["on_player_message"]:
        try:
            func(chat.player.name, chat.msg)
        except Exception as err:
            onerr(name, err, traceback.format_exc())


def execute_player_leave(player: Player, onerr: ON_ERROR_CB) -> None:
    """执行玩家离开的方法

    Args:
        player (str): 玩家
        onerr (Callable[[str, Exception, str], None], optional): 插件出错时的处理方法
    """
    for name, func in plugins_funcs["on_player_leave"]:
        try:
            func(player.name)
        except Exception as err:
            onerr(name, err, traceback.format_exc())


def execute_frame_exit(signal: int, reason: str, onerr: ON_ERROR_CB):
    """执行框架退出的方法

    Args:
        onerr (Callable[[str, Exception, str], None], optional): 插件出错时的处理方法
    """
    for name, func in plugins_funcs["on_frame_exit"]:
        try:
            func(signal, reason)
        except Exception as err:
            onerr(name, err, traceback.format_exc())


def execute_reloaded(onerr: ON_ERROR_CB):
    """执行插件重载的方法

    Args:
        onerr (Callable[[str, Exception, str], None], optional): 插件出错时的处理方法
    """
    for name, func in plugins_funcs["on_reload"]:
        try:
            func()
        except Exception as err:
            onerr(name, err, traceback.format_exc())


def execute_packet_funcs(pktID: int, pkt: dict, onerr: ON_ERROR_CB) -> bool:
    """处理数据包监听器

    Args:
        pktID (int): 数据包 ID
        pkt (dict): 数据包

    Returns:
        bool: 是否处理成功
    """
    d = packet_funcs.get(pktID)
    if d:
        for func in d:
            try:
                res = func(pkt)
                if res:
                    return True
            except Exception as err:
                onerr("插件方法:" + func.__name__, err, traceback.format_exc())
    return False
