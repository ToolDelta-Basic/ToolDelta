from .color_print import Print
import ujson
import os
import threading
import traceback
import copy
import ctypes
from typing import Any, Dict, List, Tuple, Optional

event_pool = {"tmpjson_save": threading.Event()}
event_flags_pool = {"tmpjson_save": True}


class Builtins:
    class ThreadExit(SystemExit):
        "线程退出."

    class ClassicThread(threading.Thread):
        def __init__(self, func, args: tuple = (), usage="", **kwargs):
            """
            方便地新建一个ToolDelta子线程

            参数:
                func: 线程方法
                args: 方法的参数项 tuple
                usage: 线程的用途说明
                ..kwargs: 方法的关键字参数项
            """
            super().__init__(target=func)
            self.func = func
            self.daemon = True
            self.all_args = [args, kwargs]
            self.usage = usage
            self.start()

        def run(self):
            try:
                self.func(*self.all_args[0], **self.all_args[1])
            except Builtins.ThreadExit:
                pass
            except:
                Print.print_err(f"线程 {self.usage} 出错:\n" + traceback.format_exc())

    createThread = ClassicThread

    class TMPJson:
        @staticmethod
        def loadPathJson(path: str, needFileExists: bool = True):
            """
            将json文件从磁盘加载到缓存区, 以便快速读写.
            在缓存文件已加载的情况下, 再使用一次该方法不会有任何作用.

            参数:
                path: 作为文件的磁盘内路径的同时也会作为在缓存区的虚拟路径
                needFileExists: 默认为 True, 为 False 时, 若文件路径不存在, 就会自动创建一个文件.
            """
            if path in jsonPathTmp:
                return
            try:
                js = Builtins.SimpleJsonDataReader.SafeJsonLoad(path)
            except FileNotFoundError as err:
                if not needFileExists:
                    js = None
                else:
                    raise err from None
            jsonPathTmp[path] = [False, js]

        @staticmethod
        def unloadPathJson(path: str):
            """
            将json文件从缓存区卸载(保存内容到磁盘), 之后不能再在缓存区对这个文件进行读写.
            在缓存文件已卸载的情况下, 再使用一次该方法不会有任何作用, 但是可以通过其返回的值来知道存盘有没有成功.

            参数:
                path: 文件的虚拟路径
            """
            if jsonPathTmp.get(path) is not None:
                isChanged, dat = jsonPathTmp[path]
                if isChanged:
                    Builtins.SimpleJsonDataReader.SafeJsonDump(dat, path)
                del jsonPathTmp[path]
                return True
            return False

        @staticmethod
        def read(path: str):
            """
            对缓存区的该虚拟路径的文件进行读操作

            参数:
                path: 文件的虚拟路径
            """
            if path in jsonPathTmp:
                val = jsonPathTmp.get(path)[1]
                if isinstance(val, (list, dict)):
                    val = copy.deepcopy(val)
                return val
            raise Exception("json路径未初始化, 不能进行读取和写入操作: " + path)

        @staticmethod
        def write(path: str, obj: Any):
            """
            对缓存区的该虚拟路径的文件进行写操作, 这将会覆盖之前的内容

            参数:
                path: 文件的虚拟路径
                obj: 任何合法的JSON类型 例如 dict/list/str/bool/int/float
            """
            if path in jsonPathTmp:
                jsonPathTmp[path] = [True, obj]
            else:
                raise Exception("json路径未初始化, 不能进行读取和写入操作: " + path)

        @staticmethod
        def cancel_change(path):
            "取消缓存json所做的更改, 非必要情况请勿调用, 你不知道什么时候会自动保存所做更改"
            jsonPathTmp[path][0] = False

        @staticmethod
        def get_tmps():
            "不要调用!"
            return jsonPathTmp.copy()

    class SimpleJsonDataReader:
        @staticmethod
        def SafeJsonDump(obj: str | dict | list, fp):
            """
            导出一个json文件, 会自动关闭文件读写接口.

            参数:
                obj: json对象.
                fp: 由open(...)打开的文件读写口 或 文件路径.
            """
            if isinstance(fp, str):
                with open(fp, "w", encoding="utf-8") as file:
                    file.write(ujson.dumps(obj, indent=4, ensure_ascii=False))
            else:
                with fp:
                    fp.write(ujson.dumps(obj, indent=4, ensure_ascii=False))

        @staticmethod
        def SafeJsonLoad(fp):
            """
            读取一个json文件, 会自动关闭文件读写接口.

            参数:
                fp: open(...)打开的文件读写口 或 文件路径.
            """
            if isinstance(fp, str):
                with open(fp, "r", encoding="utf-8") as file:
                    return ujson.loads(file.read())
            with fp as file:
                return ujson.loads(file.read())

        class DataReadError(ujson.JSONDecodeError):
            ...

        @staticmethod
        def readFileFrom(plugin_name: str, file: str, default: dict = None):
            """
            使用插件便捷地读取一个json文件,
            这个文件应在 插件数据文件/<plugin_name>/<file>文件夹内, 文件夹不存在时也会自动创建

            参数:
                plugin_name: 插件名
                file: 文件名
                default: 不为None时: 当文件不存在则创建一个空文件, 使用default给出的json字典写入文件.
            """
            if file.endswith(".json"):
                file = file[:-5]
            filepath = os.path.join("插件数据文件", plugin_name, f"{file}.json")
            os.makedirs(os.path.join("插件数据文件", plugin_name), exist_ok=True)
            try:
                if default is not None and not os.path.isfile(filepath):
                    with open(filepath, "w", encoding="utf-8") as f:
                        Builtins.SimpleJsonDataReader.SafeJsonDump(default, f)
                    return default
                with open(filepath, "r", encoding="utf-8") as f:
                    res = Builtins.SimpleJsonDataReader.SafeJsonLoad(f)
                return res
            except ujson.JSONDecodeError as err:
                raise Builtins.SimpleJsonDataReader.DataReadError(
                    err.msg, err.doc, err.pos
                )
            except Exception as err:
                Print.print_err(f"读文件路径 {filepath} 发生错误")
                raise err

        @staticmethod
        def writeFileTo(plugin_name: str, file: str, obj):
            """
            使用插件简单地写入一个json文件, 会覆盖原有内容
            这个文件应在data/<plugin_name>/<file>文件夹内

            参数:
                plugin_name: 插件名
                file: 文件名
                obj: 任何合法的JSON类型 例如 dict/list/str/bool/int/float
            """
            os.makedirs(f"插件数据文件/{plugin_name}", exist_ok=True)
            with open(f"插件数据文件/{plugin_name}/{file}.json", "w", encoding="utf-8") as f:
                Builtins.SimpleJsonDataReader.SafeJsonDump(obj, f)

    @staticmethod
    def SimpleFmt(kw: Dict[str, Any], __sub: str) -> str:
        """
        快速将字符串内按照给出的dict的键值对替换掉内容.

        参数:
            kw: Dict[str, Any], 键值对应替换的内容
            __sub: str, 需要被替换的字符串

        示例:
            >>> my_color = "red"; my_item = "apple"
            >>> kw = {"[颜色]": my_color, "[物品]": my_item}
            >>> Builtins.SimpleFmt(kw, "I like [颜色] [物品].")
            I like red apple.
        """
        for k, v in kw.items():
            if k in __sub:
                __sub = __sub.replace(k, str(v))
        return __sub

    @staticmethod
    def simpleAssert(cond: Any, exc: Any) -> None:
        """相当于 assert cond, 但是可以自定义引发的异常的类型"""
        if not cond:
            raise exc

    @staticmethod
    def new_thread(func: Any) -> Any:
        """
        在事件方法可能执行较久会造成堵塞时使用, 方便快捷地创建一个新线程, 例如:

        @Builtins.run_as_new_thread
        def on_inject(self):
            ...
        """

        def thread_fun(*args: Tuple, **kwargs: Any) -> None:
            Builtins.createThread(func, args=args, **kwargs)

        return thread_fun

    run_as_new_thread = new_thread

    @staticmethod
    def try_int(arg: Any) -> Optional[int]:
        """
        尝试将提供的参数化为int类型并返回, 否则返回None
        """
        try:
            return int(arg)
        except:
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
            raise Exception("Already in a dialogue!")

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
        Builtins.createThread(
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
        def __init__(self, kw: Dict[str, Any]):
            self.kw = kw

        def replaceTo(self, __sub: str):
            for k, v in self.kw.items():
                if k in __sub:
                    __sub = __sub.replace(k, str(v))
            return __sub


def safe_close():
    event_pool["tmpjson_save"].set()
    event_flags_pool["tmpjson_save"] = False


def _tmpjson_save_thread():
    evt = event_pool["tmpjson_save"]
    while 1:
        evt.wait(60)
        for k, (isChanged, dat) in jsonPathTmp.copy().items():
            if isChanged:
                Builtins.SimpleJsonDataReader.SafeJsonDump(dat, k)
                jsonPathTmp[k][0] = False
        if not event_flags_pool["tmpjson_save"]:
            return


def tmpjson_save_thread():
    Builtins.createThread(_tmpjson_save_thread)


def _dialogue_thread_run(player, func, exc_cb, args, kwargs):
    if not Builtins.player_in_dialogue(player):
        Builtins.add_in_dialogue_player(player)
    else:
        if exc_cb is not None:
            exc_cb(player)
        return
    try:
        func(*args, **kwargs)
    except:
        Print.print_err(f"玩家{player}的会话线程 出现问题:")
        Print.print_err(traceback.format_exc())
    Builtins.remove_in_dialogue_player(player)


jsonPathTmp = {}
in_dialogue_list = []
