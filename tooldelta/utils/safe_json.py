import json
import os
from typing import Any
from io import TextIOWrapper

from ..constants import TOOLDELTA_PLUGIN_DATA_DIR


def safe_json_dump(obj: Any, fp: TextIOWrapper | str, indent=2) -> None:
    """将一个 json 对象写入一个文件，会自动关闭文件读写接口.

    Args:
        obj (str | dict | list): JSON 对象
        fp (Any): open(...) 打开的文件读写口 或 文件路径
    """
    if isinstance(fp, str):
        with open(fp, "w", encoding="utf-8") as file:
            file.write(json.dumps(obj, indent=indent, ensure_ascii=False))
    else:
        with fp:
            fp.write(json.dumps(obj, indent=indent, ensure_ascii=False))


def safe_json_load(fp: TextIOWrapper | str) -> Any:
    """从一个文件读取 json 对象，会自动关闭文件读写接口.

    Args:
        fp (TextIOWrapper | str): open(...) 打开的文件读写口 或文件路径

    Returns:
        dict | list: JSON 对象
    """
    if isinstance(fp, str):
        with open(fp, encoding="utf-8") as file:
            return json.load(file)
    with fp as file:
        return json.load(file)


class DataReadError(json.JSONDecodeError):
    """读取数据时发生错误"""


def read_from_plugin(plugin_name: str, file: str, default: dict | None = None) -> Any:
    """从插件数据文件夹读取一个 json 文件，会自动创建文件夹和文件.

    Args:
        plugin_name (str): 插件名
        file (str): 文件名
        default (dict, optional): 默认值，若文件不存在则会写入这个默认值

    Raises:
        DataReadError: 读取数据时发生错误
        err: 读取文件路径时发生错误

    Returns:
        dict | list: JSON 对象
    """
    if file.endswith(".json"):
        file = file[:-5]
    filepath = os.path.join(TOOLDELTA_PLUGIN_DATA_DIR, plugin_name, f"{file}.json")
    os.makedirs(os.path.join(TOOLDELTA_PLUGIN_DATA_DIR, plugin_name), exist_ok=True)
    try:
        if default is not None and not os.path.isfile(filepath):
            with open(filepath, "w") as f:
                safe_json_dump(default, f)
            return default
        with open(filepath, encoding="utf-8") as f:
            res = safe_json_load(f)
        return res
    except json.JSONDecodeError as err:
        # 判断是否有 msg.doc.pos 属性
        raise DataReadError(err.msg, err.doc, err.pos)


def write_to_plugin(plugin_name: str, file: str, obj: Any, indent=4) -> None:
    """将一个 json 对象写入插件数据文件夹，会自动创建文件夹和文件.

    Args:
        plugin_name (str): 插件名
        file (str): 文件名
        obj (str | dict[Any, Any] | list[Any]): JSON 对象
    """
    os.makedirs(f"{TOOLDELTA_PLUGIN_DATA_DIR}/{plugin_name}", exist_ok=True)
    with open(
        f"{TOOLDELTA_PLUGIN_DATA_DIR}/{plugin_name}/{file}.json", "w", encoding="utf-8"
    ) as f:
        safe_json_dump(obj, f, indent=indent)
