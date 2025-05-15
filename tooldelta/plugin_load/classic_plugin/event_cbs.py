from typing import TYPE_CHECKING, TypeVar
from collections.abc import Callable

from ...mc_bytes_packet.base_bytes_packet import BaseBytesPacket
from ...utils import fmts
from ...constants import PacketIDS
from ...internal.types import Player, Chat, InternalBroadcast, FrameExit
from ..basic import ON_ERROR_CB
from ..exceptions import (
    PluginAPINotFoundError,
    PluginAPIVersionError,
)

if TYPE_CHECKING:
    from .plugin_cls import Plugin
    from tooldelta.internal.packet_handler import (
        DictPacketListener,
        BytesPacketListener,
    )

T = TypeVar("T")
PluginEvent = tuple["Plugin", T]


on_preload_cbs: list[PluginEvent[Callable[[], None]]] = []
on_active_cbs: list[PluginEvent[Callable[[], None]]] = []
on_player_join_cbs: list[PluginEvent[Callable[[Player], None]]] = []
on_player_leave_cbs: list[PluginEvent[Callable[[Player], None]]] = []
on_chat_cbs: list[PluginEvent[Callable[[Chat], None]]] = []
on_frame_exit_cbs: list[PluginEvent[Callable[[FrameExit], None]]] = []
on_reloaded_cbs: list[PluginEvent[Callable[[], None]]] = []
dict_packet_funcs: dict[PacketIDS, list["DictPacketListener"]] = {}
bytes_packet_funcs: dict[PacketIDS, list["BytesPacketListener"]] = {}
broadcast_listener: dict[str, list[Callable[[InternalBroadcast], None]]] = {}


def reload():
    """系统调用, 重置所有处理函数"""
    on_preload_cbs.clear()
    on_active_cbs.clear()
    on_player_join_cbs.clear()
    on_player_leave_cbs.clear()
    on_chat_cbs.clear()
    on_frame_exit_cbs.clear()
    on_reloaded_cbs.clear()
    dict_packet_funcs.clear()
    bytes_packet_funcs.clear()
    broadcast_listener.clear()


def execute_preload(onerr: ON_ERROR_CB) -> None:
    """执行插件的二次初始化方法

    Args:
        onerr (Callable[[str, Exception, str], None], optional): 插件出错时的处理方法。Defaults to NON_FUNC.

    Raises:
        SystemExit: 缺少前置
        SystemExit: 前置版本过低
    """
    try:
        for p, func in on_preload_cbs:
            name = p.name
            func()
    except PluginAPINotFoundError as err:
        fmts.print_err(f"插件 {name} 需要包含该种接口的前置组件：{err.name}")
        raise SystemExit from err
    except PluginAPIVersionError as err:
        fmts.print_err(
            f"插件 {name} 需要该前置组件 {err.name} 版本：{err.m_ver}, 但是现有版本过低：{err.n_ver}"
        )
        raise SystemExit from err
    except Exception as err:
        onerr(name, err)
        raise SystemExit


def execute_active(onerr: ON_ERROR_CB) -> None:
    """执行插件的连接游戏后初始化方法

    Args:
        onerr (Callable[[str, Exception, str], None], optional): 插件出错时的处理方法
    """
    try:
        for p, func in on_active_cbs:
            name = p.name
            func()
    except Exception as err:
        onerr(name, err)


def execute_player_join(player: Player, onerr: ON_ERROR_CB) -> None:
    """执行玩家加入的方法

    Args:
        player (str): 玩家
        onerr (Callable[[str, Exception, str], None], optional): q 插件出错时的处理方法
    """
    try:
        for p, func in on_player_join_cbs:
            name = p.name
            func(player)
    except Exception as err:
        onerr(name, err)


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
    try:
        for p, func in on_chat_cbs:
            name = p.name
            func(chat)
    except Exception as err:
        onerr(name, err)


def execute_player_leave(player: Player, onerr: ON_ERROR_CB) -> None:
    """执行玩家离开的方法

    Args:
        player (str): 玩家
        onerr (Callable[[str, Exception, str], None], optional): 插件出错时的处理方法
    """
    try:
        for p, func in on_player_leave_cbs:
            name = p.name
            func(player)
    except Exception as err:
        onerr(name, err)


def execute_frame_exit(evt: FrameExit, onerr: ON_ERROR_CB):
    """执行框架退出的方法

    Args:
        onerr (Callable[[str, Exception, str], None], optional): 插件出错时的处理方法
    """
    try:
        for p, func in on_frame_exit_cbs:
            name = p.name
            func(evt)
    except Exception as err:
        onerr(name, err)


def execute_reloaded(onerr: ON_ERROR_CB):
    """执行插件重载的方法

    Args:
        onerr (Callable[[str, Exception, str], None], optional): 插件出错时的处理方法
    """
    try:
        for p, func in on_reloaded_cbs:
            name = p.name
            func()
    except Exception as err:
        onerr(name, err)


def execute_dict_packet_funcs(pktID: PacketIDS, pkt: dict, onerr: ON_ERROR_CB) -> bool:
    """处理字典类型的数据包监听器

    Args:
        pktID (int): 数据包 ID
        pkt (dict): 字典数据包

    Returns:
        bool: 是否处理成功
    """
    d = dict_packet_funcs.get(pktID)
    if d:
        try:
            for func in d:
                res = func(pkt)
                if res is True:
                    return True
        except Exception as err:
            onerr("插件方法:" + func.__name__, err)
    return False


def execute_bytes_packet_funcs(
    pktID: PacketIDS, pkt: BaseBytesPacket, onerr: ON_ERROR_CB
) -> bool:
    """处理二进制类型的数据包监听器

    Args:
        pktID (int): 数据包 ID
        pkt (BaseBytesPacket): 二进制数据包

    Returns:
        bool: 是否处理成功
    """
    d = bytes_packet_funcs.get(pktID)
    if d:
        try:
            for func in d:
                res = func(pkt)
                if res is True:
                    return True
        except Exception as err:
            onerr("插件方法:" + func.__name__, err)
    return False
