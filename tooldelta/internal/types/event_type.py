from dataclasses import dataclass
from .player import Player


@dataclass
class BasicEvent:
    @classmethod
    def load(cls, /): ...


class Chat(BasicEvent):
    player: Player
    msg: str
