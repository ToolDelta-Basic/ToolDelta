from typing import Any
from dataclasses import dataclass
from .player import Player


class BasicEvent:
    @classmethod
    def load(cls, /): ...

@dataclass
class Chat(BasicEvent):
    player: Player
    msg: str

@dataclass
class InternalBroadcast(BasicEvent):
    evt_name: str
    data: Any

@dataclass
class FrameExit(BasicEvent):
    signal: int
    reason: str
