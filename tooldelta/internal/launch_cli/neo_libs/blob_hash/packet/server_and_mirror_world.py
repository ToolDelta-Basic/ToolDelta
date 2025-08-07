import struct
import numpy
import uuid

from dataclasses import dataclass, field
from io import BytesIO
from tooldelta.internal.launch_cli.neo_libs.blob_hash.packet.define import (
    HashWithPosition,
    PayloadByHash,
    decode_hash_with_position,
)


@dataclass
class KeepAlive:
    uid: uuid.UUID = field(
        default_factory=lambda: uuid.UUID("00000000-0000-0000-0000-000000000000")
    )
    packet_name: str = "blob-hash-keep-alive"

    def decode(self, bs: bytes | None):
        if bs is None:
            return
        reader = BytesIO(bs)
        self.uid = uuid.UUID(
            reader.read(struct.unpack("<h", reader.read(2))[0]).decode(encoding="utf-8")
        )


@dataclass
class ServerDisconnected:
    mirror_world_holder_name: str = ""
    packet_name: str = "blob-hash-server-disconnected"

    def decode(self, bs: bytes | None):
        if bs is None:
            return
        reader = BytesIO(bs)
        self.mirror_world_holder_name = reader.read(
            struct.unpack("<h", reader.read(2))[0]
        ).decode(encoding="utf-8")


@dataclass
class QueryDiskHashExist:
    hashes: list[HashWithPosition] = field(default_factory=lambda: [])
    packet_name: str = "blob-hash-query-disk-hash-exist"

    def decode(self, bs: bytes | None):
        if bs is None:
            return
        reader = BytesIO(bs)
        self.hashes = [
            decode_hash_with_position(reader)
            for _ in range(struct.unpack("<H", reader.read(2))[0])
        ]


@dataclass
class QueryDiskHashExistResponse:
    holder_name: str = ""
    states: numpy.ndarray = field(
        default_factory=lambda: numpy.array([], dtype=numpy.bool)
    )
    packet_name: str = "blob-hash-query-disk-hash-exist-response"

    def encode(self) -> bytes:
        writer = BytesIO()
        encode_str = self.holder_name.encode(encoding="utf-8")
        writer.write(struct.pack("<h", len(encode_str)))
        writer.write(encode_str)
        writer.write(struct.pack("<H", len(self.states)))
        writer.write(self.states.tobytes())
        return writer.getvalue()


@dataclass
class GetDiskHashPayload:
    hashes: list[HashWithPosition] = field(default_factory=lambda: [])
    packet_name: str = "blob-hash-get-disk-hash-payload"

    def decode(self, bs: bytes | None):
        if bs is None:
            return
        reader = BytesIO(bs)
        self.hashes = [
            decode_hash_with_position(reader)
            for _ in range(struct.unpack("<H", reader.read(2))[0])
        ]


@dataclass
class GetDiskHashPayloadResponse:
    holder_name: str = ""
    payload: list[PayloadByHash] = field(default_factory=lambda: [])
    packet_name: str = "blob-hash-get-disk-hash-payload-response"

    def encode(self) -> bytes:
        writer = BytesIO()
        encode_str = self.holder_name.encode(encoding="utf-8")
        writer.write(struct.pack("<h", len(encode_str)))
        writer.write(encode_str)
        writer.write(struct.pack("<H", len(self.payload)))
        for i in self.payload:
            i.encode(writer)
        return writer.getvalue()


@dataclass
class RequireSyncHashToDisk:
    payload: list[PayloadByHash] = field(default_factory=lambda: [])
    packet_name: str = "blob-hash-require-sync-hash-to-disk"

    def decode(self, bs: bytes | None):
        if bs is None:
            return
        reader = BytesIO(bs)
        for _ in range(struct.unpack("<H", reader.read(2))[0]):
            p = PayloadByHash()
            p.decode(reader)
            self.payload.append(p)
