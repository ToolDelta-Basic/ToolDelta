import os
from typing import TYPE_CHECKING

from tooldelta.constants import TOOLDELTA_PLUGIN_DATA_DIR
from tooldelta.color_print import Print

if TYPE_CHECKING:
    from tooldelta import ToolDelta


class Plugin:
    "插件主类"

    name: str = ""
    "插件名"
    version = (0, 0, 1)
    "插件版本号"
    author: str = "?"
    "作者名"
    description = "..."
    "简介"

    __path_created__ = False

    def __init__(self, frame: "ToolDelta"):
        self.frame = frame
        self.game_ctrl = frame.get_game_control()

    @property
    def data_path(self) -> str:
        "该插件的数据文件夹路径 (调用时直接创建数据文件夹)"
        path = os.path.join(TOOLDELTA_PLUGIN_DATA_DIR, self.name)
        if not self.__path_created__:
            os.makedirs(path, exist_ok=True)
            self.__path_created__ = True
        return path

    def make_data_path(self):
        os.makedirs(os.path.join(TOOLDELTA_PLUGIN_DATA_DIR, self.name), exist_ok=True)
        self.__path_created__ = True

    def print(self, msg: str):
        Print.print_inf(f"{self.name}: {msg}")

    def format_data_path(self, *paths: str):
        return os.path.join(self.data_path, *paths)
