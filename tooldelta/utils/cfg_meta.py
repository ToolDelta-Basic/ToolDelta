import os
from types import GenericAlias, UnionType
from typing import Generic, TypeVar, Any, get_args
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
        if current_key_or_index != "":
            if fromerr:
                self.pos = [current_key_or_index, *fromerr.pos]
            else:
                self.pos = [current_key_or_index]
        else:
            self.pos = []

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
    """
    为 `JsonSchema` 模版类标注字段。

    Args:
        field_name (str): 模版字段对应的配置文件键名
        default: 该字段的默认值 (注意, 如果不填写的话, 生成配置文件时就不会生成关于它的默认配置)

    >>> class MyConfig(JsonSchema):
    ...     cfg_a: str = field("配置A")
    ...     cfg_b: int = field("配置B", default=350)
    ...
    >>> cfg = load_param_and_type_check({"配置A": "Hello world"}, MyConfig)
    >>> cfg.cfg_a
    "Hello world"
    >>> cfg.cfg_b
    350
    """
    return _Field(field_name, default)  # type: ignore


class JsonSchema:
    """
    配置文件模版类基类。所有配置模版类都必须继承它。如：
    >>> class MyConfig(JsonSchema):
    ...     cfg_a: int = field("配置A")
    ...     cfg_b: str = field("配置B")
    ...     cfg_c: str | int = field("配置C", "Hello dream")

    基本类型标注仅接受 `str`, `int`, `float`, `bool` 基本类型。
    你也可以使用 `str | int`, `list[float]` 这样的复合类型和 `JsonSchema` 嵌套。
    """

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if k not in self._fields:
                raise ValueError(f"设置默认配置时遇到未知字段 {k}")
            try:
                setattr(
                    self, k, load_param_and_type_check(v, self._fields[k]._annotation)
                )
            except ConfigError as e:
                raise ValueError("设置默认配置传参出错: " + e.msg)
        for k, v in self._fields.items():
            if k not in kwargs:
                if v.default_value is _missing:
                    raise ValueError(f'字段 "{k}" 缺失默认值')
                setattr(self, k, v.default_value)

    def __init_subclass__(cls) -> None:
        cls._annotations = cls.__annotations__
        cls._fields = {
            k: v(annotation)
            for k, v in cls.__dict__.items()
            if (annotation := cls._annotations.get(k)) and isinstance(v, _Field)
        }
        cls._checked = False
        _annotation_type_check(cls)


checkable_types = (str, int, float, bool, type(None))


def _get_cfg_type_name(typ) -> str:
    """转换类型为中文字符串

    Args:
        typ (Any): 类型

    Returns:
        str: 中文字符串
    """
    if isinstance(typ, UnionType):
        return " 或".join(_get_cfg_type_name(t) for t in get_args(typ))
    elif typ is Any:
        return "任意类型"
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


def _annotation_type_check(typ):
    if typ in checkable_types:
        return
    elif isinstance(typ, GenericAlias):
        # list[...] or dict[str, ...]
        orig = typ.__origin__
        args = get_args(typ)
        if typ.__origin__ is list:
            if len(args) != 1:
                raise ValueError("不支持的泛型类型个数, 最多只能为 1 个")
        elif typ.__origin__ is dict:
            if len(args) != 2:
                raise ValueError("不支持的泛型类型个数, 最多只能为 2 个")
            if args[0] is not str:
                raise ValueError("dict 泛型首项参数只能为 str")
            _annotation_type_check(args[1])
        else:
            raise ValueError(f"不支持的泛型类型: {orig}")
        _annotation_type_check(args[0])
    elif isinstance(typ, UnionType):
        for t in get_args(typ):
            _annotation_type_check(t)
    elif type(typ) is type and issubclass(typ, JsonSchema):
        if typ._checked:
            return
        for v in typ._annotations.values():
            _annotation_type_check(v)
        typ._checked = True
    elif typ is Any:
        return
    else:
        raise TypeError(f"不支持的类型注释 {typ}")


def load_param_and_type_check(obj, typ: type[T] | None, field_name: str = "") -> T:
    if typ in checkable_types:
        if isinstance(obj, int) and typ is float:
            return obj  # type: ignore
        if not isinstance(obj, typ):
            raise ConfigError(
                f"值 {obj} 类型错误, 需为 {_get_cfg_type_name(typ)}, 得到 {_get_cfg_type_name(type(obj))}",
                field_name,
            )
        return obj  # type: ignore
    elif isinstance(typ, UnionType):
        for t in get_args(typ):
            try:
                return load_param_and_type_check(obj, t)
            except ConfigError:
                pass
        raise ConfigError(
            f"值 {obj} 类型错误, 需为 {_get_cfg_type_name(typ)}, 得到 {_get_cfg_type_name(type(obj))}",
            field_name,
        )
    elif isinstance(typ, GenericAlias):
        # list[...]
        orig = typ.__origin__
        if orig is list:
            if not isinstance(obj, list):
                raise ConfigError(
                    f"值 {obj} 类型错误, 需为列表, 得到 {_get_cfg_type_name(type(obj))}",
                    field_name,
                )
            sub_type = get_args(typ)[0]
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
                    f"值 {obj} 类型错误, 需为json对象, 得到 {_get_cfg_type_name(type(obj))}",
                    field_name,
                )
            sub_type = get_args(typ)[1]
            dic = {}
            for k, v in obj.items():
                try:
                    dic[k] = load_param_and_type_check(v, sub_type)
                except ConfigError as e:
                    raise ConfigError(current_key_or_index=k, fromerr=e)
            return dic  # type: ignore
        else:
            raise ValueError(f"未知泛型类型 {typ}")
    elif type(typ) is type and issubclass(typ, JsonSchema):
        if not isinstance(obj, dict):
            raise ConfigError(
                f"值 {obj} 类型错误, 需为json, 得到 {_get_cfg_type_name(type(obj))}",
                field_name,
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
    elif typ is Any:
        return obj
    elif typ is None:
        if obj is not None:
            raise ConfigError(
                f"值 {obj} 类型错误, 需为null, 得到 {_get_cfg_type_name(type(obj))}"
            )
        return obj
    else:
        raise ValueError(f"不支持的模版参数类型: {typ}")


def dump_param(obj):
    if isinstance(obj, JsonSchema):
        return {
            obj._fields[k].field_name: dump_param(v)
            for k, v in obj.__dict__.items()
            if not k.startswith("__")
        }
    elif isinstance(obj, list):
        return [dump_param(v) for v in obj]
    elif isinstance(obj, dict):
        return {k: dump_param(v) for k, v in obj.items()}
    elif type(obj) in (str, int, float, bool, None):
        # Not need to dump
        return obj
    else:
        raise ValueError(f"Not support type to dump: {obj}")


def get_plugin_config_and_version(
    plugin_name: str,
    schema: type[JsonSchemaT],
    default_vers: VERSION,
) -> tuple[JsonSchemaT, VERSION]:
    """
    获取插件配置文件及版本

    Args:
        plugin_name (str): 插件名
        schema (type[JsonSchema]): 配置模版
        default (dict): 默认配置
        default_vers (tuple[int, int, int]): 默认版本

    Returns:
        tuple[dict[str, Any], tuple[int, int, int]]: 配置文件内容及版本
    """
    p = TOOLDELTA_PLUGIN_CFG_DIR / plugin_name
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
