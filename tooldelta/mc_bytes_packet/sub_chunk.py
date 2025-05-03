import struct
import numpy

from dataclasses import dataclass, field
from io import BytesIO
from tooldelta.constants.packets import PacketIDS
from tooldelta.mc_bytes_packet.base_bytes_packet import BaseBytesPacket

SUB_CHUNK_RESULT_SUCCESS = 1
SUB_CHUNK_RESULT_CHUNK_NOT_FOUND = 2
SUB_CHUNK_RESULT_INVALID_DIMENSION = 3
SUB_CHUNK_RESULT_PLAYER_NOT_FOUND = 4
SUB_CHUNK_RESULT_INDEX_OUT_OF_BOUNDS = 5
SUB_CHUNK_RESULT_SUCCESS_ALL_AIR = 6


@dataclass
class SubChunkEntry:
    Result: int = 0
    SubChunkPosX: int = 0
    SubChunkPosY: int = 0
    SubChunkPosZ: int = 0
    NBTData: numpy.ndarray = field(
        default_factory=lambda: numpy.array([], dtype=numpy.uint8)
    )
    BlobHash: int = 0

    def decode(self, reader: BytesIO):
        self.Result = reader.read(1)[0]
        self.SubChunkPosX, self.SubChunkPosY, self.SubChunkPosZ = struct.unpack(
            "<ihi", reader.read(10)
        )
        self.NBTData = numpy.frombuffer(
            reader.read(struct.unpack("<I", reader.read(4))[0]), dtype=numpy.uint8
        )
        self.BlobHash = struct.unpack("<Q", reader.read(8))[0]


@dataclass
class SubChunk(BaseBytesPacket):
    Dimension: int = 0
    Entries: list[SubChunkEntry] = field(default_factory=lambda: [])
    CacheEnabled: bool = False

    def name(self) -> str:
        return "SubChunk"

    def custom_packet_id(self) -> int:
        return 0

    def real_packet_id(self) -> int:
        return PacketIDS.IDSubChunk

    def encode(self) -> bytes:
        raise NotImplementedError("Encode packet.SubChunk is not support")

    def decode(self, bs: bytes):
        reader = BytesIO(bs)
        self.Dimension = reader.read(1)[0]
        for _ in range(struct.unpack("<H", reader.read(2))[0]):
            s = SubChunkEntry()
            s.decode(reader)
            self.Entries.append(s)
        self.CacheEnabled = bool(reader.read(1)[0])
