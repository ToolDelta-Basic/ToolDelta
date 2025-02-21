from dataclasses import dataclass
from .player import Player


@dataclass
class Chat:
    player: Player
    msg: str
