import os
from typing import TYPE_CHECKING, TypeVar, Any
from collections.abc import Callable

from ...constants import TOOLDELTA_PLUGIN_DATA_DIR, PacketIDS
from ...utils import fmts
from ...internal.types import Player, Chat, InternalBroadcast, FrameExit
from . import event_cbs

if TYPE_CHECKING:
    from tooldelta import ToolDelta
    from tooldelta.internal.packet_handler import PacketListener
    from tooldelta.plugin_load.plugins import PluginGroup

    PLUGIN_TYPE = TypeVar("PLUGIN_TYPE", bound="Plugin")


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

    # 如果将其作为 API 插件 ---
    _api_names: list[str] | None = None
    _api_ver: tuple[int, int, int] = (0, 0, 0)
    # ---

    # secret_vars ---
    __path_created__ = False
    _plugin_group: "PluginGroup | None" = None
    # ---

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
        fmts.print_inf(f"{self.name}: {msg}")

    def format_data_path(self, *paths: str):
        return os.path.join(self.data_path, *paths)

    def ListenPreload(self, cb: Callable[[], Any]):
        """
        监听预加载事件
        预加载事件: 在读取插件后、和游戏建立连接前触发一次

        Args:
            cb (Callable[[], None]): 监听回调
        """
        event_cbs.on_preload_cbs.append((self, cb))

    def ListenActive(self, cb: Callable[[], Any]):
        """
        监听连接建立事件
        连接建立事件: 在框架和游戏完全建立连接时触发一次

        Args:
            cb (Callable[[], None]): 监听回调
        """
        event_cbs.on_active_cbs.append((self, cb))

    def ListenPlayerJoin(self, cb: Callable[[Player], Any]):
        """
        监听玩家加入事件
        玩家加入事件: 在有玩家加入游戏时触发一次

        Args:
            cb (Callable[[Player], None]): 监听回调, 传参: 玩家 (Player)
        """
        event_cbs.on_player_join_cbs.append((self, cb))

    def ListenPlayerLeave(self, cb: Callable[[Player], Any]):
        """
        监听玩家退出事件
        玩家退出事件: 在有玩家退出游戏时触发一次

        Args:
            cb (Callable[[Player], None]): 监听回调, 传参: 玩家 (Player)
        """
        event_cbs.on_player_leave_cbs.append((self, cb))

    def ListenChat(self, cb: Callable[[Chat], Any]):
        """
        监听玩家聊天事件
        玩家聊天事件: 在有玩家在聊天栏发言时触发一次

        Args:
            cb (Callable[[Player], None]): 监听回调, 传参: 聊天事件 (Chat)
        """
        event_cbs.on_chat_cbs.append((self, cb))

    def ListenFrameExit(self, cb: Callable[[FrameExit], Any]):
        """
        监听框架退出事件
        框架退出事件: 在框架退出/插件即将重载时触发一次

        Args:
            cb (Callable[[Player], None]): 监听回调, 传参: 聊天事件 (Chat)
        """
        event_cbs.on_frame_exit_cbs.append((self, cb))

    def ListenPacket(self, pkt_id: PacketIDS | list[PacketIDS], cb: "PacketListener"):
        """
        监听数据包事件

        Args:
            pkt_id (PacketIDS): 数据包ID
            cb ((dict) -> bool): 数据包监听回调, 返回 True 为拦截该数据包
        """
        if isinstance(pkt_id, int):
            pkt_ids = [pkt_id]
        else:
            pkt_ids = pkt_id
        for pkt_id in pkt_ids:
            event_cbs.packet_funcs.setdefault(pkt_id, [])
            event_cbs.packet_funcs[pkt_id].append(cb)

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

    def BroadcastEvent(self, evt: InternalBroadcast):
        """
        向全局广播一个特定事件, 可以传入附加信息参数
        Args:
            evt (InternalBroadcast): 事件
        Returns:
             list[Any]: 收集到的数据的列表 (如果接收到广播的方法返回了数据的话)
        """
        if self._plugin_group is None:
            raise RuntimeError("不能在非运行环境调用此方法")
        return self._plugin_group.brocast_event(evt)

    def GetPluginAPI(
        self,
        api_name: str,
        min_version: tuple[int, int, int] = (0, 0, 0),
        force=True,
    ):
        """获取插件 API

        Args:
            api_name (str): 插件 API 名
            min_version (tuple, optional): API 所需的最低版本 (若不填则默认不检查最低版本)
            force: 若为 False, 则在找不到插件 API 时不报错而是返回 None

        Raises:
            PluginAPIVersionError: 插件 API 版本错误
            PluginAPINotFoundError: 无法找到 API 插件

        Returns:
            Plugin: 插件 API
        """
        return self.frame.plugin_group.get_plugin_api(
            apiName=api_name, min_version=min_version, force=force
        )

    def get_typecheck_plugin_api(self, api_cls: type["PLUGIN_TYPE"]) -> "PLUGIN_TYPE":
        """
        对外源导入 (import) 的 API 插件类进行类型实例化。
        可以使得你所使用的 IDE 对导入的插件 API 类进行识别和高亮其所含方法。
        请在 TYPE_CHECKING 的代码块下使用。

        Args:
            api_cls (type[_PLUGIN_CLS_TYPE]): 导入的 API 插件类

        Raises:
            ValueError: API 插件类未被注册

        Returns:
            _PLUGIN_CLS_TYPE: API 插件实例

        使用方法如下:
        ```python
            p_api = get_plugin_api("...")
            if TYPE_CHECKING:
                from outer_api import api_cls_xx
                p_api = get_typecheck_plugin_api(api_cls_xx)
        ```
        """
        raise NotImplementedError("仅能在 TYPE_CHECKING 代码块调用此方法")
