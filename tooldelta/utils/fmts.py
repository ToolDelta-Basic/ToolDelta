"支持 mc 颜色代码的输出模块"

import datetime
import threading
import re
import colorama
from typing import Any

from .logger import publicLogger

colorama.init(autoreset=True)
MC_COLOR_CODE_REG = re.compile("§.")

INFO_NORMAL = "§f 信息 "
INFO_WARN = "§6 警告 "
INFO_ERROR = "§4 报错 "
INFO_FAIL = "§c 失败 "
INFO_SUCC = "§a 成功 "
INFO_LOAD = "§d 加载 "
print_lock = threading.RLock()

_original_print = print


def simple_fmt(kw: dict[str, Any], sub: str) -> str:
    """
    快速将字符串内按照给出的 dict 的键值对替换掉内容.

    参数:
        kw: Dict[str, Any], 键值对应替换的内容
        *args: str, 需要被替换的字符串

    示例:
        >>> my_color = "red"; my_item = "apple"
        >>> kw = {"[颜色]": my_color, "[物品]": my_item}
        >>> SimpleFmt(kw, "I like [颜色] [物品].")
        I like red apple.
    """
    for k, v in kw.items():
        if k in sub:
            sub = sub.replace(k, str(v))
    return sub


def colormode_replace(text: str, showmode=0) -> str:
    """颜色代码替换

    Args:
        text (str): 需要替换的字符串
        showmode (int, optional): 显示模式

    Returns:
        str: 替换后的字符串
    """
    # 1 = bg_color
    text = _strike(text)
    return (
        simple_fmt(
            {
                "§0": f"\033[{showmode};37;90m",
                "§1": f"\033[{showmode};37;34m",
                "§2": f"\033[{showmode};37;32m",
                "§3": f"\033[{showmode};37;36m",
                "§4": f"\033[{showmode};37;31m",
                "§5": f"\033[{showmode};37;35m",
                "§6": f"\033[{showmode};37;33m",
                "§7": f"\033[{showmode};37;90m",
                "§8": f"\033[{showmode};37;2m",
                "§9": f"\033[{showmode};37;94m",
                "§a": f"\033[{showmode};37;92m",
                "§b": f"\033[{showmode};37;96m",
                "§c": f"\033[{showmode};37;91m",
                "§d": f"\033[{showmode};37;95m",
                "§e": f"\033[{showmode};37;93m",
                "§f": f"\033[{showmode};37;1m",
                "§r": "\033[0m",
                "§u": "\033[4m",
                "§l": "\033[1m",
            },
            text,
        )
        + "\033[0m"
    )


def align(text: str, length: int = 15) -> str:
    """对齐字符串

    Args:
        text (str): 需要对齐的字符串
        length (int, optional): 对齐长度

    Returns:
        str: 对齐后的字符串
    """
    text_length = len(text)
    for char in text:
        if not char.isascii():
            text_length += 1
    return text + " " * (length - text_length)


def _strike(text: str) -> str:
    """删除线
    对于Unicode字符不适用

    Args:
        text (str): 需要删除线的字符串

    Returns:
        str: 删除线后的字符串
    """
    text_ok = ""
    strike_mode = False
    i = 0
    while i < len(text):
        char = text[i]
        try:
            if char == "§":
                if text[i + 1] == "S":
                    strike_mode = True
                    i += 2
                    continue
                if text[i + 1] == "r":
                    strike_mode = False
        except IndexError:
            pass
        if strike_mode:
            text_ok += "\u0336" + char
        else:
            text_ok += char
        i += 1
    return text_ok


def print_gradient(text, start_rgb, end_rgb):
    """使用ANSI转义码打印渐变文字"""
    result = []
    length = len(text)

    for i in range(length):
        ratio = i / (length - 1) if length > 1 else 0
        r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * ratio)
        g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * ratio)
        b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * ratio)
        result.append(f"\033[38;2;{r};{g};{b}m{text[i]}")

    return "".join(result) + "\033[0m"


def print_with_info(
    text: str, info: str = INFO_NORMAL, need_log: bool = True, **print_kwargs
):
    """输出带有信息的文本

    Args:
        text (str): 输出的文本
        info (str, optional): 输出的信息
        need_log (bool, optional): 是否需要记录日志
        **print_kwargs: 原 print 函数的参数

    Raises:
        AssertionError: 无法找到对应的颜色代码
    """

    if need_log:
        c_log(info, text)
    set_next_color = "§r"
    if "\n" in text:
        output_txts = []
        for text_line in str(text).split("\n"):
            if "§" in text_line:
                try:
                    n = text_line.rfind("§")
                    _set_next_col_value = text_line[n : n + 2]
                    set_next_color = _set_next_col_value
                except Exception as exc:
                    string = "输出信息时出现错误:\n"
                    string += "    %s\n"
                    string += "    原信息: %s"
                    _original_print(string % (str(exc), text))
            output_txts.append(
                datetime.datetime.now().strftime("%H:%M ")
                + colormode_replace(info, 7)
                + " "
                + colormode_replace(set_next_color + text_line)
            )
        content = "\n".join(output_txts)
        with print_lock:
            _original_print(content, **print_kwargs)
    else:
        content = (
            datetime.datetime.now().strftime("%H:%M ")
            + colormode_replace(info, 7)
            + " "
            + colormode_replace(text)
        )
        with print_lock:
            _original_print(
                content,
                **print_kwargs,
            )


def clean_print(text: str, **print_kwargs) -> None:
    """依照 mc 的颜色代码输出文本，可带有 print 函数的参数

    Args:
        text (str): 输出的文本
        **print_kwargs: 原 print 函数的参数
    """
    with print_lock:
        _original_print(colormode_replace(text), **print_kwargs)


def clean_fmt(text: str) -> str:
    """依照 mc 的颜色代码格式化文本

    Args:
        text (str): 需要格式化的文本

    Returns:
        str: 格式化后的文本
    """
    return colormode_replace(text)


def print(*args):
    print_inf(" ".join(str(i) for i in args))


def print_err(text: str, **print_kwargs) -> None:
    """输出错误信息

    Args:
        text (str): 输出的文本
    """
    print_with_info(f"§c{text}", INFO_ERROR, **print_kwargs)


def print_inf(text: str, **print_kwargs) -> None:
    """输出 INFO 信息

    Args:
        text (str): 输出的文本
    """
    print_with_info(f"{text}", INFO_NORMAL, **print_kwargs)


def print_suc(text: str, **print_kwargs) -> None:
    """输出成功信息

    Args:
        text (str): 输出的文本
    """
    print_with_info(f"§a{text}", INFO_SUCC, **print_kwargs)


def print_war(text: str, **print_kwargs) -> None:
    """输出警告信息

    Args:
        text (str): 输出的文本
    """
    print_with_info(f"§6{text}", INFO_WARN, **print_kwargs)


def print_load(text: str, **print_kwargs) -> None:
    """输出加载信息

    Args:
        text (str): 输出的文本
    """
    with print_lock:
        print_with_info(f"§d{text}", INFO_LOAD, **print_kwargs)


def fmt_info(text: str, info: str = "§f 信息 ") -> str:
    """格式化信息

    Args:
        text (str): 输出的文本
        info (str, optional): 输出的信息

    Raises:
        AssertionError: 无法找到对应的颜色代码

    Returns:
        str: 格式化后的信息
    """
    with print_lock:
        nextcolor = "§r"
        if "\n" in text:
            output_txts = []
            for text_line in str(text).split("\n"):
                if "§" in text_line:
                    try:
                        n = text_line.rfind("§")
                        _setnextcol = text_line[n : n + 2]
                        if nextcolor == -1:
                            raise AssertionError
                        nextcolor = _setnextcol
                    except Exception:
                        pass
                output_txts.append(
                    datetime.datetime.now().strftime("%H:%M ")
                    + colormode_replace(info, 7)
                    + " "
                    + colormode_replace(nextcolor + text_line)
                )
            return "\n".join(output_txts)
        return (
            datetime.datetime.now().strftime("%H:%M ")
            + colormode_replace(info, 7)
            + " "
            + colormode_replace(text)
        )


def c_log(inf: str, msg: str) -> None:
    """记录日志

    Args:
        inf (str): 信息
        msg (str): 记录的信息
    """
    with print_lock:
        for _g, _s in [
            ("§6 警告 ", "WARN"),
            ("§a 成功 ", "INFO"),
            ("§f 信息 ", "INFO"),
            ("§c 失败 ", "FAIL"),
            ("§4 报错 ", "ERROR"),
        ]:
            if inf == _g:
                inf = _s
                break
        msg = MC_COLOR_CODE_REG.sub("", msg)
        publicLogger.log_in(msg, inf.strip())


def get_ansi_rgb(r: int, g: int, b: int):
    return f"\033[38;2;{r};{g};{b}m"


def ansi_cls():
    _original_print("\033[2J")


def ansi_home():
    _original_print("\033[H")


def ansi_locate(x: int, y: int):
    _original_print(f"\033[{x};{y}H")


def ansi_save_screen():
    _original_print("\033[?47h")


def ansi_load_screen():
    _original_print("\033[?47l")
