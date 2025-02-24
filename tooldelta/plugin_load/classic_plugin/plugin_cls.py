import os
from typing import TYPE_CHECKING
from collections.abc import Callable

from tooldelta.constants import TOOLDELTA_PLUGIN_DATA_DIR
from tooldelta.color_print import Print
from tooldelta.internal.types import Player, Chat, InternalBroadcast, FrameExit
from . import event_cbs

if TYPE_CHECKING:
    from tooldelta import ToolDelta


class Plugin:
    "插件主类"

    name: str = ""
    "插件名"
    version = (0, 0, 1)
    "插件版本号"
    author: str = "?"
    "作者名"
    description = "..."
    "简介"

    __path_created__ = False

    def __init__(self, frame: "ToolDelta"):
        self.frame = frame
        self.game_ctrl = frame.get_game_control()

    @property
    def data_path(self) -> str:
        "该插件的数据文件夹路径 (调用时直接创建数据文件夹)"
        path = os.path.join(TOOLDELTA_PLUGIN_DATA_DIR, self.name)
        if not self.__path_created__:
            os.makedirs(path, exist_ok=True)
            self.__path_created__ = True
        return path

    def make_data_path(self):
        os.makedirs(os.path.join(TOOLDELTA_PLUGIN_DATA_DIR, self.name), exist_ok=True)
        self.__path_created__ = True

    def print(self, msg: str):
        Print.print_inf(f"{self.name}: {msg}")

    def format_data_path(self, *paths: str):
        return os.path.join(self.data_path, *paths)

    def ListenPreload(self, cb: Callable[[], None]):
        """
        监听预加载事件
        预加载事件: 在读取插件后、和游戏建立连接前触发一次

        Args:
            cb (Callable[[], None]): 监听回调
        """
        event_cbs.on_preload_cbs.append((self, cb))

    def ListenActive(self, cb: Callable[[], None]):
        """
        监听连接建立事件
        连接建立事件: 在框架和游戏完全建立连接时触发一次

        Args:
            cb (Callable[[], None]): 监听回调
        """
        event_cbs.on_active_cbs.append((self, cb))

    def ListenPlayerJoin(self, cb: Callable[[Player], None]):
        """
        监听玩家加入事件
        玩家加入事件: 在有玩家加入游戏时触发一次

        Args:
            cb (Callable[[Player], None]): 监听回调, 传参: 玩家 (Player)
        """
        event_cbs.on_player_join_cbs.append((self, cb))

    def ListenPlayerLeave(self, cb: Callable[[Player], None]):
        """
        监听玩家退出事件
        玩家退出事件: 在有玩家退出游戏时触发一次

        Args:
            cb (Callable[[Player], None]): 监听回调, 传参: 玩家 (Player)
        """
        event_cbs.on_player_leave_cbs.append((self, cb))

    def ListenChat(self, cb: Callable[[Chat], None]):
        """
        监听玩家聊天事件
        玩家聊天事件: 在有玩家在聊天栏发言时触发一次

        Args:
            cb (Callable[[Player], None]): 监听回调, 传参: 聊天事件 (Chat)
        """
        event_cbs.on_chat_cbs.append((self, cb))

    def ListenFrameExit(self, cb: Callable[[FrameExit], None]):
        """
        监听框架退出事件
        框架退出事件: 在框架退出/插件即将重载时触发一次

        Args:
            cb (Callable[[Player], None]): 监听回调, 传参: 聊天事件 (Chat)
        """
        event_cbs.on_frame_exit_cbs.append((self, cb))

    def ListenInternalBroadcast(
        self, broadcast_name: str, cb: Callable[[InternalBroadcast], None]
    ):
        """
        监听广播事件
        广播事件: 在产生广播事件时触发一次

        Args:
            broadcast_name (str): 广播事件名
            cb (Callable[[InternalBroadcast], None]): 监听回调, 传参: 广播事件 (InternalBroadcast)
        """
        event_cbs.broadcast_listener.setdefault(broadcast_name, [])
        event_cbs.broadcast_listener[broadcast_name].append(cb)
