"""配置文件模块"""

import os
import json
from typing import Any
from ..constants import TOOLDELTA_PLUGIN_CFG_DIR


NoneType = type(None)
VERSION = tuple[int, int, int]

PLUGINCFG_DEFAULT = {"配置版本": "0.0.1", "配置项": None}
PLUGINCFG_STANDARD_TYPE = {"配置版本": str, "配置项": [type(None), dict]}


def _cfg_isinstance_single(obj: Any, typ: type) -> bool:
    if not isinstance(typ, type):
        raise TypeError(f"_cfg_isinstance arg 1 must be a type, not {typ}")
    return {
        PInt: lambda: isinstance(obj, int) and obj > 0,
        NNInt: lambda: isinstance(obj, int) and obj >= 0,
        PFloat: lambda: isinstance(obj, float) and obj > 0,
        NNFloat: lambda: (isinstance(obj, float) or obj == 0) and obj >= 0,
        PNumber: lambda: isinstance(obj, int | float) and obj > 0,
        NNNumber: lambda: isinstance(obj, int | float) and obj >= 0,
    }.get(typ, lambda: isinstance(obj, typ))()


def _cfg_isinstance(obj: Any, typ: type | tuple[type]):
    """
    专用于 Cfg 的类型检测

    Args:
        obj (Any): 待检测对象
        typ (Any | tuple[Any]): 类型或类型元组

    Returns:
        bool: 是否为对应类型
    """
    if isinstance(typ, type):
        return _cfg_isinstance_single(obj, typ)
    if isinstance(typ, tuple):
        try:
            return any(_cfg_isinstance_single(obj, i) for i in typ)
        except TypeError as e:
            raise ValueError(f"_cfg_isinstance arg 2 can't be: {typ}") from e
    else:
        raise ValueError(f"_cfg_isinstance arg 2 can't be: {typ}")


def _get_cfg_type_name(typ: Any) -> str:
    """转换类型为中文字符串

    Args:
        typ (Any): 类型

    Returns:
        str: 中文字符串
    """
    if not isinstance(typ, type):
        typ = type(typ)
    return {
        PInt: "正整数",
        NNInt: "非负整数",
        PFloat: "正浮点小数",
        NNFloat: "非负浮点小数",
        str: "字符串",
        float: "浮点小数",
        int: "整数",
        dict: "json 对象",
        list: "列表",
        bool: "true/false",
        NoneType: "null",
    }.get(typ, typ.__name__)


class ConfigError(Exception):
    """配置文件错误"""

    def __init__(self, errStr: str, errPos: list | None = None):
        if errPos is None:
            errPos = []
        self.errPos = errPos
        self.args = (errStr,)


class JsonList:
    """配置文件的列表类型

    Args:
        patt: 判定规则
        len_limit (int): 限制列表的特定长度, 不限制则为-1
    """

    def __init__(self, patt: Any, len_limit=-1):
        self.patt = patt
        self.len_limit = len_limit


class AnyKeyValue:
    """配置文件的任意键名键值对类型"""

    def __init__(self, val_type: Any):
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


class IntRange:
    """配置文件的值限制：整数域范围"""

    def __init__(self, min: int, max: int):
        self.min = min
        self.max = max


class FloatRange:
    """配置文件的值限制：浮点数域范围"""

    def __init__(self, min: float, max: float):
        self.min = min
        self.max = max


class PNumber:
    """配置文件的值限制：正数"""


class NNNumber:
    """配置文件的值限制：大于 0 的数"""


class FindNone:
    """找不到值"""


def get_cfg(path: str, standard_type: Any):
    """从 path 路径获取 json 文件文本信息，并按照 standard_type 给出的标准形式进行检测。"""
    path = path if path.endswith(".json") else f"{path}.json"
    with open(path, encoding="utf-8") as f:
        try:
            obj = json.load(f)
        except json.JSONDecodeError as exc:
            raise ConfigValueError(
                "JSON 配置文件格式不正确，请修正或直接删除", None
            ) from exc
    check_dict(standard_type, obj)
    return obj


def get_plugin_config_and_version(
    plugin_name: str,
    standard_type: Any,
    default: dict,
    default_vers: VERSION,
) -> tuple[dict[str, Any], VERSION]:
    """
    获取插件配置文件及版本

    Args:
        plugin_name (str): 插件名
        standard_type (dict): 标准类型
        default (dict): 默认配置
        default_vers (tuple[int, int, int]): 默认版本

    Returns:
            tuple[dict[str, Any], tuple[int, int, int]]: 配置文件内容及版本
    """
    # 详情见 插件编写指南.md
    assert isinstance(standard_type, dict)
    p = os.path.join(TOOLDELTA_PLUGIN_CFG_DIR, plugin_name)
    if not _jsonfile_exists(p) and default:
        defaultCfg = PLUGINCFG_DEFAULT.copy()
        defaultCfg["配置项"] = default
        defaultCfg["配置版本"] = ".".join([str(n) for n in default_vers])
        check_auto(standard_type, default)
        default_cfg(f"{p}.json", defaultCfg, force=True)
    cfg_stdtyp = PLUGINCFG_STANDARD_TYPE.copy()
    cfg_stdtyp["配置项"] = standard_type
    cfgGet = get_cfg(p, cfg_stdtyp)
    cfgVers = tuple(int(c) for c in cfgGet["配置版本"].split("."))
    VERSION_LENGTH = 3  # 版本长度
    if len(cfgVers) != VERSION_LENGTH:
        raise ValueError("配置文件出错：版本出错")
    return cfgGet["配置项"], cfgVers


def upgrade_plugin_config(
    plugin_name: str,
    configs: dict,
    version: VERSION,
):
    """
    获取插件配置文件及版本

    Args:
        plugin_name (str): 插件名
        configs (dict): 配置内容
        default_vers (tuple[int, int, int]): 版本
    """
    p = os.path.join(TOOLDELTA_PLUGIN_CFG_DIR, plugin_name)
    defaultCfg = PLUGINCFG_DEFAULT.copy()
    defaultCfg["配置项"] = configs
    defaultCfg["配置版本"] = ".".join([str(n) for n in version])
    write_default_cfg_file(f"{p}.json", defaultCfg, force=True)


def check_auto(
    standard: Any,
    val: Any,
    fromkey: str = "?",
):
    """
    检测任意类型的 json 类型是否合法

    Args:
        standard (type, dict, list): 标准模版
        val (Any): 待检测的值
        fromkey (Any, optional): 从哪个json键向下检索而来

    Raises:
        ValueError: 未知标准检测类型
        ConfigValueError: 值错误
    """
    if fromkey == FindNone:
        raise ValueError("不允许传入 FindNone")
    if isinstance(standard, type):
        if not _cfg_isinstance(val, standard):
            if isinstance(val, dict):
                raise ConfigValueError(
                    f'JSON 键"{fromkey}" 对应值的类型不正确：需要 {_get_cfg_type_name(standard)}, '
                    f"实际上为 json 对象：{json.dumps(val, ensure_ascii=False)}"
                )
            raise ConfigValueError(
                f'JSON 键"{fromkey}" 对应值的类型不正确：需要 {_get_cfg_type_name(standard)}, 实际上为 {_get_cfg_type_name(val)}'
            )
    elif isinstance(standard, JsonList):
        check_list(standard, val, fromkey)
    elif isinstance(standard, dict | AnyKeyValue):
        check_dict(standard, val, fromkey)
    elif isinstance(standard, IntRange):
        check_auto(int, val, fromkey)
        if not standard.min <= val <= standard.max:
            raise ConfigValueError(
                f'JSON 键"{fromkey}" 对应值的范围不正确：需要 {standard.min} ~ {standard.max}, 实际上为 {val}'
            )
    elif isinstance(standard, FloatRange):
        check_auto(float, val, fromkey)
        if not standard.min <= val <= standard.max:
            raise ConfigValueError(
                f'JSON 键"{fromkey}" 对应值的范围不正确：需要 {standard.min} ~ {standard.max}, 实际上为 {val}'
            )
    elif isinstance(standard, tuple | list):
        errs = []
        for single_type in standard:
            try:
                check_auto(single_type, val, fromkey)
                break
            except Exception as err:
                errs.append(err)
        else:
            reason = "\n".join(str(err) for err in errs)
            raise ConfigValueError(
                f'JSON 键 对应的键"{fromkey}" 类型不正确，以下为可能的原因：\n{reason}'
            )
    else:
        raise ValueError(f'JSON 键 "{fromkey}" 自动检测的标准类型传入异常：{standard}')


def auto_to_std(cfg):
    """
    从默认的配置文件内容的字典自动生成检测模版
    注意: 无法自动检测 AnyKeyValue, KeyGroup, PInt, PFloat 等

    Args:
        cfg: 默认的配置文件内容的字典

    Returns:
        标准检测模版样式, 用于 check_dict
    """
    if isinstance(cfg, dict):
        res = {}
        for k, v in cfg.items():
            if isinstance(v, dict | list):
                res[k] = auto_to_std(v)
            elif isinstance(v, str | int | float | bool):
                res[k] = type(v)
        return res
    if isinstance(cfg, list):
        setting_types = []
        for v in cfg:
            t = auto_to_std(v) if isinstance(v, dict | list) else type(v)
            if t not in setting_types:
                setting_types.append(t)
        if len(setting_types) == 1:
            return JsonList(setting_types[0])
        return JsonList(tuple(setting_types))
    raise ValueError("auto_to_std() 仅接受 dict 与 list 参数")


def check_dict(pattern: Any, jsondict: Any, from_key="?"):
    """
    按照给定的标准配置样式比对传入的字典, 键值对不上模版则引发相应异常
    请改为使用 check_auto

    参数:
        pattern: 标准模版 dict
        jsondict: 待检测的配置文件 dict
    """
    if not isinstance(jsondict, dict):
        raise ValueError(
            f'json 键"{from_key}" 需要 json 对象，而不是 {_get_cfg_type_name(jsondict)}'
        )
    if isinstance(pattern, AnyKeyValue):
        for key, val in jsondict.items():
            check_auto(pattern.type, val, key)
    else:
        for key, std_val in pattern.items():
            if isinstance(key, KeyGroup):
                for k, v in jsondict.items():
                    if k in key.keys:
                        check_auto(std_val, v, k)
            elif isinstance(key, str):
                val_get = jsondict.get(key, FindNone)
                if val_get == FindNone:
                    raise ConfigKeyError(f"不存在的 JSON 键：{key}")
                check_auto(std_val, val_get, key)
            else:
                raise ValueError(f"Invalid key type: {key.__class__.__name__}")


def check_list(pattern: JsonList, value: Any, fromkey: Any = "?") -> None:
    """
    检查列表是否合法
    请改为使用 check_auto

    Args:
        pattern (list): 标准模版
        value (Any): 待检测值
        fromkey (Any, optional): 从哪个字典键向下检索而来

    Raises:
        ValueError: 不是合法的标准列表检测样式
        ValueError: 标准检测列表的长度不能为 0
        ConfigValueError: 值错误
    """
    if not isinstance(pattern, JsonList):
        raise ValueError("不是合法的标准列表检测样式")
    if not isinstance(value, list):
        raise ConfigValueError(
            f'JSON 键 "{fromkey}" 需要列表 而不是 {_get_cfg_type_name(value)}'
        )
    if pattern.len_limit != -1 and len(value) != pattern.len_limit:
        raise ConfigValueError(
            f'JSON 键 "{fromkey}" 所对应的值列表有误：需要 {pattern.len_limit} 项，实际上为 {len(value)} 项'
        )
    for val in value:
        check_auto(pattern.patt, val, fromkey)


def write_default_cfg_file(path: str, default: dict, force: bool = False) -> None:
    """
    生成默认配置文件

    Args:
        path (str): 路径
        default (dict): 默认配置
        force (bool, optional): 是否即使是配置文件存在时, 也强制覆盖内容.
    """
    path = path if path.endswith(".json") else f"{path}.json"
    if force or not os.path.isfile(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=4, ensure_ascii=False)


default_cfg = write_default_cfg_file


def _jsonfile_exists(path: str) -> bool:
    return os.path.isfile(path if path.endswith(".json") else f"{path}.json")
