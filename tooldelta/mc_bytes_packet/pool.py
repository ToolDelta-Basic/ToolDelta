from ..constants.packets import PacketIDS
from .base_bytes_packet import BaseBytesPacket
from .level_chunk import LevelChunk
from .sub_chunk import SubChunk
from .sub_chunk_request import SubChunkRequest
from .structure_template_data_response import (
    StructureTemplateDataResponse,
)


def is_bytes_packet(real_packet_id: int) -> bool:
    return (
        real_packet_id == PacketIDS.IDSubChunkRequest
        or real_packet_id == PacketIDS.IDLevelChunk
        or real_packet_id == PacketIDS.IDSubChunk
        or real_packet_id == PacketIDS.IDStructureTemplateDataResponse
    )


def bytes_packet_by_name(custom_packet_name: str) -> BaseBytesPacket:
    match custom_packet_name:
        case "SubChunkRequest":
            return SubChunkRequest()
        case "SubChunk":
            return SubChunk()
        case "LevelChunk":
            return LevelChunk()
        case _:
            return StructureTemplateDataResponse()
