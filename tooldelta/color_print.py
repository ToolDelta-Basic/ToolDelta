"支持mc颜色代码的输出模块"

import datetime
import threading
import colorama

colorama.init(autoreset=True)

try:
    from .logger import publicLogger
except ImportError:
    pass

unicode = type("")


def simple_fmt(kw: dict, arg: str) -> str:
    """简单的字符串格式化

    Args:
        kw (dict): 颜色列表（key为颜色代码，value为颜色代码对应的颜色）
        arg (str): 需要格式化的字符串

    Returns:
        str: 格式化后的字符串
    """
    for k, v in kw.items():
        arg = arg.replace(k, str(v))
    return arg


class _Print:
    """输出状态栏

    Raises:
        AssertionError: 无法找到对应的颜色代码
    """
    INFO_NORMAL = "§f 信息 "
    INFO_WARN = "§6 警告 "
    INFO_ERROR = "§4 报错 "
    INFO_FAIL = "§c 失败 "
    INFO_SUCC = "§a 成功 "
    INFO_LOAD = "§d 加载 "
    STD_COLOR_LIST = [
        ["0", "#000000"],
        ["1", "#0000AA"],
        ["2", "#00AA00"],
        ["3", "#00AAAA"],
        ["4", "#AA0000"],
        ["5", "#AA00AA"],
        ["6", "#FFAA00"],
        ["7", "#AAAAAA"],
        ["8", "#555555"],
        ["9", "#5555FF"],
        ["a", "#55FF55"],
        ["b", "#55FFFF"],
        ["c", "#FF5555"],
        ["d", "#FF55FF"],
        ["e", "#FFFF55"],
        ["f", "#FFFFFF"],
        ["g", "#DDD605"],
        ["r", "/"],
    ]

    def __init__(self) -> None:
        "初始化"
        self.lock = threading.RLock()

    def __call__(self, text: str) -> None:
        "输出信息"
        with self.lock:
            self.print_inf(text)

    def simple_fmt(self, kw: dict, arg: str) -> str:
        """简单的字符串格式化

        Args:
            kw (dict): 颜色列表（key为颜色代码，value为颜色代码对应的颜色）
            arg (str): 需要格式化的字符串

        Returns:
            str: 格式化后的字符串
        """

        with self.lock:
            return simple_fmt(kw, arg)

    def colormode_replace(self, text: str, showmode=0) -> str:
        """颜色代码替换

        Args:
            text (str): 需要替换的字符串
            showmode (int, optional): 显示模式

        Returns:
            str: 替换后的字符串
        """
        with self.lock:
            # 1 = bg_color
            text = self._strike(text)
            return (
                simple_fmt(
                    {
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

    @staticmethod
    def align(text: str, length: int = 15) -> str:
        """对齐字符串

        Args:
            text (str): 需要对齐的字符串
            length (int, optional): 对齐长度

        Returns:
            str: 对齐后的字符串
        """
        l = len(text)
        for char in text:
            if not char.isascii():
                l += 1
        return text + " " * (length - l)

    @staticmethod
    def _strike(text: str) -> str:
        """删除线

        Args:
            text (str): 需要删除线的字符串

        Returns:
            str: 删除线后的字符串
        """

        text_ok = ""
        strikeMode = False
        i = 0
        while i < len(text):
            char = text[i]
            try:
                if char == "§":
                    if text[i + 1] == "s":
                        strikeMode = True
                        i += 2
                        continue
                    if text[i + 1] == "r":
                        strikeMode = False
            except IndexError:
                pass
            if strikeMode:
                text_ok += "\u0336" + char
            else:
                text_ok += char
            i += 1
        return text_ok

    def print_with_info(
        self, text: str, info: str = INFO_NORMAL, need_log: bool = True, **print_kwargs
    ):
        """输出带有信息的文本

        Args:
            text (str): 输出的文本
            info (str, optional): 输出的信息
            need_log (bool, optional): 是否需要记录日志
            **print_kwargs: 原print函数的参数

        Raises:
            AssertionError: 无法找到对应的颜色代码
        """
        with self.lock:
            if need_log:
                self.c_log(info, text)
            setNextColor = "§r"
            if "\n" in text:
                output_txts = []
                for text_line in str(text).split("\n"):
                    if "§" in text_line:
                        try:
                            n = text_line.rfind("§")
                            _setNextCol = text_line[n: n + 2]
                            if setNextColor == -1:
                                raise AssertionError
                            setNextColor = _setNextCol
                        except Exception:
                            pass
                    output_txts.append(
                        datetime.datetime.now().strftime("[%H:%M] ")
                        + self.colormode_replace(info, 7)
                        + " "
                        + self.colormode_replace(setNextColor + text_line)
                    )
                print("\n".join(output_txts), **print_kwargs)
            else:
                print(
                    datetime.datetime.now().strftime("[%H:%M] ")
                    + self.colormode_replace(info, 7)
                    + " "
                    + self.colormode_replace(text),
                    **print_kwargs,
                )

    def clean_print(self, text: str, **print_kwargs) -> None:
        """依照mc的颜色代码输出文本，可带有print函数的参数

        Args:
            text (str): 输出的文本
            **print_kwargs: 原print函数的参数
        """
        with self.lock:
            print(self.colormode_replace(text), **print_kwargs)

    def clean_fmt(self, text: str) -> str:
        """依照mc的颜色代码格式化文本

        Args:
            text (str): 需要格式化的文本

        Returns:
            str: 格式化后的文本
        """
        with self.lock:
            return self.colormode_replace(text)

    def print_err(self, text: str, **print_kwargs) -> None:
        """输出错误信息

        Args:
            text (str): 输出的文本
        """
        with self.lock:
            self.print_with_info(f"§c{text}", self.INFO_ERROR, **print_kwargs)

    def print_inf(self, text: str, **print_kwargs) -> None:
        """输出INDO信息

        Args:
            text (str): 输出的文本
        """
        with self.lock:
            self.print_with_info(f"{text}", self.INFO_NORMAL, **print_kwargs)

    def print_suc(self, text: str, **print_kwargs) -> None:
        """输出成功信息

        Args:
            text (str): 输出的文本
        """
        with self.lock:
            self.print_with_info(f"§a{text}", self.INFO_SUCC, **print_kwargs)

    def print_war(self, text: str, **print_kwargs) -> None:
        """输出警告信息

        Args:
            text (str): 输出的文本
        """
        with self.lock:
            self.print_with_info(f"§6{text}", self.INFO_WARN, **print_kwargs)

    def print_load(self, text: str, **print_kwargs) -> None:
        """输出加载信息

        Args:
            text (str): 输出的文本
        """
        with self.lock:
            self.print_with_info(f"§d{text}", self.INFO_LOAD, **print_kwargs)

    def fmt_info(self, text: str, info: str = "§f 信息 ") -> str:
        """格式化信息

        Args:
            text (str): 输出的文本
            info (str, optional): 输出的信息

        Raises:
            AssertionError: 无法找到对应的颜色代码

        Returns:
            str: 格式化后的信息
        """
        with self.lock:
            setNextColor = "§r"
            if "\n" in text:
                output_txts = []
                for text_line in str(text).split("\n"):
                    if "§" in text_line:
                        try:
                            n = text_line.rfind("§")
                            _setNextCol = text_line[n: n + 2]
                            if setNextColor == -1:
                                raise AssertionError
                            setNextColor = _setNextCol
                        except Exception:
                            pass
                    output_txts.append(
                        datetime.datetime.now().strftime("[%H:%M] ")
                        + self.colormode_replace(info, 7)
                        + " "
                        + self.colormode_replace(setNextColor + text_line)
                    )
                return "\n".join(output_txts)
            return (
                datetime.datetime.now().strftime("[%H:%M] ")
                + self.colormode_replace(info, 7)
                + " "
                + self.colormode_replace(text)
            )

    def c_log(self, inf: str, msg: str) -> None:
        """记录日志

        Args:
            inf (str): 信息
            msg (str): 记录的信息
        """
        with self.lock:
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
            for col, _ in self.STD_COLOR_LIST:
                col = "§" + col
                msg = msg.replace(col, "")
            for col, _ in self.STD_COLOR_LIST:
                col = "§" + col
                inf = inf.replace(col, "")
            inf = inf.replace(" ", "")
            publicLogger.log_in(msg, inf)


Print = _Print()
