from collections.abc import Callable
from enum import IntEnum
from ..constants.packets import PacketIDS
from .base_bytes_packet import BaseBytesPacket
from .level_chunk import LevelChunk
from .sub_chunk import SubChunk
from .sub_chunk_request import SubChunkRequest
from .structure_template_data_response import (
    StructureTemplateDataResponse,
)


class BytesPacketIDs(IntEnum):
    SubChunkRequest = PacketIDS.IDSubChunkRequest
    LevelChunk = PacketIDS.IDLevelChunk
    SubChunk = PacketIDS.IDSubChunk
    StructureTemplateDataResponse = PacketIDS.IDStructureTemplateDataResponse


BYTES_PACKET_ID_POOL: dict[int, Callable[[], BaseBytesPacket]] = {
    PacketIDS.IDSubChunkRequest: lambda: SubChunkRequest(),
    PacketIDS.IDLevelChunk: lambda: LevelChunk(),
    PacketIDS.IDSubChunk: lambda: SubChunk(),
    PacketIDS.IDStructureTemplateDataResponse: lambda: StructureTemplateDataResponse(),
}


def is_bytes_packet(real_packet_id: int) -> bool:
    return real_packet_id in _byte_packets


# redirect
BytesPacketIDS = BytesPacketIDs


def bytes_packet_by_id(custom_packet_id: int) -> BaseBytesPacket:
    res = BYTES_PACKET_ID_POOL.get(custom_packet_id)
    if res is not None:
        return res()
    else:
        raise ValueError(f"Invalid bytes packet id: {custom_packet_id}")

# fix: type int is always not in IntEnum
#      so we convert to int iterable
_byte_packets = [int(x) for x in BytesPacketIDs]
