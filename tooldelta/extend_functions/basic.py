from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .. import ToolDelta


class ExtendFunction:
    def __init__(self, frame: "ToolDelta"):
        self.frame = frame

    def when_activate(self): ...

    def when_console_cmd_reset(self):
        """控制台命令重置后的扩展钩子。"""
        return None
