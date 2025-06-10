import time
import json
import os
import copy
from typing import Any, TypeVar
from collections.abc import Callable
from threading import Lock, RLock

from .timer_events import timer_event
from .safe_writer import safe_write

PathLike = str | os.PathLike[str]
VT = TypeVar("VT")

tempjson_rw_lock = Lock()
tempjson_paths: dict[PathLike, "_jsonfile_status"] = {}


class _jsonfile_status:
    def __init__(
        self,
        path: PathLike,
        need_file_exists: bool,
        default: Any = None,
        unload_delay: float | None = None,
    ):
        self.path = path
        self.is_changed = False
        self.load_time = time.time()
        self.unload_delay = unload_delay
        self.lock = RLock()
        parent_dir = os.path.dirname(path)
        with self.lock:
            if parent_dir and not os.path.isdir(dp := os.path.dirname(path)):
                raise ValueError("文件夹: " + dp + " 路径不存在")
            if not need_file_exists and not os.path.isfile(path):
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(default, f, ensure_ascii=False)
                self.content = default
                self.is_changed = True
            else:
                with open(path, encoding="utf-8") as f:
                    self.content = json.load(f)

    def flush_time(self):
        self.load_time = time.time()

    def should_unload(self):
        if self.unload_delay is None:
            return False
        return time.time() - self.load_time > self.unload_delay

    def read(self, deepcopy: bool = True):
        self.flush_time()
        if deepcopy:
            return copy.deepcopy(self.content)
        else:
            return self.content

    def write(self, content):
        with self.lock:
            self.flush_time()
            self.is_changed = content != self.content
            self.content = content

    def save(self):
        with self.lock:
            if self.is_changed:
                safe_write(self.path, self.content)




def load_from_path(
    path: PathLike,
    need_file_exists: bool = True,
    default: Any = None,
    unload_delay: int | None = None,
) -> _jsonfile_status:
    """
    将 json 文件从磁盘加载到缓存区，以便快速读写.
    在缓存文件已加载的情况下，再使用一次该方法不会有任何作用.

    Args:
        path (str): 作为文件的磁盘内路径的同时也会作为在缓存区的虚拟路径
        needFileExists (bool, optional): 默认为 True, 为 False 时，若文件路径不存在，就会自动创建一个文件
        default (Any, optional): 默认为 None, 为 None 时，若文件路径不存在，就会自动创建一个文件，且写入默认值 null
        unload_delay (int, optional): 多久没有再进行读写操作时, 将其从缓存卸载


    Raises:
        err: 文件不存在时
    """
    if j := tempjson_paths.get(path):
        return j
    j = tempjson_paths[path] = _jsonfile_status(
        path, need_file_exists=need_file_exists, default=default, unload_delay=unload_delay
    )
    return j


def unload_to_path(path: PathLike) -> bool:
    """
    将 json 文件从缓存区卸载 (保存内容到磁盘), 之后不能再在缓存区对这个文件进行读写.
    在缓存文件已卸载的情况下，再使用一次该方法不会有任何作用，但是可以通过其返回的值来知道存盘有没有成功.

    Args:
        path (str): 文件的虚拟路径

    Returns:
        bool: 存盘是否成功
    """
    if (jsonf := tempjson_paths.get(path)) is not None:
        jsonf.save()
        del tempjson_paths[path]
        return True
    return False


def read(path: PathLike, deepcopy: bool = True):
    """对缓存区的该虚拟路径的文件进行读操作，返回一个深拷贝的 JSON 对象

    Args:
        path (str): 文件的虚拟路径

    Raises:
        Exception: json 路径未初始化，不能进行读取和写入操作

    Returns:
        list[Any] | dict[Any, Any] | Any: 该虚拟路径的 JSON
    """
    if jsonf := tempjson_paths.get(path):
        return jsonf.read(deepcopy=deepcopy)
    raise ValueError(f"json 路径未初始化，不能进行读取和写入操作: {path}")


def get(path: PathLike) -> Any:
    """
    直接获取缓存区的该虚拟路径的 JSON, 不使用 copy
    WARNING: 如果你不知道有什么后果，请老老实实使用`read(...)`而不是`get(...)`!

    Args:
        path (str): 文件的虚拟路径
    """
    if jsonf := tempjson_paths.get(path):
        return jsonf.read(deepcopy=False)
    raise ValueError(f"json 路径未初始化, 不能进行读取和写入操作: {path}")


def write(path: PathLike, obj: Any) -> None:
    """
    对缓存区的该虚拟路径的文件进行写操作，这将会覆盖之前的内容

    Args:
        path (str): 文件的虚拟路径
        obj (Any): 任何合法的 JSON 类型 例如 dict/list/str/bool/int/float
    """
    if jsonf := tempjson_paths.get(path):
        jsonf.write(obj)
    else:
        raise ValueError(f"json 路径未初始化, 不能进行读取和写入操作：{path}")


def load_and_read(
    path: PathLike,
    need_file_exists: bool = True,
    timeout: int = 60,
    default: Callable[[], VT] | VT = {},
) -> VT:
    """读取 json 文件并将其从磁盘加载到缓存区，以便一段时间内能快速读写.

    Args:
        path (str): 作为文件的磁盘内路径的同时也会作为在缓存区的虚拟路径
        needFileExists (bool, optional): 默认为 True, 为 False 时，若文件路径不存在，就会自动创建一个文件，且写入默认值 null
        timeout (int, optional): 多久没有再进行读取操作时卸载缓存
        default (() -> Any | Any, optional):

    Returns:
        Any: 该虚拟路径的 JSON
    """
    if path not in tempjson_paths.keys():
        load_from_path(
            path,
            need_file_exists,
            default() if callable(default) else default,
            timeout,
        )
    return read(path)


def load_and_write(
    path: PathLike, obj: Any, need_file_exists: bool = True, timeout: int = 60
) -> None:
    """写入 json 文件并将其从磁盘加载到缓存区，以便一段时间内能快速读写.

    Args:
        path (str): 作为文件的磁盘内路径的同时也会作为在缓存区的虚拟路径
        obj (Any): 任何合法的 JSON 类型 例如 dict/list/str/bool/int/float
        needFileExists (bool, optional): 默认为 True, 为 False 时，若文件路径不存在，就会自动创建一个文件，且写入默认值 null
        timeout (int, optional): 多久没有再进行读取操作时卸载缓存
    """
    if path not in tempjson_paths.keys():
        load_from_path(path, need_file_exists, default=obj, unload_delay=timeout)
    write(path, obj)


def cancel_change(path: str):
    "取消缓存 json 所做的更改，非必要情况请勿调用，你不知道什么时候会自动保存所做更改"
    tempjson_paths[path].is_changed = False


def flush(path: PathLike | None = None):
    """
    刷新单个/全部JSON缓存区的缓存文件, 存入磁盘

    Args:
        path (str | None, optional): 文件虚拟路径, 默认全部存盘
    """
    if path:
        if tmpjson := tempjson_paths.get(path):
            tmpjson.save()
        else:
            raise ValueError(f"json 路径未初始化, 不能 flush: {path}")
    else:
        save_all()


def get_tmps() -> dict:
    "获取缓存区中所有临时文件"
    return tempjson_paths.copy()


@timer_event(30, "缓冲区 json 文件自动保存")
def jsonfile_auto_save():
    save_all()


def save_all():
    with tempjson_rw_lock:
        for k, v in tempjson_paths.copy().items():
            v.save()
            if v.should_unload():
                del tempjson_paths[k]


def reset():
    tempjson_paths.clear()
