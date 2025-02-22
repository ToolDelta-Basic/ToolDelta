from dataclasses import dataclass
from .player import Player


class BasicEvent:
    @classmethod
    def load(cls, /): ...

@dataclass
class Chat(BasicEvent):
    player: Player
    msg: str
