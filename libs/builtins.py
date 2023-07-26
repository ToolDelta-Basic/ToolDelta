from libs.color_print import Print
import orjson, os, time, threading
def on_plugin_err_common(pluginName: str, _, trace: str):
    Print.print_err(f"§4插件 {pluginName} 报错, 信息：§c\n" + trace)

class Builtins:
    class SimpleJsonDataReader:
        @staticmethod
        def SafeOrJsonDump(obj: str | dict | list, fp):
            """
            导出一个json文件, 弥补orjson库没有dump方法的不足.
                obj: json对象.
                fp: open(...)打开的文件读写口 或 文件路径.
            """
            if isinstance(fp, str):
                fp = open(fp, "w", encoding="utf-8")
            fp.write(orjson.dumps(obj, option = orjson.OPT_INDENT_2).decode("utf-8"))
            fp.close()
        @staticmethod
        def SafeOrJsonLoad(fp):
            """
            读取一个json文件, 弥补orjson库没有load方法的不足.
                fp: open(...)打开的文件读写口 或 文件路径.
            """
            if isinstance(fp, str):
                fp = open(fp, "r", encoding="utf-8")
            d = orjson.loads(fp.read())
            fp.close()
            return d
        class DataReadError(orjson.JSONDecodeError):...
        @staticmethod
        def readFileFrom(plugin_name: str, file: str, default: dict = None):
            """
            使用插件便捷地读取一个json文件, 当文件不存在则创建一个空文件, 使用default给出的json默认值写入文件.
            这个文件应在data/<plugin_name>/<file>文件夹内
            """
            filepath = f"data/{plugin_name}/{file}.json"
            os.makedirs(f"data/{plugin_name}", exist_ok=True)
            try:
                if default is not None and not os.path.isfile(filepath):
                    Builtins.SimpleJsonDataReader.SafeOrJsonDump(default, open(filepath, "w", encoding='utf-8'))
                    return default
                return Builtins.SimpleJsonDataReader.SafeOrJsonLoad(open(filepath, "r", encoding='utf-8'))
            except orjson.JSONDecodeError as err:
                raise Builtins.SimpleJsonDataReader.DataReadError(err.msg, err.doc, err.pos)
        @staticmethod
        def writeFileTo(plugin_name: str, file: str, obj):
            """
            使用插件简单地写入一个json文件
            这个文件应在data/<plugin_name>/<file>文件夹内
            """
            os.makedirs(f"data/{plugin_name}", exist_ok=True)
            Builtins.SimpleJsonDataReader.SafeOrJsonDump(obj, open(f"data/{plugin_name}/{file}.json", "w", encoding='utf-8'))
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

    class ArgsReplacement:
        def __init__(this, kw: dict[str, any]):
            this.kw = kw
        def replaceTo(this, __sub: str):
            for k, v in this.kw.items():
                if k in __sub:
                    __sub = __sub.replace(k, str(v))
            return __sub
        
    class TMPJson:
        @staticmethod
        def loadPathJson(path, needFileExists: bool = True):
            """
            将json文件加载到缓存区, 以便快速读写.
            needFileExists = False 时, 若文件路径不存在, 就会自动创建一个文件.
            path 作为文件的真实路径的同时也会作为在缓存区的虚拟路径
            """
            try:
                js = Builtins.SimpleJsonDataReader.SafeOrJsonLoad(path)
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
            """
            if jsonPathTmp.get(path) is not None:
                isChanged, dat = jsonPathTmp[path]
                if isChanged:
                    Builtins.SimpleJsonDataReader.SafeOrJsonDump(dat, path)
                del jsonPathTmp[path]
                return True
            else:
                return False
        @staticmethod
        def read(path):
            "对缓存区的该虚拟路径的文件进行读操作"
            if path in jsonPathTmp.keys():
                return jsonPathTmp.get(path)[1]
            else:
                raise Exception("json路径未初始化, 不能进行读取和写入操作")
        @staticmethod
        def write(path, obj):
            "对缓存区的该虚拟路径的文件进行写操作"
            if path in jsonPathTmp.keys():
                jsonPathTmp[path] = [True, obj]
            else:
                raise Exception("json路径未初始化, 不能进行读取和写入操作")

def safe_close():
    for k, (isChanged, dat) in jsonPathTmp.items():
        if isChanged:
            Builtins.SimpleJsonDataReader.SafeOrJsonDump(dat, k)

def _tmpjson_save_thread():
    while 1:
        time.sleep(60)
        for k, (isChanged, dat) in jsonPathTmp.copy().items():
            if isChanged:
                Builtins.SimpleJsonDataReader.SafeOrJsonDump(dat, k)
                jsonPathTmp[k][0] = False

def tmpjson_save_thread(frame):
    frame.ClassicThread(_tmpjson_save_thread)

jsonPathTmp = {}
