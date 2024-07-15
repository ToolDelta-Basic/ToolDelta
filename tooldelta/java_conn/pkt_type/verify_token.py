from dataclasses import dataclass
from typing import Any
import ujson

@dataclass
class VerifyTokenBuild:
    pkt_id: int
    type: str
    data: str
    build: str
    def __init__(self, data: str) -> None:
        self.pkt_id = 1
        self.type = "verify_token"
        self.data = data
        self.build = ujson.dumps({"pkt_id": self.pkt_id, "type": self.type, "data": self.data, "paramTypes": ["int", "string", "string"], "paramValues": [self.pkt_id, self.type, self.data]})

class VerifyTokenResult:
    pkt_id: int
    type: str
    data: str
    result: str
    def __init__(self, data: bool) -> None:
        self.pkt_id = 1
        self.type = "verify_token"
        self.data = str(data)
        self.result = ujson.dumps({"pkt_id": self.pkt_id, "type": self.type, "data": self.data, "paramTypes": ["int", "string", "string"], "paramValues": [self.pkt_id, self.type, self.data]})

def handlePacket(message: Any, client, server, token, sign_token) -> VerifyTokenResult:
    try:
        if message["data"] == token:
            sign_token[token]["client"].append(client)
            return VerifyTokenResult(True)
        else:
            return VerifyTokenResult(False)
    except Exception as err:
        return VerifyTokenResult(False)