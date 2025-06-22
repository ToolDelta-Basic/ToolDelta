"数据包类构建器"

from tooldelta.constants import PacketIDS
from tooldelta.protocol.reader import Reader


class Packet:
    ID: int
    raw: bytes

    def __init__(self, raw: bytes):
        self.raw = raw

    def marshal(self):
        raise NotImplementedError


class SubPacket_CmdOutputMsg:
    """命令输出消息子包构建"""

    Success: bool
    Message: str
    Parameters: list

    def __init__(self, pkt: dict):
        self.Success = pkt["Success"]
        self.Parameters = pkt["Parameters"]
        self.Message = pkt["Message"]


class SubPacket_CmdOrigin:
    "命令来源子包构建"

    Origin: int
    UUID: str
    RequestID: str
    PlayerUniqueID: int

    def __init__(self, pkt: dict):
        self.Origin = pkt["Origin"]
        self.UUID = pkt["UUID"]
        self.RequestID = pkt["RequestID"]
        self.PlayerUniqueID = pkt["PlayerUniqueID"]


class Packet_CommandOutput:
    "命令输出包构建"

    CommandOrigin: SubPacket_CmdOrigin
    OutputType: int
    SuccessCount: int
    OutputMessages: list[SubPacket_CmdOutputMsg]
    DataSet: str
    as_dict: dict

    def __init__(self, pkt: dict):
        self.as_dict = pkt
        self.CommandOrigin = SubPacket_CmdOrigin(pkt["CommandOrigin"])
        self.OutputMessages = [
            SubPacket_CmdOutputMsg(imsg) for imsg in pkt["OutputMessages"]
        ]
        self.SuccessCount = pkt["SuccessCount"]
        self.OutputType = pkt["OutputType"]
        self.DataSet = pkt["DataSet"]


class Text(Packet):
    ID = PacketIDS.IDText
    TextType: int
    NeedsTranslation: bool
    SourceName: str
    Message: str
    Parameters: list[str]
    XUID: str
    PlatformChatID: str
    NeteaseExtraData: list[str]
    Unknown: str

    def marshal(self):
        reader = Reader(self.raw)
        self.TextType = reader.uint8()
        self.NeedsTranslation = reader.bool()
        match self.TextType:
            case 1 | 7 | 8:
                self.SourceName = reader.string()
                self.Message = reader.string()
                self.Parameters = []
            case 0 | 5 | 6 | 9 | 10 | 11:
                self.Message = reader.string()
            case 2 | 3 | 4:
                self.Message = reader.string()
                self.Parameters = reader.list(reader.string)
        self.XUID = reader.string()
        self.PlatformChatID = reader.string()
        # 网易
        match self.TextType:
            case 1:
                self.NeteaseExtraData = reader.list(reader.string)
            case 3:
                self.Unknown = reader.string()

