from libs.color_print import Print
import json, os
def on_plugin_err_common(pluginName: str, _, trace: str):
    Print.print_err(f"§4插件 {pluginName} 报错, 信息：§c\n" + trace)

class Builtins:
    class SimpleJsonDataReader:
        class DataReadError(json.JSONDecodeError):...
        def readFileFrom(this, plugin_name: str, file: str, default: dict = None):
            filepath = f"data/{plugin_name}/{file}.json"
            os.makedirs(f"data/{plugin_name}", exist_ok=True)
            try:
                if default is not None and not os.path.isfile(filepath):
                    with open(filepath, "w", encoding='utf-8') as f:
                        json.dump(default, f)
                        return default
                with open(filepath, "r", encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError as err:
                raise this.DataReadError(err.msg, err.doc, err.pos)
            
        def writeFileTo(this, plugin_name: str, file: str, obj):
            os.makedirs(f"data/{plugin_name}", exist_ok=True)
            with open(f"data/{plugin_name}/{file}.json", "w", encoding='utf-8') as f:
                json.dump(obj, f)
    class ArgsReplacement:
        def __init__(this, kw: dict[str, any]):
            this.kw = kw
        def replaceTo(this, __sub: str):
            for k, v in this.kw.items():
                if k in __sub:
                    __sub = __sub.replace(k, str(v))
            return __sub
