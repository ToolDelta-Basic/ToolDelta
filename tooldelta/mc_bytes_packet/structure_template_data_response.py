import struct
from dataclasses import dataclass
from io import BytesIO
from tooldelta.constants.packets import PacketIDS
from tooldelta.mc_bytes_packet.base_bytes_packet import BaseBytesPacket


STRUCTURE_TEMPLATE_RESPONSE_EXPORT = 1
STRUCTURE_TEMPLATE_RESPONSE_QUERY = 2
STRUCTURE_TEMPLATE_RESPONSE_IMPORT = 3


@dataclass
class StructureTemplateDataResponse(BaseBytesPacket):
    StructureName: str = ""
    Success: bool = False
    ResponseType: int = 0
    StructureTemplate: bytes = b""

    def name(self) -> str:
        return "StructureTemplateDataResponse"

    def custom_packet_id(self) -> int:
        return 3

    def real_packet_id(self) -> int:
        return PacketIDS.IDStructureTemplateDataResponse

    def encode(self) -> bytes:
        raise NotImplementedError(
            "Encode packet.StructureTemplateDataResponse is not support"
        )

    def decode(self, bs: bytes):
        bytes_length = len(bs)
        reader = BytesIO(bs)

        string_length = struct.unpack("<h", reader.read(2))[0]
        self.StructureName = reader.read(string_length).decode(encoding="utf-8",errors="ignore")

        self.Success = bool(reader.read(1)[0])
        self.ResponseType = reader.read(1)[0]
        self.StructureTemplate = reader.read(bytes_length - reader.seek(0, 1))
