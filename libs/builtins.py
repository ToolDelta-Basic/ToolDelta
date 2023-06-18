from libs.color_print import Print
import orjson, os
def on_plugin_err_common(pluginName: str, _, trace: str):
    Print.print_err(f"§4插件 {pluginName} 报错, 信息：§c\n" + trace)

class Builtins:
    class SimpleJsonDataReader:
        @staticmethod
        def SafeOrJsonDump(obj: str | dict | list, fp):
            fp.write(orjson.dumps(obj))
            fp.close()
        @staticmethod
        def SafeOrJsonLoad(fp):
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
    def SimpleFmt(this, kw: dict[str, any], __sub: str):
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
        
