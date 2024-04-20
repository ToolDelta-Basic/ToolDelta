"""配置文件模块"""

import os
from typing import Any
import ujson

NoneType = type(None)

PLUGINCFG_DEFAULT = {"配置版本": "0.0.1", "配置项": None}

PLUGINCFG_STANDARD_TYPE = {"配置版本": str, "配置项": [type(None), dict]}


def _CfgIsinstance(obj, typ):
    # 专用于Cfg的类型检测
    if isinstance(typ, type):
        return {
            Cfg.PInt: lambda: isinstance(obj, int) and obj > 0,
            Cfg.NNInt: lambda: isinstance(obj, int) and obj >= 0,
            Cfg.PFloat: lambda: isinstance(obj, float) and obj > 0,
            Cfg.NNFloat: lambda: (isinstance(obj, float) or obj == 0) and obj >= 0,
            Cfg.PNumber: lambda: isinstance(obj, (int, float)) and obj > 0,
            Cfg.NNNumber: lambda: isinstance(obj, (int, float)) and obj >= 0,
        }.get(typ, lambda: isinstance(obj, typ))()
    if isinstance(typ, tuple):
        try:
            for i in typ:
                result = {
                    Cfg.PInt: lambda: isinstance(obj, int) and obj > 0,
                    Cfg.NNInt: lambda: isinstance(obj, int) and obj >= 0,
                    Cfg.PFloat: lambda: isinstance(obj, float) and obj > 0,
                    Cfg.NNFloat: lambda: (isinstance(obj, float) or obj == 0)
                    and obj >= 0,
                    Cfg.PNumber: lambda: isinstance(obj, (int, float)) and obj > 0,
                    Cfg.NNNumber: lambda: isinstance(obj, (int, float)) and obj >= 0,
                }.get(i, lambda: isinstance(obj, typ))()
                if result:
                    return True
            return False
        except TypeError as e:
            raise ValueError(f"Can't be: {typ}") from e
    raise ValueError(f"Can't be: {typ}")


def _CfgShowType(typ: Any) -> str:
    """转换类型为中文字符串

    Args:
        typ (Any): 类型

    Returns:
        str: 中文字符串
    """
    if isinstance(typ, type):
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
        NoneType: "null",
    }.get(typ, typ.__name__)


FIND_NONE = r"%FindNone"


class Cfg:
    """配置文件模块"""
    class Group:
        """配置文件的键组合, 用于检测多个键中的一个是否存在"""

        def __init__(self, *keys):
            self.members = keys

        def __repr__(self) -> str:
            return 'Cfg.Group("' + '", "'.join(self.members) + '")'

    class ConfigError(Exception):
        "配置文件错误"

        def __init__(self, errStr: str, errPos: list | None = None):
            if errPos is None:
                errPos = []
            self.errPos = errPos
            self.args = (errStr,)

    class UnneccessaryKey:
        "配置文件的多余键"

        def __init__(self, key):
            self.key = key

        def __repr__(self):
            return f"Cfg.UnneccessaryKey({self.key})"

    class ConfigKeyError(ConfigError):
        "配置json的键错误"

    class ConfigValueError(ConfigError):
        "配置json的值错误"

    class VersionLowError(ConfigError):
        "配置json的版本过低的错误"

    class PInt(int):
        "配置文件的值限制: 正整数"

    class NNInt(int):
        "配置文件的值限制: 非负整数"

    class PFloat(float):
        "配置文件的值限制: 正浮点小数"

    class NNFloat(float):
        "配置文件的值限制: 非负浮点小数"

    class PNumber:
        "配置文件的值限制: 正数"

    class NNNumber:
        "配置文件的值限制: 大于0的数"

    def get_cfg(self, path: str, standard_type: dict):
        "从path路径获取json文件文本信息, 并按照standard_type给出的标准形式进行检测."
        path = path if path.endswith(".json") else path + ".json"
        with open(path, "r", encoding="utf-8") as f:
            try:
                obj = ujson.load(f)
            except ujson.JSONDecodeError as exc:
                raise self.ConfigValueError(
                    "JSON配置文件格式不正确, 请修正或直接删除", None) from exc
        self.check_dict_2(standard_type, obj)
        return obj

    @staticmethod
    def default_cfg(path: str, default: dict, force: bool = False) -> None:
        """生成默认配置文件

        Args:
            path (str): 路径
            default (dict): 默认配置
            force (bool, optional): 是否强制生成
        """
        path = path if path.endswith(".json") else path + ".json"
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
        return os.path.isfile(path if path.endswith(".json") else path + ".json")

    def getPluginConfigAndVersion(
        self,
        pluginName: str,
        standardType: dict,
        default: dict,
        default_vers: tuple[int, int, int] | list,
    ) -> tuple[dict[str, Any], tuple[int, ...]]:
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
        p = "插件配置文件/" + pluginName
        if not self.exists(p) and default:
            defaultCfg = PLUGINCFG_DEFAULT.copy()
            defaultCfg["配置项"] = default
            defaultCfg["配置版本"] = ".".join([str(n) for n in default_vers])
            self.check_auto(standardType, default)
            self.default_cfg(p + ".json", defaultCfg, force=True)
        cfg_stdtyp = PLUGINCFG_STANDARD_TYPE.copy()
        cfg_stdtyp["配置项"] = standardType
        cfgGet = self.get_cfg(p, cfg_stdtyp)
        cfgVers = tuple(int(c) for c in cfgGet["配置版本"].split("."))
        return cfgGet["配置项"], cfgVers

    def check_auto(self, standard: type | dict | list, val: Any, fromkey: Any = "?") -> None:
        """检查配置文件

        Args:
            standard (type, dict, list): 标准
            val (Any): 值
            fromkey (Any, optional): 键

        Raises:
            ValueError: 未知类型
            self.ConfigValueError: 值错误
            ValueError: 未知类型
        """

        if fromkey == FIND_NONE:
            raise ValueError("不允许传入FindNone")
        if isinstance(standard, type):
            if not _CfgIsinstance(val, standard):
                raise self.ConfigValueError(
                    f'JSON键"{fromkey}" 对应值的类型不正确: 需要 {_CfgShowType(standard)}, 实际上为 {_CfgShowType(val)}'
                )
        elif isinstance(standard, list):
            # [%list] or [multi[type/dict]]
            self.check_list_2(standard, val)
        elif isinstance(standard, dict):
            self.check_dict_2(standard, val)
        else:
            raise ValueError(
                f'JSON键 "{fromkey}"未曾遇到过的类型: {standard.__class__.__name__}, 另外两个参数 standard={standard}, val={val}'
            )

    def check_dict_2(self, pattern: dict, jsondict: dict):
        """
        按照给定的标准配置样式比对传入的配置文件jsondict, 对不上则引发相应异常

        参数:
            pattern: 标准样式dict
            jsondict: 待检测的配置文件dict
        """
        for key, std_val in pattern.items():
            if key == r"%any":
                # ANY key
                for js_key, js_val in jsondict.items():
                    self.check_auto(std_val, js_val, js_key)
            elif isinstance(key, self.Group):
                # any key in members?
                js_val = FIND_NONE
                for member_key in key.members:
                    val_get = jsondict.get(member_key, FIND_NONE)
                    if val_get != FIND_NONE:
                        self.check_auto(std_val, val_get, member_key)
            elif isinstance(key, self.UnneccessaryKey):
                val_get = jsondict.get(key.key, FIND_NONE)
                if val_get != FIND_NONE:
                    self.check_auto(std_val, val_get, key.key)
            else:
                val_get = jsondict.get(key, FIND_NONE)
                if val_get == FIND_NONE:
                    raise self.ConfigKeyError(f"不存在的JSON键: {key}")
                self.check_auto(std_val, val_get, key)

    def check_list_2(self, pattern: list, value: Any, fromkey: Any = "?") -> None:
        """检查列表

        Args:
            pattern (list): 标准
            value (Any): 值
            fromkey (Any, optional): 键

        Raises:
            ValueError: 不是合法的标准列表检测样式
            ValueError: 标准检测列表的长度不能为0
            self.ConfigValueError: json键值错误
        """
        if not isinstance(pattern, list):
            raise ValueError("不是合法的标准列表检测样式")
        if len(pattern) == 0:
            raise ValueError("标准检测列表的长度不能为0")
        if isinstance(pattern[0], str) and pattern[0].startswith(r"%list"):
            if not isinstance(value, list):
                raise self.ConfigValueError(
                    f'JSON键 "{fromkey}" 需要列表 而不是 {_CfgShowType(value)}'
                )
            limitNumber = 0
            if pattern[0].replace(r"%list", "").isnumeric():
                limitNumber = int(pattern[0].replace(r"%list", ""))
            if limitNumber and len(value) != limitNumber:
                raise self.ConfigValueError(
                    f'JSON键 "{fromkey}" 所对应的值列表有误: 需要 {limitNumber} 项, 实际上为 {len(value)} 项'
                )
            for val in value:
                self.check_auto(pattern[1], val, fromkey)
        else:
            for single_type in pattern:
                try:
                    self.check_auto(single_type, value, fromkey)
                    return
                except Exception:
                    pass
            raise self.ConfigValueError(
                f"JSON列表的值 \"{fromkey}\" 类型不正确: 需要 {' 或 '.join(_CfgShowType(i) for i in pattern)}, 实际上为 {_CfgShowType(value)}"
            )

    def auto_to_std(self, cfg):
        """
        自动以默认配置文件生成标准配置文件格式.
        注意: 不支持固定长度列表以及Cfg.NeccessaryKey与Cfg.Group的自动转换

        参数:
            cfg: 默认的CFG配置文件
        返回:
            标准cfg样式, 用于 checkDict
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
                if isinstance(v, (dict, list)):
                    t = self.auto_to_std(v)
                else:
                    t = type(v)
                if t not in setting_types:
                    setting_types.append(t)
            if len(setting_types) == 1:
                return [r"%list", setting_types[0]]
            return [r"%list", setting_types]
        raise ValueError("auto_to_std() 仅接受 dict 与 list 参数")

    checkDict = check_dict_2


if __name__ == "__main__":
    # Test Part
    try:
        test_cfg = [{"b": 1}]
        a = [1, 2, 3, {"b": True}]
        std = Cfg().auto_to_std(a)
        print(std)
        Cfg().check_auto(std, test_cfg)
    except Cfg.ConfigError:
        import traceback

        print(traceback.format_exc())
