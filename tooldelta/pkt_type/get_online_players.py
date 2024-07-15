from dataclasses import dataclass
from typing import Any, Collection
import ujson

@dataclass
class GetOnlinePlayers:
    player_name: str
    player_entity_id: int
    player_is_op: bool

    def __init__(self, player_name: str = "", player_entity_id: int = -1, player_is_op: bool = False) -> None:
        self.player_name = player_name
        self.player_entity_id = player_entity_id
        self.player_is_op = player_is_op

@dataclass
class GetOnlinePlayersBuild:
    pkt_id: int
    type: str
    data: str
    build: str

    def __init__(self) -> None:
        self.pkt_id = 5
        self.type = "get_online_players"
        self.data = ""
        self.build = ujson.dumps({
            "pkt_id": self.pkt_id,
            "type": self.type,
            "data": self.data,
            "paramTypes": ["int", "string", "string"],
            "paramValues": [self.pkt_id, self.type, self.data]
        })

class GetOnlinePlayersResult:
    pkt_id: int
    type: str
    data: str
    result: str

    def __init__(self, data) -> None:
        self.pkt_id = 5
        self.type = "get_online_players"
        self.data = str(data)
        self.result = ujson.dumps({
            "pkt_id": self.pkt_id,
            "type": self.type,
            "data": self.data,
            "paramTypes": ["int", "string", "string"],
            "paramValues": [self.pkt_id, self.type, self.data]
        })

def handlePacket(message: Any, client, server, token, sign_token) -> GetOnlinePlayersResult:
    data: list = message["data"]
    players: list[GetOnlinePlayers] = []
    for player in data:
        player = ujson.loads(player)
        player_name = list(player)[0]
        player_entity_id = player[player_name]["PlayerEntityId"]
        player_is_op = player[player_name]["PlayerIsOp"]
        players.append(GetOnlinePlayers(player_name, player_entity_id, player_is_op))

    return GetOnlinePlayersResult(True)
