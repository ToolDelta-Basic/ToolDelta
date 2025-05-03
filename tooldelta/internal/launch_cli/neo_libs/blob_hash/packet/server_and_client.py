import struct
import numpy

from dataclasses import dataclass, field
from io import BytesIO
from tooldelta.internal.launch_cli.neo_libs.blob_hash.packet.define import (
    HashWithPosition,
    PayloadByHash,
)


@dataclass
class SetHolderRequest:
    packet_name: str = "blob-hash-set-holder-request"

    def encode(self) -> bytes:
        return b""


@dataclass
class SetHolderResponse:
    success_states: bool = False
    holder_name: str = ""
    packet_name: str = "blob-hash-set-holder-response"

    def decode(self, bs: bytes | None):
        if bs is None:
            return
        reader = BytesIO(bs)
        self.success_states = bool(reader.read(1)[0])
        self.holder_name = reader.read(struct.unpack("<h", reader.read(2))[0]).decode(
            encoding="utf-8"
        )


@dataclass
class GetHashPayload:
    hashes: list[HashWithPosition] = field(default_factory=lambda: [])
    packet_name: str = "blob-hash-get-hash-payload"

    def encode(self) -> bytes:
        writer = BytesIO()
        writer.write(struct.pack("<H", len(self.hashes)))
        for i in self.hashes:
            i.encode(writer)
        return writer.getvalue()


@dataclass
class GetHashPayloadResponse:
    payload: list[PayloadByHash] = field(default_factory=lambda: [])
    packet_name: str = "blob-hash-get-hash-payload-response"

    def decode(self, bs: bytes | None):
        if bs is None:
            return
        reader = BytesIO(bs)
        for _ in range(struct.unpack("<H", reader.read(2))[0]):
            p = PayloadByHash()
            p.decode(reader)
            self.payload.append(p)


@dataclass
class ClientQueryDiskHashExist:
    hashes: list[HashWithPosition] = field(default_factory=lambda: [])
    packet_name: str = "blob-hash-client-query-disk-hash-exist"

    def encode(self) -> bytes:
        writer = BytesIO()
        writer.write(struct.pack("<H", len(self.hashes)))
        for i in self.hashes:
            i.encode(writer)
        return writer.getvalue()


@dataclass
class ClientQueryDiskHashExistResponse:
    states: numpy.ndarray = field(
        default_factory=lambda: numpy.array([], dtype=numpy.bool)
    )
    packet_name: str = "blob-hash-client-query-disk-hash-exist-response"

    def decode(self, bs: bytes | None):
        if bs is None:
            return
        reader = BytesIO(bs)
        self.states = numpy.frombuffer(
            reader.read(struct.unpack("<H", reader.read(2))[0]), dtype=numpy.bool
        )


@dataclass
class ClientGetDiskHashPayload:
    hashes: list[HashWithPosition] = field(default_factory=lambda: [])
    packet_name: str = "blob-hash-client-get-disk-hash-payload"

    def encode(self) -> bytes:
        writer = BytesIO()
        writer.write(struct.pack("<H", len(self.hashes)))
        for i in self.hashes:
            i.encode(writer)
        return writer.getvalue()


@dataclass
class ClientGetDiskHashPayloadResponse:
    payload: list[PayloadByHash] = field(default_factory=lambda: [])
    packet_name: str = "blob-hash-client-get-disk-hash-payload-response"

    def decode(self, bs: bytes | None):
        if bs is None:
            return
        reader = BytesIO(bs)
        for _ in range(struct.unpack("<H", reader.read(2))[0]):
            p = PayloadByHash()
            p.decode(reader)
            self.payload.append(p)
