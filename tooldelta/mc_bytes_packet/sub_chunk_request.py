import struct, numpy
from dataclasses import dataclass, field
from io import BytesIO
from tooldelta.constants.packets import PacketIDS
from tooldelta.mc_bytes_packet.base_bytes_packet import BaseBytesPacket


@dataclass
class SubChunkRequest(BaseBytesPacket):
    Dimension: int = 0
    SubChunkPosX: int = 0
    SubChunkPosY: int = 0
    SubChunkPosZ: int = 0
    Offsets: list[tuple[int, int, int]] = field(default_factory=lambda: [])

    def name(self) -> str:
        return "SubChunkRequest"

    def custom_packet_id(self) -> int:
        return 2

    def real_packet_id(self) -> int:
        return PacketIDS.IDSubChunk

    def encode(self) -> bytes:
        writer = BytesIO()
        writer.write(self.Dimension.to_bytes(length=1, byteorder="little"))
        writer.write(struct.pack("<i", self.SubChunkPosX))
        writer.write(struct.pack("<h", self.SubChunkPosY))
        writer.write(struct.pack("<i", self.SubChunkPosZ))
        writer.write(struct.pack("<H", len(self.Offsets)))
        for i in self.Offsets:
            writer.write(struct.pack("<b", i[0]))
            writer.write(struct.pack("<b", i[1]))
            writer.write(struct.pack("<b", i[2]))
        return writer.getvalue()

    def decode(self, bs: bytes):
        raise NotImplementedError("Decode packet.SubChunkRequest is not support")
