from .color_print import Print
import ujson, os, time, threading, traceback, copy, ctypes

event_pool = {
    "tmpjson_save": threading.Event()
}
event_flags_pool = {
    "tmpjson_save": True
}

class Builtins:
    class ThreadExit(SystemExit):
        "线程退出."

    class ClassicThread(threading.Thread):
        def __init__(self, func, args: tuple = (), usage="", **kwargs):
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
                if "exc_cb" in self.all_args[1].keys():
                    self.all_args[1]["exc_cb"]

        def get_id(self):
            if hasattr(self, "_thread_id"):
                return self._thread_id
            for id, thread in threading._active.items():
                if thread is self:
                    return id

        def stop(self):
            res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
                self.get_id(), ctypes.py_object(Builtins.ThreadExit)
            )
            return res

    createThread = ClassicThread

    class TMPJson:
        @staticmethod
        def loadPathJson(path, needFileExists: bool = True):
            """
            将json文件加载到缓存区, 以便快速读写.
            needFileExists = False 时, 若文件路径不存在, 就会自动创建一个文件.
            在缓存文件已加载的情况下, 再使用一次该方法不会有任何作用.
            path: 作为文件的真实路径的同时也会作为在缓存区的虚拟路径
            """
            if path in jsonPathTmp.keys():
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
        def unloadPathJson(path):
            """
            将json文件从缓存区卸载(保存内容到磁盘), 之后不能再在缓存区对这个文件进行读写.
            在缓存文件已卸载的情况下, 再使用一次该方法不会有任何作用, 但是可以通过其返回的值来知道存盘有没有成功.
            """
            if jsonPathTmp.get(path) is not None:
                isChanged, dat = jsonPathTmp[path]
                if isChanged:
                    Builtins.SimpleJsonDataReader.SafeJsonDump(dat, path)
                del jsonPathTmp[path]
                return True
            else:
                return False

        @staticmethod
        def read(path):
            "对缓存区的该虚拟路径的文件进行读操作"
            if path in jsonPathTmp.keys():
                val = jsonPathTmp.get(path)[1]
                if isinstance(val, (list, dict)):
                    val = copy.deepcopy(val)
                return val
            else:
                raise Exception("json路径未初始化, 不能进行读取和写入操作: " + path)

        @staticmethod
        def write(path, obj):
            "对缓存区的该虚拟路径的文件进行写操作"
            if path in jsonPathTmp.keys():
                jsonPathTmp[path] = [True, obj]
            else:
                raise Exception(f"json路径未初始化, 不能进行读取和写入操作: " + path)

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
            导出一个json文件, 弥补orjson库没有dump方法的不足.
                obj: json对象.
                fp: open(...)打开的文件读写口 或 文件路径.
            """
            if isinstance(fp, str):
                fp = open(fp, "w", encoding="utf-8")
            fp.write(ujson.dumps(obj, indent=4, ensure_ascii=False))
            fp.close()

        @staticmethod
        def SafeJsonLoad(fp):
            """
            读取一个json文件, 弥补orjson库没有load方法的不足.
                fp: open(...)打开的文件读写口 或 文件路径.
            """
            if isinstance(fp, str):
                fp = open(fp, "r", encoding="utf-8")
            d = ujson.loads(fp.read())
            fp.close()
            return d

        class DataReadError(ujson.JSONDecodeError):
            ...

        @staticmethod
        def readFileFrom(plugin_name: str, file: str, default: dict = None):
            """
            使用插件便捷地读取一个json文件, 当文件不存在则创建一个空文件, 使用default给出的json默认值写入文件.
            这个文件应在data/<plugin_name>/<file>文件夹内
            """
            filepath = os.path.join("data", plugin_name, f"{file}.json")
            os.makedirs(os.path.join("data", plugin_name), exist_ok=True)
            try:
                if default is not None and not os.path.isfile(filepath):
                    with open(filepath, "w", encoding="utf-8") as f:
                        Builtins.SimpleJsonDataReader.SafeJsonDump(
                            default, f
                        )
                    return default
                else:
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
            使用插件简单地写入一个json文件
            这个文件应在data/<plugin_name>/<file>文件夹内
            """
            os.makedirs(f"data/{plugin_name}", exist_ok=True)
            with open(f"data/{plugin_name}/{file}.json", "w", encoding="utf-8") as f:
                Builtins.SimpleJsonDataReader.SafeJsonDump(obj, f)

    @staticmethod
    def SimpleFmt(kw: dict[str, any], __sub: str):
        """
        快速将字符串内的内容用给出的字典替换掉.
        >>> my_color = "red"; my_item = "apple"
        >>> kw = {"[颜色]": my_color, "[物品]": my_item}
        >>> SimpleFmt(kw, "I like [颜色] [物品].")
        I like red apple.
        """
        for k, v in kw.items():
            if k in __sub:
                __sub = __sub.replace(k, str(v))
        return __sub

    @staticmethod
    def simpleAssert(cond: any, exc):
        """
        相当于 assert cond, 但是可以自定义引发的异常的类型
        """
        if not cond:
            raise exc
        
    @staticmethod
    def run_as_new_thread(func):
        """
        在事件方法可能执行较久会造成堵塞时使用, 方便快捷地创建一个新线程, 例如:
        @Builtins.run_as_new_thread
        def on_inject(self):
            ...
        """
        def thread_fun(*args, **kwargs):
            Builtins.createThread(func, args = args, **kwargs)
        return thread_fun

    @staticmethod
    def try_int(arg):
        try:
            return int(arg)
        except:
            return None

    @staticmethod
    def add_in_dialogue_player(player: str):
        "使玩家进入聊天栏对话模式"
        if player not in in_dialogue_list:
            in_dialogue_list.append(player)
        else:
            raise Exception("Already in a dialogue!")

    @staticmethod
    def remove_in_dialogue_player(player: str):
        "使玩家离开聊天栏对话模式"
        if player not in in_dialogue_list:
            return
        else:
            in_dialogue_list.remove(player)

    @staticmethod
    def player_in_dialogue(player: str):
        "玩家是否处在一个聊天栏对话中."
        return player in in_dialogue_list

    @staticmethod
    def create_dialogue_threading(player, func, exc_cb=None, args=(), kwargs={}):
        "创建一个玩家与聊天栏交互的线程, 若玩家已处于一个对话中, 则向方法exc_cb传参: player(玩家名)"
        threading.Thread(
            target=_dialogue_thread_run, args=(player, func, exc_cb, args, kwargs)
        ).start()

    @staticmethod
    def fuzzy_match(lst: list, sub: str):
        "模糊匹配列表内的字符串"
        res = []
        for i in lst:
            if sub in i:
                res.append(i)
        return res

    class ArgsReplacement:
        def __init__(this, kw: dict[str, any]):
            this.kw = kw

        def replaceTo(this, __sub: str):
            for k, v in this.kw.items():
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
