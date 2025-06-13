"""提供了一些实用方法的类"""

import re
import threading
from typing import Any, TypeVar
from collections.abc import Callable
import uuid

from .fmts import simple_fmt, print_war

__all__ = [
    "create_desperate_attr_class",
    "create_result_cb",
    "fill_list_index",
    "fuzzy_match",
    "remove_mc_color_code",
    "simple_assert",
    "simple_fmt",
    "split_list",
    "to_plain_name",
    "to_player_selector",
    "try_convert",
    "try_int",
]
MC_COLOR_CODE_REG = re.compile("§.")
FACTORY_TYPE = TypeVar("FACTORY_TYPE")
VT = TypeVar("VT")


def simple_assert(cond: Any, exc: Any) -> None:
    """相当于 assert cond, 但是可以自定义引发的异常的类型"""
    if not cond:
        raise exc


def try_int(arg: Any) -> int | None:
    """尝试将提供的参数化为 int 类型并返回，否则返回 None"""
    try:
        return int(arg)
    except Exception:
        return None


def try_convert(
    arg: Any, factory: Callable[[Any], FACTORY_TYPE]
) -> FACTORY_TYPE | None:
    """
    尝试将提供的参数交给传入的 factory 处理并返回

    Args:
        arg (Any): 参数
        factory (Callable[[Any], factory_type]): 处理器方法

    Returns:
        factory_type | None: 处理结果, 遇到 ValueError 则返回 None

    >>> try_convert("4.5", float)
    4.5
    >>> print(try_convert("3", bool))
    None
    """
    try:
        return factory(arg)
    except Exception:
        return None


def fuzzy_match(lst: list[str], sub: str, ignore_caps = True) -> list[str]:
    """
    模糊匹配列表内的字符串，可以用在诸如模糊匹配玩家名的用途

    参数:
        lst: list, 字符串列表
        sub: str, 需要匹配的字符串
        ignore_caps (bool, optional): 是否忽略大小写. Defaults to True.
    返回:
        list, 匹配结果
    """
    res = []
    if ignore_caps:
        for i in lst:
            if sub.lower() in i.lower():
                res.append(i)
    else:
        for i in lst:
            if sub in i:
                res.append(i)
    return res


def split_list(lst: list[VT], length: int) -> list[list[VT]]:
    """
    将列表进行块分割

    Args:
        lst (list[VT]): 传入列表
        length (int): 分割的单个列表的长度

    Returns:
        list[list[VT]]: 传出的被分割的列表
    """
    return [lst[i : i + length] for i in range(0, len(lst), length)]


def fill_list_index(lst: list[VT], default: list[VT]):
    """
    使用默认值填充列表。

    Args:
        lst (list[VT]): 待填充列表
        default (list[VT]): 默认的填充值 (补全待填充列表)
    """
    if len(lst) < len(default):
        lst.extend(default[len(lst) :])


def remove_mc_color_code(string: str):
    return MC_COLOR_CODE_REG.sub("", string)


def to_plain_name(name: str) -> str:
    """
    去除 网易版 Minecraft 的名字中的颜色代码
    可用于将 VIP 玩家名 转换为普通玩家名

    Args:
        name (str): 玩家名

    Returns:
        str: 去除颜色代码后的名字
    """
    if "§" in name:
        name = remove_mc_color_code(name)
    if name.count("<") > 1:
        # <<VIP名><玩家名>> -> 玩家名
        cached_str = ""
        words = []
        for char in name:
            if char == "<":
                cached_str = ""
            elif char == ">":
                words.append(cached_str)
            else:
                cached_str += char
        return words[-1]
    elif name.startswith("<") and name.endswith(">"):
        # <玩家名> -> 玩家名
        return name[1:-1]
    return name


def to_player_selector(playername: str) -> str:
    """
    将玩家名转换为目标选择器.
    >>> to_player_selector("123坐端正")
    '@a[name="123坐端正"]'
    >>> to_player_selector('@a[name="123坐端正"]') # 已有选择器不会再套选择器
    '@a[name="123坐端正"]'

    Args:
        playername (str): 玩家名

    Returns:
        str: 含玩家名的目标选择器
    """
    if not playername.startswith("@"):
        return f'@a[name="{playername}"]'
    else:
        # 很可能这就已经是目标选择器了
        return playername


def create_result_cb(typechecker: type[VT] = object):
    """
    获取一对回调锁
    Args:
        typechecker (type[VT], optional): 设置类型检测时回调函数返回值的类型, 无实际作用, Defaults to type[object].

    ```
    getter, setter = create_result_cb(str)

    cbs[special_id] = setter
    # 在这边等待回调...
    result = getter()

    # 与此同时, 在另一边...
    getting_data: str = ...
    if special_id in cbs.keys():
        cbs[special_id](getting_data)

    ```
    """
    ret: list[VT | None] = [None]
    lock = threading.Lock()
    lock.acquire()

    def getter(timeout=60.0) -> VT | None:
        lock.acquire(timeout=timeout)
        return ret[0]

    def setter(s: VT):
        ret[0] = s
        lock.release()

    return getter, setter

def parse_uuid(ud: str | bytes | uuid.UUID) -> uuid.UUID:
    if isinstance(ud, str):
        return uuid.UUID(ud)
    elif isinstance(ud, uuid.UUID):
        return ud
    elif isinstance(ud, bytes):
        return uuid.UUID(bytes=ud)
    else:
        raise ValueError(f"Invalid UUID type: {type(ud).__name__}")

def validate_uuid(ud: str | bytes | uuid.UUID) -> str:
    if isinstance(ud, str):
        return ud
    elif isinstance(ud, bytes):
        return str(uuid.UUID(bytes=ud))
    elif isinstance(ud, uuid.UUID):
        return str(ud)
    else:
        raise ValueError(f"Invalid UUID type: {type(ud).__name__}")


class DesperateFuncClass:
    def __init__(self):
        self._desperate_warn = False

    def __getattribute__(self, attr):
        if not object.__getattribute__(self, "_desperate_warn"):
            self._desperate_warn = True
            print_war(f"{type(self).__name__} 已被弃用。请查看文档以使用新方法。")
            #time.sleep(3)
        return object.__getattribute__(self, attr)


def create_desperate_attr_class(class_name, attrs: list[Callable | DesperateFuncClass]):
    new_class = type(
        class_name,
        (DesperateFuncClass,),
        {
            (f.__name__ if callable(f) else type(f).__name__): (
                staticmethod(f) if callable(f) else f
            )
            for f in attrs
        },
    )
    return new_class()
