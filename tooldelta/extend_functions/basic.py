from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .. import ToolDelta


class ExtendFunction:
    def __init__(self, frame: "ToolDelta"):
        self.frame = frame

    def when_activate(self): ...
