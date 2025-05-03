import struct
import numpy

from dataclasses import dataclass, field
from io import BytesIO


@dataclass(frozen=True)
class SubChunkPos:
    x: int = 0
    y: int = 0
    z: int = 0


@dataclass(frozen=True)
class HashWithPosY:
    hash: int = 0
    pos_y: int = 0


@dataclass(frozen=True)
class HashWithPosition:
    hash: int = 0
    sub_chunk_pos: SubChunkPos = field(default_factory=lambda: SubChunkPos())
    dimension: int = 0

    def encode(self, writer: BytesIO):
        writer.write(
            struct.pack(
                "<Qiii",
                self.hash,
                self.sub_chunk_pos.x,
                self.sub_chunk_pos.y,
                self.sub_chunk_pos.z,
            )
        )
        writer.write(self.dimension.to_bytes(length=1, byteorder="little"))


def decode_hash_with_position(reader: BytesIO) -> HashWithPosition:
    hash, x, y, z = struct.unpack("<Qiii", reader.read(20))
    dimension = reader.read(1)[0]
    return HashWithPosition(hash, SubChunkPos(x, y, z), dimension)


@dataclass
class PayloadByHash:
    hash: HashWithPosition = field(default_factory=lambda: HashWithPosition())
    payload: numpy.ndarray = field(
        default_factory=lambda: numpy.array([], dtype=numpy.uint8)
    )

    def encode(self, writer: BytesIO):
        self.hash.encode(writer)
        writer.write(struct.pack("<I", len(self.payload)))
        writer.write(self.payload.tobytes())

    def decode(self, reader: BytesIO):
        self.hash = decode_hash_with_position(reader)
        self.payload = numpy.frombuffer(
            reader.read(struct.unpack("<I", reader.read(4))[0]), dtype=numpy.uint8
        )
