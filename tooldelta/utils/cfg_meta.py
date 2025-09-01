import os
from types import GenericAlias, UnionType
from typing import Generic, TypeVar
from .cfg import (
    TOOLDELTA_PLUGIN_CFG_DIR,
    PLUGINCFG_DEFAULT,
    PLUGINCFG_STANDARD_TYPE,
    _jsonfile_exists,
    get_cfg,
    write_default_cfg_file,
    VERSION,
)

__all__ = ["JsonSchema", "field", "get_plugin_config_and_version"]

T = TypeVar("T")
JsonSchemaT = TypeVar("JsonSchemaT", bound="JsonSchema")
_missing = type("_missing", (), {})


class ConfigError(Exception):
    def __init__(
        self,
        msg: str = "",
        current_key_or_index: str | int | None = None,
        fromerr: "ConfigError | None" = None,
    ):
        if msg:
            self.msg = msg
        elif fromerr:
            self.msg = fromerr.msg
        if fromerr:
            self.pos = [current_key_or_index, *fromerr.pos]
        else:
            self.pos = [current_key_or_index]

    def __str__(self):
        outputs = []
        for arg in self.pos:
            if isinstance(arg, str):
                outputs.append(f'键"{arg}"')
            elif isinstance(arg, int):
                outputs.append(f"列表第{arg + 1}项")
        return " 的 ".join(outputs) + ": " + self.msg


class _Field(Generic[T]):
    def __init__(self, field_name: str, default_value: type[T] | type[_missing]):
        self.field_name = field_name
        self.default_value = default_value
        self._annotation = None

    def __call__(self, annotation):
        self._annotation = annotation
        return self


def field(field_name: str, default: T | type[_missing] = _missing) -> T:
    return _Field(field_name, default)  # type: ignore


class JsonSchema:
    """
    配置文件模版类基类。所有配置模版类都必须继承它。如：
    >>> class MyConfig(JsonSchema):
    ...     cfg_a: int = field("配置A")
    ...     cfg_b: str = field("配置B")
    ...     cfg_c: str | int = field("配置C", "Hello dream")

    基本类型标注仅接受 `str`, `int`, `float`, `bool` 基本类型。
    """

    def __init_subclass__(cls) -> None:
        cls._annotations = cls.__annotations__
        cls._fields = {
            k: v(annotation)
            for k, v in cls.__dict__.items()
            if (annotation := cls._annotations.get(k)) and isinstance(v, _Field)
        }
        cls._checked = False
        annotation_type_check(cls)


checkable_types = (str, int, float, bool, type(None))


def _get_cfg_type_name(typ) -> str:
    """转换类型为中文字符串

    Args:
        typ (Any): 类型

    Returns:
        str: 中文字符串
    """
    if isinstance(typ, UnionType):
        return " 或".join(_get_cfg_type_name(t) for t in typ.__args__)
    if not isinstance(typ, type):
        typ = type(typ)
    return {
        str: "字符串",
        float: "浮点小数",
        int: "整数",
        dict: "json对象",
        list: "列表",
        bool: "true/false",
        type(None): "null",
    }.get(typ, typ.__name__)


def annotation_type_check(typ):
    if typ in checkable_types:
        return
    elif isinstance(typ, GenericAlias):
        # list[...] or dict[str, ...]
        orig = typ.__origin__
        if typ.__origin__ is list:
            if len(typ.__args__) != 1:
                raise ValueError("不支持的泛型类型个数, 最多只能为 1 个")
        elif typ.__origin__ is dict:
            if len(typ.__args__) != 2:
                raise ValueError("不支持的泛型类型个数, 最多只能为 2 个")
            if typ.__args__[0] is not str:
                raise ValueError("dict 泛型首项参数只能为 str")
            annotation_type_check(typ.__args__[1])
        else:
            raise ValueError(f"不支持的泛型类型: {orig}")
        annotation_type_check(typ.__args__[0])
    elif isinstance(typ, UnionType):
        for t in typ.__args__:
            annotation_type_check(t)
    elif issubclass(typ, JsonSchema):
        if typ._checked:
            return
        for v in typ._annotations.values():
            annotation_type_check(v)
        typ._checked = True
    else:
        raise TypeError(f"不支持的类型注释 {typ}")


def load_param_and_type_check(obj, typ: type[T], field_name: str = "") -> T:
    if typ in checkable_types:
        if isinstance(obj, int) and typ is float:
            return obj  # type: ignore
        if not isinstance(obj, typ):
            raise ConfigError(
                f"值 {obj} 类型错误, 需为 {_get_cfg_type_name(typ)}, 得到 {_get_cfg_type_name(type(obj))}"
            )
        return obj  # type: ignore
    elif isinstance(typ, UnionType):
        for t in typ.__args__:
            try:
                return load_param_and_type_check(obj, t)
            except ConfigError:
                pass
        raise ConfigError(
            f"值 {obj} 类型错误, 需为 {_get_cfg_type_name(typ)}, 得到 {_get_cfg_type_name(type(obj))}"
        )
    elif isinstance(typ, GenericAlias):
        # list[...]
        orig = typ.__origin__
        if orig is list:
            if not isinstance(obj, list):
                raise ConfigError(
                    f"值 {obj} 类型错误, 需为列表, 得到 {_get_cfg_type_name(type(obj))}"
                )
            sub_type = typ.__args__[0]
            lst = []
            for i, v in enumerate(obj):
                try:
                    lst.append(load_param_and_type_check(v, sub_type))
                except ConfigError as e:
                    raise ConfigError(current_key_or_index=i, fromerr=e)
            return lst  # type: ignore
        elif orig is dict:
            if not isinstance(obj, dict):
                raise ConfigError(
                    f"值 {obj} 类型错误, 需为json对象, 得到 {_get_cfg_type_name(type(obj))}"
                )
            sub_type = typ.__args__[1]
            dic = {}
            for k, v in obj.items():
                try:
                    dic[k] = load_param_and_type_check(v, sub_type)
                except ConfigError as e:
                    raise ConfigError(current_key_or_index=k, fromerr=e)
            return dic  # type: ignore
        else:
            raise ValueError(f"未知泛型类型 {typ}")
    elif issubclass(typ, JsonSchema):
        if not isinstance(obj, dict):
            raise ValueError(
                f"值 {obj} 类型错误, 需为json, 得到 {_get_cfg_type_name(type(obj))}"
            )
        instance = typ()
        for k, v in instance._fields.items():
            annotation = v._annotation
            assert annotation
            field_name = v.field_name
            if field_name in obj:
                try:
                    setattr(
                        instance,
                        k,
                        load_param_and_type_check(
                            obj[v.field_name], annotation, field_name
                        ),
                    )
                except ConfigError as e:
                    raise ConfigError(current_key_or_index=field_name, fromerr=e)
            else:
                if v.default_value is _missing:
                    raise ConfigError(f"{v.field_name} 缺少必填字段")
                setattr(instance, k, v.default_value)
        return instance
    else:
        raise ValueError(f"不支持的模版参数类型: {typ}")


def dump_param(obj):
    if isinstance(obj, JsonSchema):
        return {
            obj._fields[k].field_name: dump_param(v)
            for k, v in obj.__dict__.items()
            if not k.startswith("__")
        }
    else:
        # Not need to dump
        return obj


def get_plugin_config_and_version(
    plugin_name: str,
    schema: type[JsonSchemaT],
    default_vers: VERSION,
) -> tuple[JsonSchemaT, VERSION]:
    """
    获取插件配置文件及版本

    Args:
        plugin_name (str): 插件名
        schema (dict): 配置模版
        default (dict): 默认配置
        default_vers (tuple[int, int, int]): 默认版本

    Returns:
        tuple[dict[str, Any], tuple[int, int, int]]: 配置文件内容及版本
    """
    p = os.path.join(TOOLDELTA_PLUGIN_CFG_DIR, plugin_name)
    if not _jsonfile_exists(p):
        s = load_param_and_type_check({}, schema)
        defaultCfg = PLUGINCFG_DEFAULT.copy()
        defaultCfg["配置项"] = dump_param(s)
        defaultCfg["配置版本"] = ".".join([str(n) for n in default_vers])
        write_default_cfg_file(f"{p}.json", defaultCfg, force=True)
    cfg_get = get_cfg(p, PLUGINCFG_STANDARD_TYPE)
    cfg_vers = tuple(int(c) for c in cfg_get["配置版本"].split("."))
    VERSION_LENGTH = 3  # 版本长度
    if len(cfg_vers) != VERSION_LENGTH:
        raise ValueError("配置文件出错：版本出错")
    return load_param_and_type_check(cfg_get["配置项"], schema), cfg_vers
