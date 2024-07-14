from dataclasses import dataclass
from typing import Any
import ujson

@dataclass
class VerifyTokenBuild:
    """
        Args: None
        VerifyTokenBuild: 验证Token
    """
    pkt_id: int
    type: str
    token: str
    build: str
    def __init__(self, token: str) -> None:
        self.pkt_id = 1
        self.type = "verify_token"
        self.token = token
        self.build = ujson.dumps({"pkt_id": self.pkt_id, "type": self.type, "token": self.token, "paramTypes": ["int", "string", "string"], "paramValues": [self.pkt_id, self.type, self.token]})

class VerifyTokenResult:
    """
        VerifyTokenResult: Token验证结果
    """
    pkt_id: int
    type: str
    data: bool
    token: str
    result: str
    def __init__(self, data: bool) -> None:
        self.pkt_id = 1
        self.type = "verify_token"
        self.data = data
        self.token = "null"
        self.result = ujson.dumps({"pkt_id": self.pkt_id, "type": self.type, "data": self.data, "token": self.token, "paramTypes": ["int", "string", "bool", "string"], "paramValues": [self.pkt_id, self.type, self.data, self.token]})

def handlePacket(message: Any, client, server, token, sign_token) -> VerifyTokenResult:
    """
        Returns: VerifyTokenResult
        处理客户端发来的验证token请求
    """
    try:
        if message["token"] == token:
            sign_token[token]["client"].append(client)
            return VerifyTokenResult(True)
        else:
            return VerifyTokenResult(False)
    except:
        return VerifyTokenResult(False)