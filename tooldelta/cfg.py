"""配置文件模块"""

import os
from typing import Any

import ujson

NoneType = type(None)

PLUGINCFG_DEFAULT = {"配置版本": "0.0.1", "配置项": None}
PLUGINCFG_STANDARD_TYPE = {"配置版本": str, "配置项": [type(None), dict]}


def cfg_isinstance_single(obj: Any, typ: type) -> bool:
    if not isinstance(typ, type):
        raise TypeError(f"cfg_isinstance arg 1 must be a type, not {typ}")
    return {
        Cfg.PInt: lambda: isinstance(obj, int) and obj > 0,
        Cfg.NNInt: lambda: isinstance(obj, int) and obj >= 0,
        Cfg.PFloat: lambda: isinstance(obj, float) and obj > 0,
        Cfg.NNFloat: lambda: (isinstance(obj, float) or obj == 0) and obj >= 0,
        Cfg.PNumber: lambda: isinstance(obj, (int, float)) and obj > 0,
        Cfg.NNNumber: lambda: isinstance(obj, (int, float)) and obj >= 0,
        int: lambda: type(obj) is int,
    }.get(typ, lambda: isinstance(obj, typ))()


def cfg_isinstance(obj: Any, typ: type | tuple[type]):
    """
    专用于 Cfg 的类型检测

    Args:
        obj (Any): 待检测对象
        typ (Any | tuple[Any]): 类型或类型元组

    Returns:
        bool: 是否为对应类型
    """
    if isinstance(typ, type):
        return cfg_isinstance_single(obj, typ)
    if isinstance(typ, tuple):
        try:
            return any(cfg_isinstance_single(obj, i) for i in typ)
        except TypeError as e:
            raise ValueError(f"cfg_isinstance arg 2 can't be: {typ}") from e
    else:
        raise ValueError(f"cfg_isinstance arg 2 can't be: {typ}")


def _CfgShowType(typ: Any) -> str:
    """转换类型为中文字符串

    Args:
        typ (Any): 类型

    Returns:
        str: 中文字符串
    """
    if not isinstance(typ, type):
        typ = type(typ)
    return {
        Cfg.PInt: "正整数",
        Cfg.NNInt: "非负整数",
        Cfg.PFloat: "正浮点小数",
        Cfg.NNFloat: "非负浮点小数",
        str: "字符串",
        float: "浮点小数",
        int: "整数",
        dict: "json 对象",
        list: "列表",
        bool: "true/false",
        NoneType: "null",
    }.get(typ, typ.__name__)


class Cfg:
    """配置文件模块"""

    class ConfigError(Exception):
        """配置文件错误"""

        def __init__(self, errStr: str, errPos: list | None = None):
            if errPos is None:
                errPos = []
            self.errPos = errPos
            self.args = (errStr,)

    class JsonList:
        """配置文件的列表类型"""

        def __init__(self, patt: type | dict | tuple[type | dict, ...], len_limit=-1):
            self.patt = patt
            self.len_limit = len_limit

    class AnyKeyValue:
        """配置文件的任意键名键值对类型"""

        def __init__(self, val_type: type | tuple[type] | dict):
            self.type = val_type

    class KeyGroup:
        """配置文件的键组，充当 dict_key 使用"""

        def __init__(self, *keys: str):
            self.keys = keys

    class ConfigKeyError(ConfigError):
        """配置 json 的键错误"""

    class ConfigValueError(ConfigError):
        """配置 json 的值错误"""

    class VersionLowError(ConfigError):
        """配置 json 的版本过低的错误"""

    class PInt(int):
        """配置文件的值限制：正整数"""

    class NNInt(int):
        """配置文件的值限制：非负整数"""

    class PFloat(float):
        """配置文件的值限制：正浮点小数"""

    class NNFloat(float):
        """配置文件的值限制：非负浮点小数"""

    class PNumber:
        """配置文件的值限制：正数"""

    class NNNumber:
        """配置文件的值限制：大于 0 的数"""

    class FindNone:
        """找不到值"""

    def get_cfg(self, path: str, standard_type: dict):
        """从 path 路径获取 json 文件文本信息，并按照 standard_type 给出的标准形式进行检测。"""
        path = path if path.endswith(".json") else f"{path}.json"
        with open(path, "r", encoding="utf-8") as f:
            try:
                obj = ujson.load(f)
            except ujson.JSONDecodeError as exc:
                raise self.ConfigValueError(
                    "JSON 配置文件格式不正确，请修正或直接删除", None
                ) from exc
        self.check_dict(standard_type, obj)
        return obj

    @staticmethod
    def default_cfg(path: str, default: dict, force: bool = False) -> None:
        """生成默认配置文件

        Args:
            path (str): 路径
            default (dict): 默认配置
            force (bool, optional): 是否强制生成
        """
        path = path if path.endswith(".json") else f"{path}.json"
        if force or not os.path.isfile(path):
            with open(path, "w", encoding="utf-8") as f:
                ujson.dump(default, f, indent=4, ensure_ascii=False)

    @staticmethod
    def exists(path: str) -> bool:
        """判断文件是否存在

        Args:
            path (str): 路径

        Returns:
            bool: 是否存在
        """
        return os.path.isfile(path if path.endswith(".json") else f"{path}.json")

    def get_plugin_config_and_version(
        self,
        pluginName: str,
        standardType: Any,
        default: dict,
        default_vers: tuple[int, int, int] | list,
    ) -> tuple[dict[str, Any], tuple[int, int, int]]:
        """获取插件配置文件及版本

        Args:
            pluginName (str): 插件名
            standardType (dict): 标准类型
            default (dict): 默认配置
            default_vers (tuple[int, int, int]): 默认版本

        Returns:
             tuple[dict[str, Any], tuple[int, ...]]: 配置文件及版本
        """
        # 详情见 插件编写指南.md
        assert isinstance(standardType, dict)
        p = f"插件配置文件/{pluginName}"
        if not self.exists(p) and default:
            defaultCfg = PLUGINCFG_DEFAULT.copy()
            defaultCfg["配置项"] = default
            defaultCfg["配置版本"] = ".".join([str(n) for n in default_vers])
            self.check_auto(standardType, default)
            self.default_cfg(f"{p}.json", defaultCfg, force=True)
        cfg_stdtyp = PLUGINCFG_STANDARD_TYPE.copy()
        cfg_stdtyp["配置项"] = standardType
        cfgGet = self.get_cfg(p, cfg_stdtyp)
        cfgVers = tuple(int(c) for c in cfgGet["配置版本"].split("."))
        if len(cfgVers) != 3:
            raise ValueError("配置文件出错：版本出错")
        return cfgGet["配置项"], cfgVers

    getPluginConfigAndVersion = get_plugin_config_and_version

    def check_auto(
        self,
        standard: type | dict | JsonList | tuple[type | dict, ...],
        val: Any,
        fromkey: str = "?",
    ):
        """检查配置文件 (自动类型判断)

        Args:
            standard (type, dict, list): 标准
            val (Any): 值
            fromkey (Any, optional): 键

        Raises:
            ValueError: 未知标准检测类型
            ConfigValueError: 值错误
        """
        if fromkey == Cfg.FindNone:
            raise ValueError("不允许传入 FindNone")
        if isinstance(standard, type):
            if not cfg_isinstance(val, standard):
                if isinstance(val, dict):
                    raise self.ConfigValueError(
                        f'JSON 键"{fromkey}" 对应值的类型不正确：需要 {_CfgShowType(standard)}, '
                        f"实际上为 json 对象：{ujson.dumps(val, ensure_ascii=False)}"
                    )
                raise self.ConfigValueError(
                    f'JSON 键"{fromkey}" 对应值的类型不正确：需要 {_CfgShowType(standard)}, 实际上为 {_CfgShowType(val)}'
                )
        elif isinstance(standard, Cfg.JsonList):
            self.check_list(standard, val, fromkey)
        elif isinstance(standard, (tuple, list)):
            errs = []
            for single_type in standard:
                try:
                    self.check_auto(single_type, val, fromkey)
                    break
                except Exception as err:
                    errs.append(err)
            else:
                reason = "\n".join(str(err) for err in errs)
                raise self.ConfigValueError(
                    f'JSON 键 对应的键"{fromkey}" 类型不正确，以下为可能的原因：\n{reason}'
                )
        elif isinstance(standard, (dict, Cfg.AnyKeyValue)):
            self.check_dict(standard, val, fromkey)
        else:
            raise ValueError(
                f'JSON 键 "{fromkey}" 自动检测的标准类型传入异常：{standard}'
            )

    def check_dict(self, pattern: dict | AnyKeyValue, jsondict: Any, from_key="?"):
        """
        按照给定的标准配置样式比对传入的配置文件 jsondict, 对不上则引发相应异常

        参数:
            pattern: 标准样式 dict
            jsondict: 待检测的配置文件 dict
        """
        if not isinstance(jsondict, dict):
            raise ValueError(
                f'json 键"{from_key}" 需要 json 对象，而不是 {_CfgShowType(jsondict)}'
            )
        if isinstance(pattern, Cfg.AnyKeyValue):
            for key, val in jsondict.items():
                self.check_auto(pattern.type, val, key)
        else:
            for key, std_val in pattern.items():
                if isinstance(key, self.KeyGroup):
                    for k, v in jsondict.items():
                        if k in key.keys:
                            self.check_auto(std_val, v, k)
                elif isinstance(key, str):
                    val_get = jsondict.get(key, Cfg.FindNone)
                    if val_get == Cfg.FindNone:
                        raise self.ConfigKeyError(f"不存在的 JSON 键：{key}")
                    self.check_auto(std_val, val_get, key)
                else:
                    raise ValueError(f"Invalid key type: {key.__class__.__name__}")

    def check_list(self, pattern: JsonList, value: Any, fromkey: Any = "?") -> None:
        """检查列表

        Args:
            pattern (list): 标准
            value (Any): 值
            fromkey (Any, optional): 键

        Raises:
            ValueError: 不是合法的标准列表检测样式
            ValueError: 标准检测列表的长度不能为 0
            ConfigValueError: json 键值错误
        """
        if not isinstance(pattern, Cfg.JsonList):
            raise ValueError("不是合法的标准列表检测样式")
        if not isinstance(value, list):
            raise self.ConfigValueError(
                f'JSON 键 "{fromkey}" 需要列表 而不是 {_CfgShowType(value)}'
            )
        if pattern.len_limit != -1 and len(value) != pattern.len_limit:
            raise self.ConfigValueError(
                f'JSON 键 "{fromkey}" 所对应的值列表有误：需要 {pattern.len_limit} 项，实际上为 {len(value)} 项'
            )
        for val in value:
            self.check_auto(pattern.patt, val, fromkey)

    def auto_to_std(self, cfg):
        """
        自动以默认配置文件生成标准配置文件格式.
        注意：不支持固定长度列表以及 Cfg.NeccessaryKey 与 Cfg.Group 的自动转换

        Args:
            cfg: 默认的 CFG 配置文件
        Returns:
            标准 cfg 样式，用于 check_dict
        """
        if isinstance(cfg, dict):
            res = {}
            for k, v in cfg.items():
                if isinstance(v, (dict, list)):
                    res[k] = self.auto_to_std(v)
                elif isinstance(v, (str, int, float, bool)):
                    res[k] = type(v)
            return res
        if isinstance(cfg, list):
            setting_types = []
            for v in cfg:
                t = self.auto_to_std(v) if isinstance(v, (dict, list)) else type(v)
                if t not in setting_types:
                    setting_types.append(t)
            if len(setting_types) == 1:
                return Cfg.JsonList(setting_types[0])
            return Cfg.JsonList(tuple(setting_types))
        raise ValueError("auto_to_std() 仅接受 dict 与 list 参数")

    checkDict = check_dict


Config = Cfg()
