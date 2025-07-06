from typing import TYPE_CHECKING, TypeVar, Any
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
PluginEvents_P = dict[int, list[tuple["Plugin", T]]]
"具有优先级的回调表"


on_preload_cbs: PluginEvents_P[Callable[[], None]] = {}
on_active_cbs: PluginEvents_P[Callable[[], None]] = {}
on_player_join_cbs: PluginEvents_P[Callable[[Player], None]] = {}
on_player_leave_cbs: PluginEvents_P[Callable[[Player], None]] = {}
on_chat_cbs: PluginEvents_P[Callable[[Chat], None]] = {}
on_frame_exit_cbs: PluginEvents_P[Callable[[FrameExit], None]] = {}
on_reloaded_cbs: PluginEvents_P[Callable[[], None]] = {}
dict_packet_funcs: dict[PacketIDS, PluginEvents_P["DictPacketListener"]] = {}
bytes_packet_funcs: dict[PacketIDS, PluginEvents_P["BytesPacketListener"]] = {}
broadcast_listener: dict[str, PluginEvents_P[Callable[[InternalBroadcast], Any]]] = {}


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


def run_by_priority(listeners: PluginEvents_P[Callable], args: tuple, onerr: ON_ERROR_CB,):
    for _, sub_listeners in sorted(listeners.items(), reverse=True):
        for plugin, listener in sub_listeners:
            try:
                is_blocking = listener(*args)
                if is_blocking is True:
                    return True
            except Exception as e:
                onerr(plugin.name, e)
    return False


def execute_preload(onerr: ON_ERROR_CB) -> None:
    """执行插件的二次初始化方法

    Args:
        onerr (Callable[[str, Exception, str], None], optional): 插件出错时的处理方法。Defaults to NON_FUNC.

    Raises:
        SystemExit: 缺少前置
        SystemExit: 前置版本过低
    """
    def error_handler(plugin_name: str, err: Exception):
        if isinstance(err, PluginAPINotFoundError):
            fmts.print_err(f"插件 {plugin_name} 需要包含该种接口的前置组件：{err.api_name}")
            raise SystemExit from err
        elif isinstance(err, PluginAPIVersionError):
            fmts.print_err(
                f"插件 {plugin_name} 需要该前置组件 {err.name} 版本：{err.m_ver}, 但是现有版本过低：{err.n_ver}"
            )
            raise SystemExit from err
        else:
            onerr(plugin_name, err)
            raise SystemExit
    run_by_priority(on_preload_cbs, (), error_handler)


def execute_active(onerr: ON_ERROR_CB) -> None:
    """执行插件的连接游戏后初始化方法

    Args:
        onerr (Callable[[str, Exception, str], None], optional): 插件出错时的处理方法
    """
    run_by_priority(on_active_cbs, (), onerr)


def execute_player_join(player: Player, onerr: ON_ERROR_CB) -> None:
    """执行玩家加入的方法

    Args:
        player (str): 玩家
        onerr (Callable[[str, Exception, str], None], optional): q 插件出错时的处理方法
    """
    run_by_priority(on_player_join_cbs, (player,), onerr)


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
    run_by_priority(on_chat_cbs, (chat,), onerr)


def execute_player_leave(player: Player, onerr: ON_ERROR_CB) -> None:
    """执行玩家离开的方法

    Args:
        player (str): 玩家
        onerr (Callable[[str, Exception, str], None], optional): 插件出错时的处理方法
    """
    run_by_priority(on_player_leave_cbs, (player,), onerr)


def execute_frame_exit(evt: FrameExit, onerr: ON_ERROR_CB):
    """执行框架退出的方法

    Args:
        onerr (Callable[[str, Exception, str], None], optional): 插件出错时的处理方法
    """
    run_by_priority(on_frame_exit_cbs, (evt,), onerr)


def execute_reloaded(onerr: ON_ERROR_CB):
    """执行插件重载的方法

    Args:
        onerr (Callable[[str, Exception, str], None], optional): 插件出错时的处理方法
    """
    run_by_priority(on_reloaded_cbs, (), onerr)


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
        return run_by_priority(d, (pkt,), onerr)
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
        return run_by_priority(d, (pkt,), onerr)
    return False
