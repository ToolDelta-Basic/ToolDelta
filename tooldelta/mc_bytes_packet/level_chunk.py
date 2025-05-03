import struct
from dataclasses import dataclass
from io import BytesIO
from tooldelta.constants.packets import PacketIDS
from tooldelta.mc_bytes_packet.base_bytes_packet import BaseBytesPacket


@dataclass
class LevelChunk(BaseBytesPacket):
    Dimension: int = 0
    ChunkPosX: int = 0
    ChunkPosZ: int = 0
    HighestSubChunkIndex: int = 0
    CacheEnabled: bool = False

    def name(self) -> str:
        return "LevelChunk"

    def custom_packet_id(self) -> int:
        return 0

    def real_packet_id(self) -> int:
        return PacketIDS.IDLevelChunk

    def encode(self) -> bytes:
        raise NotImplementedError("Encode packet.LevelChunk is not support")

    def decode(self, bs: bytes):
        reader = BytesIO(bs)
        self.Dimension = reader.read(1)[0]
        self.ChunkPosX, self.ChunkPosZ = struct.unpack("<ii", reader.read(8))
        self.HighestSubChunkIndex = reader.read(1)[0]
        self.CacheEnabled = bool(reader.read(1)[0])
