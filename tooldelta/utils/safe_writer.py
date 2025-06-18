import json
import os
from typing import Any
from . import fmts

PathLike = str | os.PathLike[str]

def safe_write(filepath: PathLike, obj: Any, indent=2):
    """
    安全地写入文件, 防止文件在写入途中被强行中止。

    Args:
        filepath (TextIOWrapper): 文件路径
        obj (Any): 写入的 json 待序列化对象
    """
    retry_times = 0
    while 1:
        try:
            bak_name = str(filepath) + ".bak"
            content = json.dumps(obj, indent=indent, ensure_ascii=False)
            # 1. make backup
            with open(bak_name, "w", encoding="utf-8") as fp:
                fp.write(content)
            # Seemed unneccessary
            # # 2. write orig file
            # with open(filepath, "w", encoding="utf-8") as fp:
            #     fp.write(content)
            break
        except BaseException as err:
            # 防止写入过程中被退出, 导致文件只写了一半
            retry_times += 1
            if retry_times >= 50:
                fmts.print_err(f"文件第 50 次写入失败: {err}")
                raise
            fmts.print_war(f"文件在写入时遭到强行中止 ({err}), 重试第 {retry_times} 次")
            continue
    try:
        os.remove(filepath)
    except FileNotFoundError:
        pass
    os.rename(bak_name, filepath)
