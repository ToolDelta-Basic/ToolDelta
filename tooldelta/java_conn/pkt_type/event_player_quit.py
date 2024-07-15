from dataclasses import dataclass
from typing import Any, Collection
import ujson

@dataclass
class EventPlayerQuitPlayer:
    player_is_op: bool
    player_level: int
    player_name: str
    player_address: str
    player_allow_flight: bool
    player_exp: float
    player_health_scale: float
    player_is_flying: bool
    player_is_health_scaled: bool
    player_is_sleeping: bool
    player_entity_id: int
    player_game_mode: str
    player_height: float

    def __init__(self, player_is_op: bool = False, player_level: int = -1, player_name: str = "", player_address: str = "", player_allow_flight: bool = False, player_exp: float = 0.0, player_health_scale: float = 0.0, player_is_flying: bool = False, player_is_health_scaled: bool = False, player_is_sleeping: bool = False, player_entity_id: int = -1, player_game_mode: str = "", player_height: float = 0.0) -> None:
        self.player_is_op = player_is_op
        self.player_level = player_level
        self.player_name = player_name
        self.player_address = player_address        
        self.player_allow_flight = player_allow_flight
        self.player_exp = player_exp
        self.player_health_scale = player_health_scale
        self.player_is_flying = player_is_flying
        self.player_is_health_scaled = player_is_health_scaled
        self.player_is_sleeping = player_is_sleeping
        self.player_entity_id = player_entity_id
        self.player_game_mode = player_game_mode
        self.player_height = player_height

@dataclass
class EventPlayerQuitBuild:
    pkt_id: int
    type: str
    data: EventPlayerQuitPlayer
    build: str

    def __init__(self, data) -> None:
        self.pkt_id = 4
        self.type = "event_player_quit"
        self.data = data
        self.build = ujson.dumps({
            "pkt_id": self.pkt_id,
            "type": self.type,
            "data": self.data,
            "paramTypes": ["int", "string", "string"],
            "paramValues": [self.pkt_id, self.type, self.data]
        })

class EventPlayerQuitResult:
    pkt_id: int
    type: str
    data: str
    result: str

    def __init__(self, data) -> None:
        self.pkt_id = 4
        self.type = "event_player_quit"
        self.data = str(data)
        self.result = ujson.dumps({
            "pkt_id": self.pkt_id,
            "type": self.type,
            "data": self.data,
            "paramTypes": ["int", "string", "string"],
            "paramValues": [self.pkt_id, self.type, self.data]
        })

def handlePacket(message: Any, client, server, token, sign_token) -> EventPlayerQuitResult:
    message["data"] = ujson.loads(message["data"])
    return EventPlayerQuitResult(True)
