import json, os

NoneType = type(None)

PLUGINCFG_DEFAULT = {
    "配置版本": "0.0.1",
    "配置项": None
}
PLUGINCFG_STANDARD_TYPE = {
    "配置版本": str,
    "配置项": [type(None), dict]
}

def _CfgIsinstance(obj, typ):
    return {
        Cfg.PInt: lambda:isinstance(obj, int) and obj > 0, 
        Cfg.NNInt: lambda:isinstance(obj, int) and obj >= 0,
        Cfg.PFloat: lambda:isinstance(obj, float) and obj > 0,
        Cfg.NNFloat: lambda:(isinstance(obj, float) and obj > 0) or obj == 0,
    }.get(typ, lambda:isinstance(obj, typ))()

def _CfgShowType(typ):
    if type(typ) != type:
        typ = type(typ)
    return {
        Cfg.PInt: "正整数",
        Cfg.NNInt: "非负整数",
        Cfg.PFloat: "正浮点小数",
        Cfg.NNFloat: "非负浮点小数",
        str: "字符串",
        float: "浮点小数",
        int: "整数",
        dict: "json对象",
        list: "列表",
        NoneType: "null"
    }.get(typ, typ.__name__)

class Cfg:
    class ConfigError(Exception):
        def __init__(this, errStr: str, errPos: list):
            this.errPos = errPos
            this.args = (errStr,)
    class ConfigKeyError(ConfigError):...
    class ConfigValueError(ConfigError):...
    class VersionLowError(ConfigError):...
    class PInt(int):"正整数"
    class NNInt(int):"非负整数"
    class PFloat(float):"正浮点小数"
    class NNFloat(float):"非负浮点小数"

    def get_cfg(this, path: str, standard_type: dict):
        path = path if path.endswith(".json") else path + ".json"
        with open(path, "r", encoding="utf-8") as f:
            try:
                obj = json.load(f)
            except json.JSONDecodeError:
                raise this.ConfigValueError("JSON配置文件格式不正确, 请修正或直接删除", None)
        this.checkDict(standard_type, obj)
        return obj

    def default_cfg(this, path: str, default: dict, force: bool = False):
        path = path if path.endswith(".json") else path + ".json"
        if force or not os.path.isfile(path):
            with open(path, "w", encoding='utf-8') as f:
                json.dump(default, f, indent=4, ensure_ascii=False)

    def exists(this, path: str):
        return os.path.isfile(path if path.endswith(".json") else path + ".json")

    def checkDict(this, patt: dict, cfg: dict | list, __nowcheck: list = []):
        patt = patt.copy()
        __nowcheck.append(None)
        assert patt is not None, "Patt = None???"
        if _CfgIsinstance(patt, list) and patt[0] == "%list":
            this.checkList(patt[1], cfg)
            return
        if not _CfgIsinstance(patt, dict) or not _CfgIsinstance(cfg, dict):
            raise this.ConfigValueError(f"JSON值 应为json, 而非{_CfgShowType(cfg)}: 获取{cfg}, 需要{patt}", __nowcheck)
        for k, v in patt.items():
            if k == r"%any":
                for k2, v2 in cfg.items():
                    __nowcheck[-1] = str(k2)
                    if _CfgIsinstance(v, type):
                        if not _CfgIsinstance(v2, v):
                            raise this.ConfigValueError(f"JSON键\"{k2}\" 所对应的值类型不正确: 需要 {_CfgShowType(v)}, 实际上为 {_CfgShowType(v2)}", __nowcheck)
                    elif _CfgIsinstance(v, list):
                        if v[0] == r"%list":
                            this.checkList(v[1], v2)
                        else:
                            if type(v2) not in v:
                                raise this.ConfigValueError(f"JSON键\"{k2}\" 所对应的值类型不正确: 需要 {' 或 '.join(_CfgShowType(i) for i in patt[k])}, 实际上为 {_CfgShowType(v2)}", __nowcheck)
                    elif _CfgIsinstance(v, dict):
                        this.checkDict(v, v2)
            else:
                v2 = cfg.get(k, r"%Exception")
                if v2 == r"%Exception":
                    raise this.ConfigKeyError(f'不存在的JSON键: {k}', __nowcheck)
                __nowcheck[-1] = str(v2)
                if _CfgIsinstance(v, type):
                    # Compare directly
                    if not _CfgIsinstance(v2, v):
                        raise this.ConfigValueError(f"JSON键\"{k}\" 所对应的值类型不正确: 需要 {_CfgShowType(v)}, 实际上为 {_CfgShowType(v2)}", __nowcheck)
                elif _CfgIsinstance(v, list):
                    # Met ["%list", any] or [type1, type2..]
                    if v[0] == r"%list":
                        # Met ["%list", any]
                        this.checkList(v[1], v2, __nowcheck)
                    elif _CfgIsinstance(v, list):
                        # Met [type1, type2..]
                        isAllType = all([_CfgIsinstance(vi, type) for vi in v])
                        if isAllType:
                            if type(v2) not in v:
                                raise this.ConfigValueError(f"JSON键\"{k}\" 所对应的值类型不正确: 需要 {' 或 '.join(_CfgShowType(i) for i in patt[k])}, 实际上为 {_CfgShowType(v2)}", __nowcheck)
                        else:
                            # AAAAH!
                            # List[type, dict, ...] ?
                            for v_identifier in v:
                                if _CfgIsinstance(v_identifier, dict) and _CfgIsinstance(v2, dict):
                                    try:
                                        this.checkDict(v_identifier, v2)
                                        return
                                    except Exception as exc:
                                        exc_raise = exc
                                elif _CfgIsinstance(v_identifier, type):
                                    if not _CfgIsinstance(v2, v_identifier):
                                        exc_raise = this.ConfigValueError(f"JSON键\"{k}\" 所对应的值类型不正确: 需要 {' 或 '.join(_CfgShowType(i) for i in v)} 等, 实际上为 {_CfgShowType(v2)}\n可能的另一个错误: {exc_raise}", __nowcheck)
                                    else:
                                        return
                            raise exc_raise
                    else:
                        raise this.ConfigValueError(f"??????: v={v} while v2={v2}", __nowcheck)
                elif _CfgIsinstance(v, dict):
                    this.checkDict(v, v2)

    def checkList(this, patt, lst: list, __nowcheck: list = []):
        if not _CfgIsinstance(lst, list):
            raise this.ConfigValueError(f"List Error: {patt} ? {lst}", __nowcheck)
        __nowcheck.append(None)
        for v in lst:
            __nowcheck[-1] = v
            if _CfgIsinstance(patt, type):
                if not _CfgIsinstance(v, patt):
                    raise this.ConfigValueError(f"JSON键列表的值\"{v}\" 的类型不正确: 需要 {_CfgShowType(patt)}, 实际上为 {_CfgShowType(v)}", __nowcheck)
            elif _CfgIsinstance(patt, list):
                if patt[0] == r"%list":
                    this.checkList(patt[1], v, __nowcheck)
                else:
                    if type(v) not in patt:
                        raise this.ConfigValueError(f"JSON列表的值\"{v}\" 类型不正确: 需要 {' 或 '.join(_CfgShowType(i) for i in patt)}, 实际上为 {_CfgShowType(v)}", __nowcheck)
            elif _CfgIsinstance(patt, dict):
                this.checkDict(patt, v, __nowcheck)

    def getPluginConfigAndVersion(this, pluginName: str, standardType: dict, default: dict, default_vers: tuple[int, int, int]):
        assert isinstance(standardType, dict)
        p = "插件配置文件/" + pluginName
        if not this.exists(p) and default:
            defaultCfg = PLUGINCFG_DEFAULT.copy()
            defaultCfg["配置项"] = default
            defaultCfg["配置版本"] = ".".join([str(n) for n in default_vers])
            this.default_cfg(p + ".json", defaultCfg, force=True)
            return default, default_vers
        cfg_stdtyp = PLUGINCFG_STANDARD_TYPE.copy()
        cfg_stdtyp["配置项"] = standardType
        cfgGet = this.get_cfg(p, cfg_stdtyp)
        cfgVers = tuple(int(c) for c in cfgGet["配置版本"].split("."))
        return cfgGet["配置项"], cfgVers

if __name__ == "__main__":
    try:
        a_mapping = [{"a": 0.1}]
        a_std = ["%list", {"a": Cfg.NNFloat}]
        Cfg().checkDict(a_std, a_mapping)
    except Cfg.ConfigError as err:
        import traceback
        print(traceback.format_exc())