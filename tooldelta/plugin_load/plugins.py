"插件加载器框架"

import asyncio
import os
import traceback
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, TypeVar

from .. import utils
from ..utils import fmts
from ..constants import (
    TOOLDELTA_CLASSIC_PLUGIN,
    TOOLDELTA_INJECTED_PLUGIN,
    TOOLDELTA_PLUGIN_DIR,
    SysStatus,
)
from .exceptions import (
    PluginAPINotFoundError,
    PluginAPIVersionError,
)
from ..constants import TextType, PacketIDS
from ..internal.packet_handler import PacketHandler
from ..internal.types import Player, Chat, InternalBroadcast, FrameExit
from ..game_utils import _set_frame
from .classic_plugin.loader import Plugin
from .classic_plugin import event_cbs as classic_plugin
from .classic_plugin import loader as classic_plugin_loader
from .injected_plugin import loader as injected_plugin
from .basic import auto_move_plugin_dir, non_func, ON_ERROR_CB

if TYPE_CHECKING:
    from ..frame import ToolDelta

VT = TypeVar("VT")


class PluginGroup:
    "插件组类, 存放插件代码有关数据"

    def __init__(self, frame: "ToolDelta"):
        self.set_frame(frame)
        self.broadcast_listeners: dict[
            str, list[Callable[[InternalBroadcast], Any]]
        ] = {}
        self.plugin_listen_packets: set[PacketIDS] = set()
        self.plugins_api: dict[str, Plugin] = {}
        self.normal_plugin_loaded_num = 0
        self.injected_plugin_loaded_num = 0
        self.loaded_plugin_ids = []
        self.on_err_cb = self.linked_frame.on_plugin_err

    def reload(self):
        """
        重载插件框架
        这是一个不很安全的操作, 多次 reload 后
        可能会因为一些插件线程由于底层原因无法被停止, 或者有垃圾无法被回收, 导致内存泄露等问题
        """
        self.plugins_api = {}
        self.broadcast_listeners = {}
        self.execute_frame_exit(FrameExit(SysStatus.NORMAL_EXIT, "normal"))
        classic_plugin.reload()
        injected_plugin.reload()
        fmts.print_inf("正在重新读取所有插件")
        self.load_plugins()
        self.execute_reloaded(self.linked_frame.on_plugin_err)
        fmts.print_inf("开始执行插件游戏初始化方法")
        self.execute_init()
        fmts.print_suc("重载插件已完成")

    def hook_packet_handler(self, hdl: "PacketHandler"):
        self.plugin_listen_packets = set(classic_plugin.packet_funcs.keys())
        self.plugin_listen_packets |= set(injected_plugin.packet_funcs.keys())
        for pkID in self.plugin_listen_packets:

            def any_pk_handler(pkt: dict, pkID=pkID):
                return self.handle_packets(pkID, pkt)

            hdl.add_packet_listener(pkID, any_pk_handler, 0)
        hdl.add_packet_listener(PacketIDS.Text, self.handle_text_packet)

    def brocast_event(self, evt: InternalBroadcast) -> list[Any]:
        callback_list = []
        res = self.broadcast_listeners.get(evt.evt_name)
        if res:
            for f in res:
                res2 = f(evt)
                if res2:
                    callback_list.append(res2)
        return callback_list

    def get_plugin_api(
        self, apiName: str, min_version: tuple | None = None, force=True
    ) -> Any:
        api = self.plugins_api.get(apiName)
        if api:
            if min_version and api.version < min_version:
                raise PluginAPIVersionError(apiName, min_version, api.version)
            return api
        if force:
            raise PluginAPINotFoundError(apiName)
        return None

    def set_frame(self, frame: "ToolDelta") -> None:
        """为各个框架分发关联的系统框架"""
        self.linked_frame = frame
        _set_frame(frame)

    def load_plugins(self) -> None:
        """
        读取所有插件/重载所有插件 并对插件进行预初始化

        Raises:
            SystemExit: 读取插件出现问题
        """
        if self.linked_frame is None or self.linked_frame.on_plugin_err is None:
            raise ValueError("无法读取插件，请确保系统已初始化")
        for fdir in os.listdir(TOOLDELTA_PLUGIN_DIR):
            if fdir not in (TOOLDELTA_CLASSIC_PLUGIN, TOOLDELTA_INJECTED_PLUGIN):
                auto_move_plugin_dir(fdir)
        self.loaded_plugin_ids = []
        self.normal_plugin_loaded_num = 0
        self.injected_plugin_loaded_num = 0
        try:
            fmts.print_inf("§a正在使用 §bHiQuality §dDX§r§a 模式读取插件")
            classic_plugin_loader.read_plugins(self)
            asyncio.run(injected_plugin.load_plugin(self))
            # 主动读取类式插件监听的数据包
            for i in classic_plugin.packet_funcs.keys():
                self.__add_listen_packet_id(i)
            # 主动读取类式插件监听的广播事件器
            self.broadcast_listeners.update(classic_plugin.broadcast_listener)
            # 主动读取注入式插件监听的数据包
            for i in injected_plugin.packet_funcs.keys():
                self.__add_listen_packet_id(i)
            # 因为注入式插件自带一个handler, 所以不用再注入方法
            fmts.print_suc("所有插件读取完毕, 将进行插件初始化")
            self.execute_preload(self.linked_frame.on_plugin_err)
            fmts.print_suc(
                f"插件初始化成功, 载入 §f{self.normal_plugin_loaded_num}§a 个类式插件, §f{self.injected_plugin_loaded_num}§a 个注入式插件"
            )
        except Exception as err:
            err_str = "\n".join(traceback.format_exc().split("\n")[1:])
            fmts.print_err(f"加载插件出现问题：\n{err_str}")
            raise SystemExit from err

    def execute_preload(self, onerr: ON_ERROR_CB = non_func) -> None:
        """执行插件的二次初始化方法

        Args:
            onerr (Callable[[str, Exception, str], None], optional): 插件出错时的处理方法。Defaults to non_func.

        Raises:
            SystemExit: 缺少前置
            SystemExit: 前置版本过低
        """
        classic_plugin.execute_preload(onerr)

    def execute_init(self, onerr: ON_ERROR_CB = non_func) -> None:
        """执行插件的连接游戏后初始化方法

        Args:
            onerr (Callable[[str, Exception, str], None], optional): 插件出错时的处理方法
        """
        classic_plugin.execute_active(onerr)
        asyncio.run(injected_plugin.execute_init())
        utils.createThread(
            asyncio.run, (injected_plugin.execute_repeat(),), "注入式插件定时任务"
        )

    def execute_player_prejoin(
        self, player: str, onerr: ON_ERROR_CB = non_func
    ) -> None:
        """执行玩家加入前的方法

        Args:
            player (_type_): 玩家
            onerr (Callable[[str, Exception, str], None], optional): 插件出错时的处理方法
        """
        asyncio.run(injected_plugin.execute_player_prejoin(player))

    def execute_player_join(
        self, player: Player, onerr: ON_ERROR_CB = non_func
    ) -> None:
        """执行玩家加入的方法

        Args:
            player (str): 玩家
            onerr (Callable[[str, Exception, str], None], optional): q 插件出错时的处理方法
        """
        classic_plugin.execute_player_join(player, onerr)
        asyncio.run(injected_plugin.execute_player_join(player.name))

    def execute_chat(
        self,
        chat: Chat,
        onerr: ON_ERROR_CB = non_func,
    ) -> None:
        """执行玩家消息的方法

        Args:
            player (str): 玩家
            msg (str): 消息
            onerr (Callable[[str, Exception, str], None], optional): 插件出错时的处理方法
        """
        classic_plugin.execute_chat(chat, onerr)
        asyncio.run(injected_plugin.execute_player_message(chat.player.name, chat.msg))

    def execute_player_leave(
        self, player: Player, onerr: ON_ERROR_CB = non_func
    ) -> None:
        """执行玩家离开的方法

        Args:
            player (str): 玩家
            onerr (Callable[[str, Exception, str], None], optional): 插件出错时的处理方法
        """
        classic_plugin.execute_player_leave(player, onerr)
        asyncio.run(injected_plugin.execute_player_left(player.name))

    def execute_frame_exit(self, evt: FrameExit, onerr: ON_ERROR_CB = non_func):
        """执行框架退出的方法

        Args:
            onerr (Callable[[str, Exception, str], None], optional): 插件出错时的处理方法
        """
        classic_plugin.execute_frame_exit(evt, onerr)
        asyncio.run(injected_plugin.execute_frame_exit())

    def execute_reloaded(self, onerr: ON_ERROR_CB = non_func):
        """执行插件重载的方法

        Args:
            onerr (Callable[[str, Exception, str], None], optional): 插件出错时的处理方法
        """
        classic_plugin.execute_reloaded(onerr)
        asyncio.run(injected_plugin.execute_reloaded())

    def handle_packets(self, pktID: PacketIDS, pkt: dict) -> bool:
        """处理数据包监听器

        Args:
            pktID (int): 数据包 ID
            pkt (dict): 数据包

        Returns:
            bool: 是否处理成功
        """
        blocking = classic_plugin.execute_packet_funcs(pktID, pkt, self.on_err_cb)
        asyncio.run(injected_plugin.execute_packet_funcs(pktID, pkt))
        return blocking

    def handle_text_packet(self, pkt: dict):
        match pkt["TextType"]:
            case TextType.TextTypeTranslation:
                if pkt["Message"] == "§e%multiplayer.player.joined":
                    playername = pkt["Parameters"][0]
                    if player := self.linked_frame.players_maintainer.getPlayerByName(
                        playername
                    ):
                        self.execute_player_join(player)
                    else:
                        fmts.print_war(f"玩家 {playername} 未找到")
                elif pkt["Message"] == "§e%multiplayer.player.left":
                    playername = pkt["Parameters"][0]
                    if player := self.linked_frame.players_maintainer.getPlayerByName(
                        playername
                    ):
                        self.execute_player_leave(player)
                    else:
                        fmts.print_war(f"玩家 {playername} 未找到")
            case TextType.TextTypeChat | TextType.TextTypeWhisper:
                raw_name = pkt["SourceName"]
                msg = pkt["Message"]
                cleaned_name = utils.to_plain_name(raw_name)
                if player := self.linked_frame.players_maintainer.getPlayerByName(
                    cleaned_name
                ):
                    chat = Chat(player, msg)
                    self.execute_chat(chat)
                else:
                    fmts.print_war(f"玩家 {cleaned_name} 未找到")
        return False

    help = staticmethod(classic_plugin_loader.help)

    def __add_listen_packet_id(self, packetType: PacketIDS) -> None:
        """添加数据包监听，仅在系统内部使用

        Args:
            packetType (int): 数据包 ID

        Raises:
            ValueError: 无法添加数据包监听，请确保已经加载了系统组件
        """
        self.plugin_listen_packets.add(packetType)
