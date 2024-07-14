from dataclasses import dataclass
from typing import Any, Collection
import ujson

@dataclass
class EventPlayerJoinPlayer:
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
class EventPlayerJoinBuild:
    """
        CoreVersionBuild: 请求Core版本号
    """
    pkt_id: int
    type: str
    data: EventPlayerJoinPlayer
    build: str

    def __init__(self, data) -> None:
        self.pkt_id = 3
        self.type = "core_version"
        self.data = data
        self.build = ujson.dumps({
            "pkt_id": self.pkt_id,
            "type": self.type,
            "data": self.data,
            "paramTypes": ["int", "string", "string"],
            "paramValues": [self.pkt_id, self.type, self.data]
        })

class EventPlayerJoinResult:
    """
        EventPlayerJoinResult: 玩家加入服务器返回结果
    """
    pkt_id: int
    type: str
    success: bool
    result: str

    def __init__(self, success) -> None:
        self.pkt_id = 3
        self.type = "event_player_join"
        self.success = success
        self.result = ujson.dumps({
            "pkt_id": self.pkt_id,
            "type": self.type,
            "success": self.success,
            "paramTypes": ["int", "string", "bool"],
            "paramValues": [self.pkt_id, self.type, self.success]
        })

def handlePacket(message: Any, client, server, token, sign_token) -> EventPlayerJoinResult:
    """
        Returns: EventPlayerJoinResult
        处理客户端发来的玩家加入事件的玩家信息
    """
    message["data"] = ujson.loads(message["data"])
