from dataclasses import dataclass
from typing import Any
import ujson

@dataclass
class CoreVersionBuild:
    """
        CoreVersionBuild: 请求Core版本号
    """
    pkt_id: int
    type: str
    build: str
    def __init__(self) -> None:
        self.pkt_id = 2
        self.type = "core_version"
        self.build = ujson.dumps({"pkt_id": self.pkt_id, "type": self.type, "paramTypes": ["int", "string"], "paramValues": [self.pkt_id, self.type]})

class CoreVersionResult:
    """
        CoreVersionResult: Core版本号返回结果
    """
    pkt_id: int
    type: str
    version: str
    result: str
    def __init__(self, version: str) -> None:
        self.pkt_id = 2
        self.type = "verify_token"
        self.version = version
        self.result = ujson.dumps({"pkt_id": self.pkt_id, "type": self.type, "version": self.version, "paramTypes": ["int", "string", "string"], "paramValues": [self.pkt_id, self.type, self.version]})

def handlePacket(message: Any, client, server, token, sign_token) -> CoreVersionResult:
    """
        Returns: CoreVersionResult
        处理客户端发来的Core版本请求
    """
    return CoreVersionResult(sign_token[token]["version"])