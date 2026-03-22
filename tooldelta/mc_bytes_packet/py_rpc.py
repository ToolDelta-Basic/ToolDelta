import struct
import msgpack
from dataclasses import dataclass
from io import BytesIO
from tooldelta.constants.packets import PacketIDS
from tooldelta.mc_bytes_packet.base_bytes_packet import BaseBytesPacket
from typing import Any

PYRPC_OP_SEND = 0x05DB23AE
PYRPC_OP_RECV = 0x0094D408


@dataclass
class PyRpc(BaseBytesPacket):
    Value: Any = None
    OperationType: int = 0

    def name(self) -> str:
        return "PyRpc"

    def custom_packet_id(self) -> int:
        return 4

    def real_packet_id(self) -> int:
        return PacketIDS.IDPyRpc

    def encode(self) -> bytes:
        writer = BytesIO()
        payload = msgpack.packb(self.Value, use_bin_type=True)
        writer.write(struct.pack("<I", len(payload)))  # type: ignore
        writer.write(payload)  # type: ignore
        writer.write(struct.pack("<I", self.OperationType))
        return writer.getvalue()

    def decode(self, bs: bytes):
        reader = BytesIO(bs)
        length = struct.unpack("<I", reader.read(4))[0]
        self.Value = msgpack.unpackb(
            reader.read(length), raw=False, strict_map_key=False
        )
        self.OperationType = struct.unpack("<I", reader.read(4))[0]
