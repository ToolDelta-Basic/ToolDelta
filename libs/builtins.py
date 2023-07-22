from libs.color_print import Print
import orjson, os, time, threading
def on_plugin_err_common(pluginName: str, _, trace: str):
    Print.print_err(f"§4插件 {pluginName} 报错, 信息：§c\n" + trace)

class Builtins:
    class SimpleJsonDataReader:
        @staticmethod
        def SafeOrJsonDump(obj: str | dict | list, fp):
            if isinstance(fp, str):
                fp = open(fp, "w", encoding="utf-8")
            fp.write(orjson.dumps(obj, option = orjson.OPT_INDENT_2).decode("utf-8"))
            fp.close()
        @staticmethod
        def SafeOrJsonLoad(fp):
            if isinstance(fp, str):
                fp = open(fp, "r", encoding="utf-8")
            d = orjson.loads(fp.read())
            fp.close()
            return d
        class DataReadError(orjson.JSONDecodeError):...
        @staticmethod
        def readFileFrom(plugin_name: str, file: str, default: dict = None):
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
            os.makedirs(f"data/{plugin_name}", exist_ok=True)
            Builtins.SimpleJsonDataReader.SafeOrJsonDump(obj, open(f"data/{plugin_name}/{file}.json", "w", encoding='utf-8'))
    @staticmethod
    def SimpleFmt(kw: dict[str, any], __sub: str):
        for k, v in kw.items():
            if k in __sub:
                __sub = __sub.replace(k, str(v))
        return __sub
    @staticmethod
    def simpleAssert(cond: any, exc):
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
            if path in jsonPathTmp.keys():
                return jsonPathTmp.get(path)[1]
            else:
                raise Exception("json路径未初始化, 不能进行读取和写入操作")
        @staticmethod
        def write(path, obj):
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