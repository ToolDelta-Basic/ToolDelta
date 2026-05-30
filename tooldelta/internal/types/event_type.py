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
class Death(BasicEvent):
    player: Player
    death_type: str

@dataclass
class Attack(BasicEvent):
    origin_player: Player
    target_player: Player
    weapon_name: str

@dataclass
class InternalBroadcast(BasicEvent):
    evt_name: str
    data: Any

@dataclass
class FrameExit(BasicEvent):
    signal: int
    reason: str
