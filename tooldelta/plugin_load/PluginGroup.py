"插件加载器框架"

import asyncio
import os
import traceback
from typing import TYPE_CHECKING, Any, Callable, Union, TypeVar

from ..color_print import Print
from .classic_plugin import (
    Plugin,
    add_plugin,
    add_plugin_as_api,
    _init_frame,
    _PLUGIN_CLS_TYPE,
)
from ..utils import Utils
from .injected_plugin import (
    execute_init,
    execute_player_prejoin,
    execute_player_join,
    execute_player_message,
    execute_death_message,
    execute_player_left,
    execute_frame_exit,
    execute_command_say,
    execute_repeat,
)
from ..plugin_load import (
    classic_plugin,
    injected_plugin,
    NON_FUNC,
    PluginAPINotFoundError,
    PluginAPIVersionError,
    auto_move_plugin_dir,
)
from ..constants import (
    PRG_NAME,
    TOOLDELTA_PLUGIN_DIR,
    TOOLDELTA_CLASSIC_PLUGIN,
    TOOLDELTA_INJECTED_PLUGIN,
)
from ..game_utils import _set_frame
from .injected_plugin.movent import set_frame as _set_frame_inj

if TYPE_CHECKING:
    from ..frame import ToolDelta

_TV = TypeVar("_TV")
_SUPER_CLS = TypeVar("_SUPER_CLS")


class PluginGroup:
    "插件组"

    plugins: list[Plugin] = []
    plugins_funcs: dict[str, list] = {
        "on_def": [],
        "on_inject": [],
        "on_player_prejoin": [],
        "on_player_join": [],
        "on_player_message": [],
        "on_player_death": [],
        "on_player_leave": [],
        "on_command": [],
        "on_frame_exit": [],
    }
    plugin_added_cache = {"packets": []}
    Agree_bot_patrol: list[bool] = []
    broadcast_evts_cache = {}

    def __init__(self):
        "初始化"
        self.listen_packet_ids = set()
        self._packet_funcs: dict[str, list[Callable]] = {}
        self._update_player_attributes_funcs: list[Callable] = []
        self._broadcast_listeners: dict[str, list[Callable]] = {}
        self.plugins_api: dict[str, Plugin] = {}
        self.normal_plugin_loaded_num = 0
        self.injected_plugin_loaded_num = 0
        self.loaded_plugins_name = []
        self.linked_frame: Union["ToolDelta", None] = None

    add_plugin = staticmethod(add_plugin)

    add_plugin_as_api = staticmethod(add_plugin_as_api)

    def add_packet_listener(self, pktID: int | list[int]):
        """
        添加数据包监听器
        将下面的方法作为一个 MC 数据包接收器
        Tips: 只能在插件主类里的函数使用此装饰器!

        Args:
            pktID (int | list[int]): 数据包 ID 或多个 ID

        Returns:
            Callable[[Callable], Callable]: 添加数据包监听器
        """

        def deco(func: Callable[[_SUPER_CLS, dict], bool]):
            if isinstance(pktID, int):
                self.plugin_added_cache["packets"].append((pktID, func))
            else:
                for i in pktID:
                    self.plugin_added_cache["packets"].append((i, func))
            return func

        return deco

    def add_broadcast_listener(self, evt_name: str):
        """
        添加广播事件监听器
        将下面的方法作为一个广播事件接收器
        Tips: 只能在插件主类里的函数使用此装饰器!

        Args:
            evt_name (str): 事件名

        Returns:
            Callable[[Callable], Callable]: 添加广播事件监听器

        原理:
        方法 1 广播：hi, what's ur name? 附加参数=english_only
            - 方法 2 接收到广播并被执行：方法 2(english_only) -> my name is Super. -> 收集表

        事件 1 获取到 收集表 作为返回：["my name is Super."]
        """

        def deco(
            func: Callable[[_SUPER_CLS, _TV], bool],
        ) -> Callable[[_SUPER_CLS, _TV], bool]:
            if self.broadcast_evts_cache.get(evt_name):
                self.broadcast_evts_cache[evt_name].append(func)
            else:
                self.broadcast_evts_cache[evt_name] = [func]
            return func

        return deco

    def broadcastEvt(self, evt_name: str, data: Any = None) -> list[Any]:
        """
        向全局广播一个特定事件，可以传入附加信息参数
        Args:
            evt_name (str): 事件名
            data (Any, optional): 附加信息参数
        Returns:
             list[Any]: 收集到的数据的列表 (如果接收到广播的方法返回了数据的话)
        """
        callback_list = []
        res = self._broadcast_listeners.get(evt_name)
        if res:
            for f in res:
                res2 = f(data)
                if res2:
                    callback_list.append(res2)
        return callback_list

    @staticmethod
    def help(plugin: Plugin) -> None:
        """
        查看插件帮助.
        常用于查看 get_plugin_api() 方法获取到的插件实例的帮助.
        """
        plugin_docs = "<plugins.help>: " + plugin.name + "开放的 API 接口说明:\n"
        for attr_name, attr in plugin.__dict__.items():
            if not attr_name.startswith("__") and attr.__doc__ is not None:
                plugin_docs += (
                    "\n §a"
                    + attr_name
                    + ":§f\n    "
                    + attr.__doc__.replace("\n", "\n    ")
                )
        Print.clean_print(plugin_docs)

    def checkSystemVersion(self, need_vers: tuple[int, int, int]):
        """检查 ToolDelta 系统的版本

        Args:
            need_vers (tuple[int, int, int]): 需要的版本

        Raises:
            self.linked_frame.SystemVersionException: 该组件需要的 ToolDelta 系统版本
        """
        if (
            self.linked_frame is not None
            and need_vers > self.linked_frame.sys_data.system_version
        ):
            raise self.linked_frame.SystemVersionException(
                f"该组件需要{PRG_NAME}为最低 {'.'.join([str(i) for i in self.linked_frame.sys_data.system_version])} 版本，请及时更新"
            )
        if self.linked_frame is None:
            raise ValueError(
                "无法检查 ToolDelta 系统版本，请确保已经加载了 ToolDelta 系统组件"
            )

    def get_plugin_api(
        self, apiName: str, min_version: tuple | None = None, force=True
    ) -> Any:
        """获取插件 API

        Args:
            apiName (str): 插件 API 名
            min_version (tuple | None, optional): API 最低版本 (若不填则默认不检查最低版本)
            force: 若为 False, 则在找不到插件 API 时不报错而是返回 None

        Raises:
            PluginAPIVersionError: 插件 API 版本错误
            PluginAPINotFoundError: 无法找到 API 插件

        Returns:
            Plugin: 插件 API
        """
        api = self.plugins_api.get(apiName)
        if api:
            if min_version and api.version < min_version:
                raise PluginAPIVersionError(apiName, min_version, api.version)
            return api
        if force:
            raise PluginAPINotFoundError(f"无法找到 API 插件：{apiName}")
        return None

    def set_frame(self, frame: "ToolDelta") -> None:
        """设置关联的系统框架"""
        self.linked_frame = frame
        _set_frame(frame)
        _set_frame_inj(frame)
        _init_frame(frame)

    def read_all_plugins(self) -> None:
        """读取所有插件

        Raises:
            SystemExit: 读取插件出现问题
        """
        if self.linked_frame is None or self.linked_frame.on_plugin_err is None:
            raise ValueError("无法读取插件，请确保系统已初始化")
        for fdir in os.listdir(TOOLDELTA_PLUGIN_DIR):
            if fdir not in (TOOLDELTA_CLASSIC_PLUGIN, TOOLDELTA_INJECTED_PLUGIN):
                auto_move_plugin_dir(fdir)
        try:
            classic_plugin.read_plugins(self)
            self.execute_def(self.linked_frame.on_plugin_err)
            asyncio.run(injected_plugin.load_plugin(self))
        except Exception as err:
            err_str = "\n".join(traceback.format_exc().split("\n")[1:])
            Print.print_err(f"加载插件出现问题：\n{err_str}")
            raise SystemExit from err

    def load_plugin_hot(self, plugin_name: str, plugin_type: str) -> None:
        """热加载插件

        Args:
            plugin_name (str): 插件名
            plugin_type (str): 插件类型
        """
        plugin = None
        if plugin_type == "classic":
            plugin = classic_plugin.load_plugin(self, plugin_name)
        elif plugin_type == "injected":
            asyncio.run(injected_plugin.load_plugin_file(plugin_name))
        # 检查是否有 on_def 成员再执行
        if plugin and hasattr(plugin, "on_def"):
            plugin.on_def()  # type: ignore
        Print.print_suc(f"成功热加载插件：{plugin_name}")

    def add_listen_packet_id(self, packetType: int) -> None:
        """添加数据包监听，仅在系统内部使用

        Args:
            packetType (int): 数据包 ID

        Raises:
            ValueError: 无法添加数据包监听，请确保已经加载了系统组件
        """
        if self.linked_frame is None:
            raise ValueError("无法添加数据包监听，请确保已经加载了系统组件")
        self.listen_packet_ids.add(packetType)
        self.linked_frame.link_game_ctrl.add_listen_pkt(packetType)

    def instant_plugin_api(self, api_cls: type[_PLUGIN_CLS_TYPE]) -> _PLUGIN_CLS_TYPE:
        """
        对外源导入 (import) 的 API 插件类进行类型实例化。
        可以使得你所使用的 IDE 对导入的插件 API 类进行识别和高亮其所含方法。

        Args:
            api_cls (type[_PLUGIN_CLS_TYPE]): 导入的 API 插件类

        Raises:
            ValueError: API 插件类未被注册

        Returns:
            _PLUGIN_CLS_TYPE: API 插件实例

        使用方法如下:
        ```python
            p_api = plugins.get_plugin_api("...")
            from outer_api import api_cls_xx
            p_api = plugins.instant_plugin_api(api_cls_xx)
        ```
        """
        for v in self.plugins_api.values():
            if isinstance(v, api_cls):
                return v
        raise ValueError(f"无法找到 API 插件类 {api_cls.__name__}, 有可能是还没有注册")

    def add_listen_packet_func(self, packetType: int, func: Callable) -> None:
        """添加数据包监听器，仅在系统内部使用

        Args:
            packetType (int): 数据包 ID
            func (Callable): 数据包监听器
        """
        if self._packet_funcs.get(str(packetType)):
            self._packet_funcs[str(packetType)].append(func)
        else:
            self._packet_funcs[str(packetType)] = [func]

    def add_broadcast_evt(self, evt: str, func: Callable) -> None:
        """添加广播事件监听器，仅在系统内部使用

        Args:
            evt (str): 事件名
            func (Callable): 事件监听器
        """
        if self._broadcast_listeners.get(evt):
            self._broadcast_listeners[evt].append(func)
        else:
            self._broadcast_listeners[evt] = [func]

    def _add_listen_update_player_attributes_func(self, func: Callable) -> None:
        """添加玩家属性更新监听器，仅在系统内部使用

        Args:
            func (Callable): 数据包监听器
        """
        self._update_player_attributes_funcs.append(func)

    def execute_def(
        self, onerr: Callable[[str, Exception, str], None] = NON_FUNC
    ) -> None:
        """执行插件的二次初始化方法

        Args:
            onerr (Callable[[str, Exception, str], None], optional): 插件出错时的处理方法。Defaults to NON_FUNC.

        Raises:
            SystemExit: 缺少前置
            SystemExit: 前置版本过低
        """
        try:
            for name, func in self.plugins_funcs["on_def"]:
                func()
        except PluginAPINotFoundError as err:
            name = err.name
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

    def execute_init(
        self, onerr: Callable[[str, Exception, str], None] = NON_FUNC
    ) -> None:
        """执行插件的连接游戏后初始化方法

        Args:
            onerr (Callable[[str, Exception, str], None], optional): 插件出错时的处理方法
        """
        for name, func in self.plugins_funcs["on_inject"]:
            try:
                func()
            except Exception as err:
                onerr(name, err, traceback.format_exc())
        asyncio.run(execute_init())
        Utils.createThread(asyncio.run, (execute_repeat(),))

    def execute_player_prejoin(
        self, player, onerr: Callable[[str, Exception, str], None] = NON_FUNC
    ) -> None:
        """执行玩家加入前的方法

        Args:
            player (_type_): 玩家
            onerr (Callable[[str, Exception, str], None], optional): 插件出错时的处理方法
        """
        for name, func in self.plugins_funcs["on_player_prejoin"]:
            try:
                func(player)
            except Exception as err:
                onerr(name, err, traceback.format_exc())
        asyncio.run(execute_player_prejoin(player))

    def execute_player_join(
        self, player: str, onerr: Callable[[str, Exception, str], None] = NON_FUNC
    ) -> None:
        """执行玩家加入的方法

        Args:
            player (str): 玩家
            onerr (Callable[[str, Exception, str], None], optional): q 插件出错时的处理方法
        """
        for name, func in self.plugins_funcs["on_player_join"]:
            try:
                func(player)
            except Exception as err:
                onerr(name, err, traceback.format_exc())
        asyncio.run(execute_player_join(player))

    def execute_player_message(
        self,
        player: str,
        msg: str,
        onerr: Callable[[str, Exception, str], None] = NON_FUNC,
    ) -> None:
        """执行玩家消息的方法

        Args:
            player (str): 玩家
            msg (str): 消息
            onerr (Callable[[str, Exception, str], None], optional): 插件出错时的处理方法
        """
        pat = f"[{player}] "
        if msg.startswith(pat):
            msg = msg.strip(pat)
        for name, func in self.plugins_funcs["on_player_message"]:
            try:
                func(player, msg)
            except Exception as err:
                onerr(name, err, traceback.format_exc())
        asyncio.run(execute_player_message(player, msg))

    def execute_player_leave(
        self, player: str, onerr: Callable[[str, Exception, str], None] = NON_FUNC
    ) -> None:
        """执行玩家离开的方法

        Args:
            player (str): 玩家
            onerr (Callable[[str, Exception, str], None], optional): 插件出错时的处理方法
        """
        for name, func in self.plugins_funcs["on_player_leave"]:
            try:
                func(player)
            except Exception as err:
                onerr(name, err, traceback.format_exc())
        asyncio.run(execute_player_left(player))

    def execute_player_death(
        self,
        player: str,
        killer: str | None,
        msg: str,
        onerr: Callable[[str, Exception, str], None] = NON_FUNC,
    ):
        """执行玩家死亡的方法

        Args:
            player (str): 玩家
            killer (str | None): 击杀者
            msg (str): 消息
            onerr (Callable[[str, Exception, str], None], optional): 插件出错时的处理方法
        """
        for name, func in self.plugins_funcs["on_player_death"]:
            try:
                func(player, killer, msg)
            except Exception as err:
                onerr(name, err, traceback.format_exc())
        asyncio.run(execute_death_message(player, killer, msg))

    def execute_command(
        self,
        name: str,
        msg: str,
        onerr: Callable[[str, Exception, str], None] = NON_FUNC,
    ) -> None:
        """执行命令 say 的方法

        Args:
            player (str): 玩家
            cmd (str): 命令
            onerr (Callable[[str, Exception, str], None], optional): 插件出错时的处理方法
        """
        for plugin_name, func in self.plugins_funcs["on_command"]:
            try:
                func(plugin_name, msg)
            except Exception as err:
                onerr(plugin_name, err, traceback.format_exc())
        asyncio.run(execute_command_say(name, msg))

    def execute_frame_exit(
        self, onerr: Callable[[str, Exception, str], None] = NON_FUNC
    ):
        """执行框架退出的方法

        Args:
            onerr (Callable[[str, Exception, str], None], optional): 插件出错时的处理方法
        """
        for name, func in self.plugins_funcs["on_frame_exit"]:
            try:
                func()
            except Exception as err:
                onerr(name, err, traceback.format_exc())
        asyncio.run(execute_frame_exit())

    def processPacketFunc(self, pktID: int, pkt: dict) -> bool:
        """处理数据包监听器

        Args:
            pktID (int): 数据包 ID
            pkt (dict): 数据包

        Returns:
            bool: 是否处理成功
        """
        d = self._packet_funcs.get(str(pktID))
        if d:
            for func in d:
                try:
                    res = func(pkt)
                    if res:
                        return True
                except Exception:
                    Print.print_err(f"插件方法 {func.__name__} 出错：")
                    Print.print_err(traceback.format_exc())
        return False


plugin_group = PluginGroup()
