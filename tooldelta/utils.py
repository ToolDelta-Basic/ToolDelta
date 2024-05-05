"""
提供了一些实用方法的类

Classes:
- Builtins: 一个提供了线程、JSON操作和文件操作的实用方法的类。

Methods:
- ThreadExit: 用于线程终止的SystemExit的子类。
- ClassicThread: 简化ToolDelta子线程创建的threading.Thread的子类。
- TMPJson: 提供了加载、卸载、读取和写入JSON文件到缓存区的方法的类。
- SimpleJsonDataReader: 提供了安全的JSON文件操作方法的类。
- get_threads_list: 返回使用createThread创建的所有线程的列表。
- SimpleFmt: 使用字典中的值替换字符串中的占位符的静态方法。
"""

from io import TextIOWrapper
import os
import time
import copy
from typing import Any, Callable, Dict, List, Tuple, Optional
import ctypes
import threading
import traceback
import json as rjson
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

    class ClassicThread(threading.Thread):
        """简化ToolDelta子线程创建的threading.Thread的子类."""

        def __init__(self, func: Callable, args: tuple = (), usage="", **kwargs):
            """新建一个ToolDelta子线程

            Args:
                func (Callable): 线程方法
                args (tuple, optional):方法的参数项
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
            except (Utils.ThreadExit, SystemExit):
                pass
            except Exception:
                Print.print_err(
                    f"线程 {self.usage or self.func.__name__} 出错:\n" + traceback.format_exc())
            finally:
                threads_list.remove(self)

        def get_id(self) -> int:
            """获取线程的ID

            Raises:
                RuntimeError: 线程ID未知

            Returns:
                int: 线程ID
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
                thread_id, ctypes.py_object(SystemExit))
            if res > 1:
                ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
                Print.print_err("§c终止线程失败")

    createThread = ClassicThread

    class TMPJson:
        """提供了加载、卸载、读取和写入JSON文件到缓存区的方法的类."""
        @staticmethod
        def loadPathJson(path: str, needFileExists: bool = True) -> None:
            """
            将json文件从磁盘加载到缓存区, 以便快速读写.
            在缓存文件已加载的情况下, 再使用一次该方法不会有任何作用.

            Args:
                path (str): 作为文件的磁盘内路径的同时也会作为在缓存区的虚拟路径
                needFileExists (bool, optional): 默认为 True, 为 False 时, 若文件路径不存在, 就会自动创建一个文件, 且默认值为null

            Raises:
                err: 文件不存在时
            """
            if path in jsonPathTmp:
                return
            try:
                with open(path, 'r', encoding='utf-8') as file:
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
            将json文件从缓存区卸载(保存内容到磁盘), 之后不能再在缓存区对这个文件进行读写.
            在缓存文件已卸载的情况下, 再使用一次该方法不会有任何作用, 但是可以通过其返回的值来知道存盘有没有成功.

            Args:
                path (str): 文件的虚拟路径

            Returns:
                bool: 存盘是否成功
            """
            if jsonPathTmp.get(path) is not None:
                isChanged, dat = jsonPathTmp[path]
                if isChanged:
                    with open(path, 'w', encoding='utf-8') as file:
                        Utils.SimpleJsonDataReader.SafeJsonDump(dat, file)
                del jsonPathTmp[path]
                return True
            return False

        @staticmethod
        def read(path: str) -> Any:
            """对缓存区的该虚拟路径的文件进行读操作, 返回一个深拷贝的JSON对象

            Args:
                path (str): 文件的虚拟路径

            Raises:
                Exception: json路径未初始化, 不能进行读取和写入操作

            Returns:
                list[Any] | dict[Any, Any] | Any: 该虚拟路径的JSON
            """
            if path in jsonPathTmp:
                val = jsonPathTmp.get(path)
                if val is not None:
                    val = val[1]
                    if isinstance(val, (list, dict)):
                        val = copy.deepcopy(val)
                    return val
            raise ValueError("json路径未初始化, 不能进行读取和写入操作: " + path)

        @staticmethod
        def get(path: str) -> None:
            """
            直接获取缓存区的该虚拟路径的JSON, 不使用copy
            WARNING: 如果你不知道有什么后果, 请老老实实使用`read(...)`而不是`get(...)`!

            Args:
                path (str): 文件的虚拟路径
            """
            if path in jsonPathTmp:
                val = jsonPathTmp.get(path)
                if val is not None:
                    val = val[1]
                    return val
            raise ValueError("json路径未初始化, 不能进行读取和写入操作: " + path)

        @staticmethod
        def write(path: str, obj: Any) -> None:
            """
            对缓存区的该虚拟路径的文件进行写操作, 这将会覆盖之前的内容

            Args:
                path (str): 文件的虚拟路径
                obj (Any): 任何合法的JSON类型 例如 dict/list/str/bool/int/float
            """
            if path in jsonPathTmp:
                jsonPathTmp[path] = [True, obj]
            else:
                raise ValueError("json路径未初始化, 不能进行读取和写入操作: " + path)

        @staticmethod
        def read_as_tmp(path: str, needFileExists: bool = True, timeout: int = 60) -> Any:
            """读取json文件并将其从磁盘加载到缓存区, 以便一段时间内能快速读写.

            Args:
                path (str): 作为文件的磁盘内路径的同时也会作为在缓存区的虚拟路径
                needFileExists (bool, optional): 默认为 True, 为 False 时, 若文件路径不存在, 就会自动创建一个文件, 且写入默认值null
                timeout (int, optional): 多久没有再进行读取操作时卸载缓存

            Returns:
                Any: 该虚拟路径的JSON
            """
            if path not in jsonUnloadPathTmp and not path in jsonPathTmp:
                jsonUnloadPathTmp[path] = timeout + int(time.time())
                Utils.TMPJson.loadPathJson(path, needFileExists)
            return Utils.TMPJson.read(path)

        @staticmethod
        def write_as_tmp(path: str, obj: Any, needFileExists: bool = True, timeout: int = 60) -> None:
            """写入json文件并将其从磁盘加载到缓存区, 以便一段时间内能快速读写.

            Args:
                path (str): 作为文件的磁盘内路径的同时也会作为在缓存区的虚拟路径
                obj (Any): 任何合法的JSON类型 例如 dict/list/str/bool/int/float
                needFileExists (bool, optional): 默认为 True, 为 False 时, 若文件路径不存在, 就会自动创建一个文件, 且写入默认值null
                timeout (int, optional): 多久没有再进行读取操作时卸载缓存
            """
            if path not in jsonUnloadPathTmp and not path in jsonPathTmp:
                jsonUnloadPathTmp[path] = timeout + int(time.time())
                Utils.TMPJson.loadPathJson(path, needFileExists)
            Utils.TMPJson.write(path, obj)

        @staticmethod
        def cancel_change(path: str) -> None:
            """取消缓存json所做的更改, 非必要情况请勿调用, 你不知道什么时候会自动保存所做更改"""
            jsonPathTmp[path][0] = False

        @staticmethod
        def get_tmps() -> Dict:
            """不要调用!"""
            return jsonPathTmp.copy()

    class SimpleJsonDataReader:
        """提供了安全的JSON文件操作方法的类."""
        @staticmethod
        def SafeJsonDump(obj: str | dict | list, fp: TextIOWrapper) -> None:
            """将一个json对象写入一个文件, 会自动关闭文件读写接口.

            Args:
                obj (str | dict | list): JSON对象
                fp (_type_): open(...)打开的文件读写口 或 文件路径
            """
            if isinstance(fp, str):
                with open(fp, "w", encoding="utf-8") as file:
                    file.write(json.dumps(obj, indent=4, ensure_ascii=False))
            else:
                with fp:
                    fp.write(json.dumps(obj, indent=4, ensure_ascii=False))

        @staticmethod
        def SafeJsonLoad(fp: TextIOWrapper) -> dict | list:
            """从一个文件读取json对象, 会自动关闭文件读写接口.

            Args:
                fp (TextIOWrapper): open(...)打开的文件读写口

            Returns:
                dict | list: JSON对象
            """
            if isinstance(fp, str):
                with open(fp, "r", encoding="utf-8") as file:
                    return json.loads(file.read())
            with fp as file:
                return json.loads(file.read())

        class DataReadError(json.JSONDecodeError):
            """读取数据时发生错误"""

        @staticmethod
        def readFileFrom(plugin_name: str, file: str, default: dict | None = None) -> dict | list:
            """从插件数据文件夹读取一个json文件, 会自动创建文件夹和文件.

            Args:
                plugin_name (str): 插件名
                file (str): 文件名
                default (dict, optional): 默认值, 若文件不存在则会写入这个默认值

            Raises:
                Utils.SimpleJsonDataReader.DataReadError: 读取数据时发生错误
                err: 读取文件路径时发生错误

            Returns:
                dict | list: JSON对象
            """
            if file.endswith(".json"):
                file = file[:-5]
            filepath = os.path.join(TOOLDELTA_PLUGIN_DATA_DIR, plugin_name, f"{file}.json")
            os.makedirs(os.path.join(TOOLDELTA_PLUGIN_DATA_DIR, plugin_name), exist_ok=True)
            try:
                if default is not None and not os.path.isfile(filepath):
                    with open(filepath, "w", encoding="utf-8") as f:
                        Utils.SimpleJsonDataReader.SafeJsonDump(default, f)
                    return default
                with open(filepath, "r", encoding="utf-8") as f:
                    res = Utils.SimpleJsonDataReader.SafeJsonLoad(f)
                return res
            except rjson.JSONDecodeError as err:
                # 判断是否有msg.doc.pos属性
                raise Utils.SimpleJsonDataReader.DataReadError(
                    err.msg, err.doc, err.pos
                )
            except Exception as err:
                Print.print_err(f"读文件路径 {filepath} 发生错误")
                raise err

        @staticmethod
        def writeFileTo(plugin_name: str, file: str, obj: str | dict[Any, Any] | list[Any]) -> None:
            """将一个json对象写入插件数据文件夹, 会自动创建文件夹和文件.

            Args:
                plugin_name (str): 插件名
                file (str): 文件名
                obj (str | dict[Any, Any] | list[Any]): JSON对象
            """
            os.makedirs(f"{TOOLDELTA_PLUGIN_DATA_DIR}/{plugin_name}", exist_ok=True)
            with open(f"{TOOLDELTA_PLUGIN_DATA_DIR}/{plugin_name}/{file}.json", "w", encoding="utf-8") as f:
                Utils.SimpleJsonDataReader.SafeJsonDump(obj, f)

    @staticmethod
    def get_threads_list() -> list["Utils.createThread"]:
        "返回使用 createThread 创建的全线程列表."
        return threads_list

    @staticmethod
    def SimpleFmt(kw: Dict[str, Any], *args: str) -> str:
        """
        快速将字符串内按照给出的dict的键值对替换掉内容.

        参数:
            kw: Dict[str, Any], 键值对应替换的内容
            *args: str, 需要被替换的字符串

        示例:
            >>> my_color = "red"; my_item = "apple"
            >>> kw = {"[颜色]": my_color, "[物品]": my_item}
            >>> Utils.SimpleFmt(kw, "I like [颜色] [物品].")
            I like red apple.
        """
        __sub = args[0]
        for k, v in kw.items():
            if k in __sub:
                __sub = __sub.replace(k, str(v))
        return __sub

    @staticmethod
    def simpleAssert(cond: Any, exc: Any) -> None:
        """
        相当于 assert cond, 但是可以自定义引发的异常的类型
        """
        if not cond:
            raise exc

    @staticmethod
    def thread_func(func_or_name: Callable | str) -> Any:
        """
        在事件方法可能执行较久会造成堵塞时使用, 方便快捷地创建一个新线程, 例如:

        @Utils.thread_func
        def on_inject(self):
            ...
        或者:
        @Utils.thread_func("一个会卡一分钟的线程")
        def on_inject(self):
            ...
        """
        if isinstance(func_or_name, str):
            def _recv_func(func: Callable):
                def thread_fun(*args: Tuple, **kwargs: Any) -> None:
                    Utils.createThread(
                        func,
                        usage=func_or_name,
                        args=args,
                        **kwargs
                )
                return thread_fun
            return _recv_func
        else:
            def thread_fun(*args: Tuple, **kwargs: Any) -> None:
                Utils.createThread(
                    func_or_name,
                    usage="简易线程方法:" + func_or_name.__name__,
                    args=args,
                    **kwargs
                )
        return thread_fun

    run_as_new_thread = thread_func
    new_thread = thread_func

    @staticmethod
    def try_int(arg: Any) -> Optional[int]:
        """尝试将提供的参数化为int类型并返回, 否则返回None"""
        try:
            return int(arg)
        except Exception:
            return None

    @staticmethod
    def add_in_dialogue_player(player: str) -> None:
        """
        使玩家进入聊天栏对话模式, 可防止其在对话时继续触发另一个会话线程

        参数:
            player: str, 玩家名
        """
        if player not in in_dialogue_list:
            in_dialogue_list.append(player)
        else:
            raise ValueError("Already in a dialogue!")

    @staticmethod
    def remove_in_dialogue_player(player: str) -> None:
        """
        使玩家离开聊天栏对话模式

        参数:
            player: str, 玩家名
        """
        if player not in in_dialogue_list:
            return
        in_dialogue_list.remove(player)

    @staticmethod
    def player_in_dialogue(player: str) -> bool:
        """
        检测玩家是否处在聊天栏对话模式中.

        参数:
            player: str, 玩家名
        返回:
            bool, 检测结果
        """
        return player in in_dialogue_list

    @staticmethod
    def create_dialogue_threading(
        player: str,
        func: Any,
        exc_cb: Optional[Any] = None,
        args: Tuple = (),
        kwargs: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        创建一个玩家与聊天栏交互的线程,
        线程启动时玩家会自动进入聊天栏对话模式
        线程结束后该玩家会自动退出聊天栏对话模式
        可以用来防止玩家多开聊天栏对话或菜单线程

        参数:
            player: str, 玩家名
            func: function, 线程方法
            exc_cb: function, 若玩家已处于一个对话中, 则向方法exc_cb传参并调用它: player(玩家名)
            args: tuple, 线程方法的参数组
            kwargs: dict, 线程方法的关键词参数组
        """
        if kwargs is None:
            kwargs = {}
        Utils.createThread(
            _dialogue_thread_run, args=(player, func, exc_cb, args, kwargs)
        )

    @staticmethod
    def fuzzy_match(lst: List[str], sub: str) -> List[str]:
        """
        模糊匹配列表内的字符串, 可以用在诸如模糊匹配玩家名的用途

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

    class ArgsReplacement:
        """用于替换字符串中的占位符的类"""

        def __init__(self, kw: Dict[str, Any]):
            self.kw = kw

        def replaceTo(self, __sub: str) -> str:
            """

            Args:
                __sub (str): 需要替换的字符串

            Returns:
                str: 替换后的字符串
            """
            for k, v in self.kw.items():
                if k in __sub:
                    __sub = __sub.replace(k, str(v))
            return __sub


def safe_close() -> None:
    """安全关闭"""
    event_pool["tmpjson_save"].set()
    event_flags_pool["tmpjson_save"] = False


def _tmpjson_save_thread():
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


def tmpjson_save_thread() -> None:
    """JSON缓存文件定时保存"""
    Utils.createThread(_tmpjson_save_thread, usage="JSON缓存文件定时保存")


def _dialogue_thread_run(player, func, exc_cb, args, kwargs):
    "启动专用的玩家会话线程, 可免除当玩家在对话线程时又试图再创建一个对话线程的问题"
    if not Utils.player_in_dialogue(player):
        Utils.add_in_dialogue_player(player)
    else:
        if exc_cb is not None:
            exc_cb(player)
        return
    try:
        func(*args, **kwargs)
    except Exception:
        Print.print_err(f"玩家{player}的会话线程 出现问题:")
        Print.print_err(traceback.format_exc())
    Utils.remove_in_dialogue_player(player)


jsonPathTmp = {}
in_dialogue_list = []
jsonUnloadPathTmp = {}
