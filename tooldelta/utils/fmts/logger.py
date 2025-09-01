import logging
import re
import os
from datetime import datetime
from enum import IntEnum
from rich.logging import RichHandler
from rich.console import Console
from rich.markup import escape
from rich.errors import MarkupError

enable_logger = False

re_color = re.compile(r"§([0-9a-z])")

color_map = {
    "0": "000000",
    "1": "0000AA",
    "2": "00AA00",
    "3": "00AAAA",
    "4": "AA0000",
    "5": "AA00AA",
    "6": "FFAA00",
    "7": "AAAAAA",
    "8": "555555",
    "9": "5555FF",
    "a": "55FF55",
    "b": "55FFFF",
    "c": "FF5555",
    "d": "FF55FF",
    "e": "FFFF55",
    "f": "FFFFFF",
    "g": "DDD605",
    "h": "E3D4D1",
    "i": "CECACA",
    "j": "443A3B",
    "m": "971607",
    "n": "B4684D",
    "o": "DEB12D",
    "p": "DEB12D",
    "q": "47A036",
    "r": "9A5CC6",
    "s": "2CBAA8",
    "t": "21497B",
    "u": "9A5CC6",
    "v": "EB7114",
}


class ExtraLevel(IntEnum):
    SUCCESS = 25
    LOADING = 26


custom_levels = {
    "INFO": (" 信息 ", "FFFFFF"),
    "WARNING": (" 警告 ", "FFFF00"),
    "ERROR": (" 报错 ", "FF2222"),
    "DEBUG": (" 调试 ", "00FFFF"),
    "CRITICAL": (" 严重 ", "FF0000"),
    "成功": (" 成功 ", "00FF00"),
    "加载": (" 加载 ", "FF00FF"),
}


class DailyFileHandler(logging.FileHandler):
    """
    自定义文件处理器，每天创建一个新的日志文件
    """

    def __init__(self, log_dir: str = "日志文件", filename_fmt: str = "%Y-%m-%d.log"):
        os.makedirs(log_dir, exist_ok=True)
        self.log_dir = log_dir
        self.current_day = 0
        self.filename_fmt = filename_fmt
        super().__init__(self._get_current_filename(), encoding="utf-8")

    def _get_current_filename(self):
        filename = os.path.join(
            self.log_dir, datetime.now().strftime(self.filename_fmt)
        )
        return filename

    def _is_new_day(self):
        return self.current_day != datetime.now().day

    def _update_day(self):
        self.current_day = datetime.now().day

    def emit(self, record):
        if self._is_new_day():
            self._update_day()
            self.close()
            new_filename = self._get_current_filename()
            self.baseFilename = new_filename
            self.stream = self._open()
        super().emit(record)


class CustomPrefixRichHandler(RichHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, markup=True, **kwargs)
        self.highlighter = None

    def get_level_text(self, record):
        level_name = record.levelname
        # 可以根据需要自定义任何文本
        disp_text, disp_color = custom_levels.get(level_name, (level_name, "777777"))
        return f"[#000000 on #{disp_color}]{disp_text}[/#000000 on #{disp_color}]"

    def emit(self, record):
        record.msg = color_to_rich(record.getMessage())
        try:
            super().emit(record)
        except MarkupError:
            record.msg = escape(record.msg)
            super().emit(record)


def color_to_rich(text: str):
    last_color = ""
    bold = False

    def repl_cb(match: re.Match[str]) -> str:
        nonlocal bold, last_color
        color_char = match.group()[1]
        if color_char == "r":
            if bold:
                bold = False
                return f"[/bold {last_color}]"
            elif last_color:
                return f"[/#{last_color}]"
            else:
                return ""
        elif color_char == "l":
            bold = True
            return "[bold]"
        elif m := color_map.get(color_char):
            last_color = m
            return f"[#{m}]"
        else:
            return ""

    return re_color.sub(repl_cb, text)


console = Console(highlight=False)
rich_handler = CustomPrefixRichHandler(console=console, show_time=True, show_path=False)
logging.addLevelName(ExtraLevel.SUCCESS, "成功")
logging.addLevelName(ExtraLevel.LOADING, "加载")
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="%H:%M",
    handlers=[
        rich_handler,
    ],
)


def init_file_logger():
    daily_file_handler = DailyFileHandler()
    file_formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s", datefmt="[%X]"
    )
    daily_file_handler.setFormatter(file_formatter)
    logging.getLogger().removeHandler(rich_handler)
    logging.getLogger().addHandler(daily_file_handler)
    # 使其优先级高于 rich_handler
    logging.getLogger().addHandler(rich_handler)


def switch_logger(enabled: bool):
    global enable_logger
    enable_logger = enabled
    if enabled:
        init_file_logger()
