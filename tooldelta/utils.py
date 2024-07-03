"""提供了一些实用方法的类"""

import copy
import ctypes
import json as rjson
import os
import threading
import time
import traceback
from io import TextIOWrapper
from typing import Any, Callable, Iterable, Optional

import ujson as json

from .color_print import Print
from .constants import TOOLDELTA_PLUGIN_DATA_DIR

event_pool = {"tmpjson_save": threading.Event()}
event_flags_pool = {"tmpjson_save": True}
threads_list: list["Utils.createThread"] = []


class Utils:
    """提供了一些实用方法的类"""

    class ThreadExit(SystemExit):
        """线程退出."""

    class ToolDeltaThread(threading.Thread):
        """简化 ToolDelta 子线程创建的 threading.Thread 的子类."""

        def __init__(
            self, func: Callable, args: Iterable[Any] = (), usage="", **kwargs
        ):
            """新建一个 ToolDelta 子线程

            Args:
                func (Callable): 线程方法
                args (tuple, optional): 方法的参数项
                usage (str, optional): 线程的用途说明
                kwargs (dict, optional): 方法的关键词参数项
            """
            super().__init__(target=func)
            self.func = func
            self.daemon = True
            self.all_args = [args, kwargs]
            self.usage = usage
            self.start()
            self.stopping = False
            self._thread_id = None

        def run(self) -> None:
            """线程运行方法"""
            threads_list.append(self)
            try:
                self.func(*self.all_args[0], **self.all_args[1])
            except SystemExit:
                pass
            except ValueError as e:
                if str(e) != "未连接到游戏":
                    raise
                Print.print_war(f"线程 {self.usage} 因游戏断开连接被迫中断")
            except Exception:
                Print.print_err(
                    f"线程 {self.usage or self.func.__name__} 出错:\n"
                    + traceback.format_exc()
                )
            finally:
                threads_list.remove(self)

        def get_id(self) -> int:
            """获取线程的 ID

            Raises:
                RuntimeError: 线程 ID 未知

            Returns:
                int: 线程 ID
            """
            if self._thread_id is None:
                for thread in threading.enumerate():
                    if thread is self:
                        self._thread_id = thread.ident
                        break
            if self._thread_id is None:
                raise RuntimeError("Could not determine the thread's ID")
            return self._thread_id

        def stop(self) -> None:
            """终止线程"""
            self.stopping = True
            self._thread_id = self.ident
            thread_id = self.get_id()
            res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
                thread_id, ctypes.py_object(SystemExit)
            )
            if res > 1:
                ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
                Print.print_err(f"§c终止线程 {self.name} 失败")

    createThread = ClassicThread = ToolDeltaThread

    class TMPJson:
        """提供了加载、卸载、读取和写入 JSON 文件到缓存区的方法的类."""

        @staticmethod
        def loadPathJson(path: str, needFileExists: bool = True) -> None:
            """
            将 json 文件从磁盘加载到缓存区，以便快速读写.
            在缓存文件已加载的情况下，再使用一次该方法不会有任何作用.

            Args:
                path (str): 作为文件的磁盘内路径的同时也会作为在缓存区的虚拟路径
                needFileExists (bool, optional): 默认为 True, 为 False 时，若文件路径不存在，就会自动创建一个文件，且默认值为 null

            Raises:
                err: 文件不存在时
            """
            if path in jsonPathTmp:
                return
            try:
                with open(path, "r", encoding="utf-8") as file:
                    js = Utils.SimpleJsonDataReader.SafeJsonLoad(file)
            except FileNotFoundError as err:
                if not needFileExists:
                    js = None
                else:
                    raise err from None
            jsonPathTmp[path] = [False, js]

        @staticmethod
        def unloadPathJson(path: str) -> bool:
            """
            将 json 文件从缓存区卸载 (保存内容到磁盘), 之后不能再在缓存区对这个文件进行读写.
            在缓存文件已卸载的情况下，再使用一次该方法不会有任何作用，但是可以通过其返回的值来知道存盘有没有成功.

            Args:
                path (str): 文件的虚拟路径

            Returns:
                bool: 存盘是否成功
            """
            if jsonPathTmp.get(path) is not None:
                isChanged, dat = jsonPathTmp[path]
                if isChanged:
                    with open(path, "w", encoding="utf-8") as file:
                        Utils.SimpleJsonDataReader.SafeJsonDump(dat, file)
                del jsonPathTmp[path]
                return True
            return False

        @staticmethod
        def read(path: str) -> Any:
            """对缓存区的该虚拟路径的文件进行读操作，返回一个深拷贝的 JSON 对象

            Args:
                path (str): 文件的虚拟路径

            Raises:
                Exception: json 路径未初始化，不能进行读取和写入操作

            Returns:
                list[Any] | dict[Any, Any] | Any: 该虚拟路径的 JSON
            """
            if path in jsonPathTmp:
                val = jsonPathTmp.get(path)
                if val is not None:
                    val = val[1]
                    if isinstance(val, (list, dict)):
                        val = copy.deepcopy(val)
                    return val
            raise ValueError("json 路径未初始化，不能进行读取和写入操作：" + path)

        @staticmethod
        def get(path: str) -> None:
            """
            直接获取缓存区的该虚拟路径的 JSON, 不使用 copy
            WARNING: 如果你不知道有什么后果，请老老实实使用`read(...)`而不是`get(...)`!

            Args:
                path (str): 文件的虚拟路径
            """
            if path in jsonPathTmp:
                val = jsonPathTmp.get(path)
                if val is not None:
                    val = val[1]
                    return val
            raise ValueError("json 路径未初始化，不能进行读取和写入操作：" + path)

        @staticmethod
        def write(path: str, obj: Any) -> None:
            """
            对缓存区的该虚拟路径的文件进行写操作，这将会覆盖之前的内容

            Args:
                path (str): 文件的虚拟路径
                obj (Any): 任何合法的 JSON 类型 例如 dict/list/str/bool/int/float
            """
            if path in jsonPathTmp:
                jsonPathTmp[path] = [True, obj]
            else:
                raise ValueError("json 路径未初始化，不能进行读取和写入操作：" + path)

        @staticmethod
        def read_as_tmp(
            path: str, needFileExists: bool = True, timeout: int = 60
        ) -> Any:
            """读取 json 文件并将其从磁盘加载到缓存区，以便一段时间内能快速读写.

            Args:
                path (str): 作为文件的磁盘内路径的同时也会作为在缓存区的虚拟路径
                needFileExists (bool, optional): 默认为 True, 为 False 时，若文件路径不存在，就会自动创建一个文件，且写入默认值 null
                timeout (int, optional): 多久没有再进行读取操作时卸载缓存

            Returns:
                Any: 该虚拟路径的 JSON
            """
            if path not in jsonUnloadPathTmp and path not in jsonPathTmp:
                jsonUnloadPathTmp[path] = timeout + int(time.time())
                Utils.TMPJson.loadPathJson(path, needFileExists)
            return Utils.TMPJson.read(path)

        @staticmethod
        def write_as_tmp(
            path: str, obj: Any, needFileExists: bool = True, timeout: int = 60
        ) -> None:
            """写入 json 文件并将其从磁盘加载到缓存区，以便一段时间内能快速读写.

            Args:
                path (str): 作为文件的磁盘内路径的同时也会作为在缓存区的虚拟路径
                obj (Any): 任何合法的 JSON 类型 例如 dict/list/str/bool/int/float
                needFileExists (bool, optional): 默认为 True, 为 False 时，若文件路径不存在，就会自动创建一个文件，且写入默认值 null
                timeout (int, optional): 多久没有再进行读取操作时卸载缓存
            """
            if path not in jsonUnloadPathTmp and path not in jsonPathTmp:
                jsonUnloadPathTmp[path] = timeout + int(time.time())
                Utils.TMPJson.loadPathJson(path, needFileExists)
            Utils.TMPJson.write(path, obj)

        @staticmethod
        def cancel_change(path: str) -> None:
            """取消缓存 json 所做的更改，非必要情况请勿调用，你不知道什么时候会自动保存所做更改"""
            jsonPathTmp[path][0] = False

        @staticmethod
        def get_tmps() -> dict:
            """不要调用!"""
            return jsonPathTmp.copy()

    class JsonIO:
        """提供了安全的 JSON 文件操作方法的类."""

        @staticmethod
        def SafeJsonDump(obj: Any, fp: TextIOWrapper | str, indent=4) -> None:
            """将一个 json 对象写入一个文件，会自动关闭文件读写接口.

            Args:
                obj (str | dict | list): JSON 对象
                fp (Any): open(...) 打开的文件读写口 或 文件路径
            """
            if isinstance(fp, str):
                with open(fp, "w", encoding="utf-8") as file:
                    file.write(json.dumps(obj, indent=indent, ensure_ascii=False))
            else:
                with fp:
                    fp.write(json.dumps(obj, indent=indent, ensure_ascii=False))

        @staticmethod
        def SafeJsonLoad(fp: TextIOWrapper | str) -> Any:
            """从一个文件读取 json 对象，会自动关闭文件读写接口.

            Args:
                fp (TextIOWrapper | str): open(...) 打开的文件读写口 或文件路径

            Returns:
                dict | list: JSON 对象
            """
            if isinstance(fp, str):
                with open(fp, "r", encoding="utf-8") as file:
                    return json.load(file)
            with fp as file:
                return json.load(file)

        class DataReadError(json.JSONDecodeError):
            """读取数据时发生错误"""

        @staticmethod
        def readFileFrom(
            plugin_name: str, file: str, default: dict | None = None
        ) -> Any:
            """从插件数据文件夹读取一个 json 文件，会自动创建文件夹和文件.

            Args:
                plugin_name (str): 插件名
                file (str): 文件名
                default (dict, optional): 默认值，若文件不存在则会写入这个默认值

            Raises:
                Utils.JsonIO.DataReadError: 读取数据时发生错误
                err: 读取文件路径时发生错误

            Returns:
                dict | list: JSON 对象
            """
            if file.endswith(".json"):
                file = file[:-5]
            filepath = os.path.join(
                TOOLDELTA_PLUGIN_DATA_DIR, plugin_name, f"{file}.json"
            )
            os.makedirs(
                os.path.join(TOOLDELTA_PLUGIN_DATA_DIR, plugin_name), exist_ok=True
            )
            try:
                if default is not None and not os.path.isfile(filepath):
                    with open(filepath, "w", encoding="utf-8") as f:
                        Utils.JsonIO.SafeJsonDump(default, f)
                    return default
                with open(filepath, "r", encoding="utf-8") as f:
                    res = Utils.JsonIO.SafeJsonLoad(f)
                return res
            except rjson.JSONDecodeError as err:
                # 判断是否有 msg.doc.pos 属性
                raise Utils.JsonIO.DataReadError(err.msg, err.doc, err.pos)
            except Exception as err:
                Print.print_err(f"读文件路径 {filepath} 发生错误")
                raise err

        @staticmethod
        def writeFileTo(plugin_name: str, file: str, obj: Any, indent=4) -> None:
            """将一个 json 对象写入插件数据文件夹，会自动创建文件夹和文件.

            Args:
                plugin_name (str): 插件名
                file (str): 文件名
                obj (str | dict[Any, Any] | list[Any]): JSON 对象
            """
            os.makedirs(f"{TOOLDELTA_PLUGIN_DATA_DIR}/{plugin_name}", exist_ok=True)
            with open(
                f"{TOOLDELTA_PLUGIN_DATA_DIR}/{plugin_name}/{file}.json",
                "w",
                encoding="utf-8",
            ) as f:
                Utils.JsonIO.SafeJsonDump(obj, f, indent=indent)

    SimpleJsonDataReader = JsonIO

    class ChatbarLock:
        r"""
        聊天栏锁, 用于防止玩家同时开启多个聊天栏对话\n
        调用了该锁的所有代码, 在另一个进程使用该锁的时候, 尝试调用其他锁会导致进程直接退出, 直到此锁退出为止\n
        示例(以类式插件为例):
        ```python
        class MyPlugin(Plugin):
            ...
            def on_player_message(self, player: str, msg: str):
                with ChatbarLock(player):
                    # 如果玩家处在另一个on_player_message进程 (锁环境) 中
                    # 则在上面就会直接引发 SystemExit
                    ...
        ```
        示例(以注入式插件为例):
        ```
        @player_message()
        async def onPlayerChat(info: player_message_info):
            with ChatbarLock(info.playername):
                ...
        ```
        """

        def __init__(self, player: str, oth_cb: Callable[[str], None] = lambda _: None):
            self.player = player
            self.oth_cb = oth_cb

        def __enter__(self):
            if self.player in chatbar_lock_list:
                self.oth_cb(self.player)
                Print.print_war(f"玩家 {self.player} 的线程锁正在锁定状态")
                raise SystemExit
            chatbar_lock_list.append(self.player)

        def __exit__(self, e, e2, e3):
            chatbar_lock_list.remove(self.player)

    @staticmethod
    def get_threads_list() -> list["Utils.createThread"]:
        """返回使用 createThread 创建的全线程列表。"""
        return threads_list

    @staticmethod
    def simple_fmt(kw: dict[str, Any], sub: str) -> str:
        """
        快速将字符串内按照给出的 dict 的键值对替换掉内容.

        参数:
            kw: Dict[str, Any], 键值对应替换的内容
            *args: str, 需要被替换的字符串

        示例:
            >>> my_color = "red"; my_item = "apple"
            >>> kw = {"[颜色]": my_color, "[物品]": my_item}
            >>> Utils.SimpleFmt(kw, "I like [颜色] [物品].")
            I like red apple.
        """
        for k, v in kw.items():
            if k in sub:
                sub = sub.replace(k, str(v))
        return sub

    SimpleFmt = simple_fmt

    @staticmethod
    def simple_assert(cond: Any, exc: Any) -> None:
        """相当于 assert cond, 但是可以自定义引发的异常的类型"""
        if not cond:
            raise exc

    simpleAssert = simple_assert

    @staticmethod
    def thread_func(func_or_name: Callable | str) -> Any:
        """
        在事件方法可能执行较久会造成堵塞时使用，方便快捷地创建一个新线程，例如:

        ```python
        @Utils.thread_func
        def on_inject(self):
            ...
        ```
        或者:
        ```python
        @Utils.thread_func("一个会卡一分钟的线程")
        def on_inject(self):
            ...
        ```
        """
        if isinstance(func_or_name, str):

            def _recv_func(func: Callable):
                def thread_fun(*args: tuple, **kwargs: Any) -> None:
                    Utils.createThread(func, usage=func_or_name, args=args, **kwargs)

                return thread_fun

            return _recv_func

        def thread_fun(*args: tuple, **kwargs: Any) -> None:
            Utils.createThread(
                func_or_name,
                usage="简易线程方法：" + func_or_name.__name__,
                args=args,
                **kwargs,
            )

        return thread_fun

    @staticmethod
    def try_int(arg: Any) -> Optional[int]:
        """尝试将提供的参数化为 int 类型并返回，否则返回 None"""
        try:
            return int(arg)
        except Exception:
            return None

    @staticmethod
    def fuzzy_match(lst: list[str], sub: str) -> list[str]:
        """
        模糊匹配列表内的字符串，可以用在诸如模糊匹配玩家名的用途

        参数:
            lst: list, 字符串列表
            sub: str, 需要匹配的字符串
        返回:
            list, 匹配结果
        """
        res = []
        for i in lst:
            if sub in i:
                res.append(i)
        return res


def safe_close() -> None:
    """安全关闭"""
    event_pool["tmpjson_save"].set()
    event_flags_pool["tmpjson_save"] = False


@Utils.thread_func("JSON 缓存文件定时保存")
def tmpjson_save_thread():
    evt = event_pool["tmpjson_save"]
    secs = 0
    while 1:
        evt.wait(2)
        secs += 2
        if secs >= 60:
            secs = 0
            for k, (isChanged, dat) in jsonPathTmp.copy().items():
                if isChanged:
                    Utils.SimpleJsonDataReader.SafeJsonDump(dat, k)
                    jsonPathTmp[k][0] = False
        for k, v in jsonUnloadPathTmp.copy().items():
            if time.time() - v > 0:
                Utils.TMPJson.unloadPathJson(k)
                del jsonUnloadPathTmp[k]
        if not event_flags_pool["tmpjson_save"]:
            return


jsonPathTmp = {}
chatbar_lock_list = []
jsonUnloadPathTmp = {}
