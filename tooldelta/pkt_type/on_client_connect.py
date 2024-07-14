from dataclasses import dataclass
import ujson

@dataclass
class OnClientConnectResult:
    """
        Args: data: bool
        OnClientConnectResult: 客户端连接结果
    """
    pkt_id: int
    type: str
    data: bool
    def __init__(self, msg: str) -> None:
        self.result = ujson.loads(msg)
        self.pkt_id = self.result["pkt_id"]
        self.type = self.result["type"]
        self.data = self.result["data"]

class OnClientConnectBuild:
    """
        Args: data: bool
        OnClientConnectResult: 客户端连接结果
    """    
    pkt_id: int
    type: str
    data: bool
    result: str
    def __init__(self, data: bool) -> None:
        self.pkt_id = 0
        self.type = "on_client_connect"
        self.data = data
        self.result = ujson.dumps({"pkt_id": self.pkt_id, "type": self.type, "data": self.data, "paramTypes": ["int", "string", "bool"], "paramValues": [self.pkt_id, self.type, self.data]})


