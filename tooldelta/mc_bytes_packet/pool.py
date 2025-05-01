from tooldelta.constants.packets import PacketIDS
from tooldelta.mc_bytes_packet.base_bytes_packet import BaseBytesPacket
from tooldelta.mc_bytes_packet.level_chunk import LevelChunk
from tooldelta.mc_bytes_packet.sub_chunk import SubChunk
from tooldelta.mc_bytes_packet.sub_chunk_request import SubChunkRequest


def is_bytes_packet(real_packet_id: int) -> bool:
    return (
        real_packet_id == PacketIDS.IDSubChunkRequest
        or real_packet_id == PacketIDS.IDLevelChunk
        or real_packet_id == PacketIDS.IDSubChunk
    )


def bytes_packet_by_name(custom_packet_name: str) -> BaseBytesPacket:
    if custom_packet_name == "SubChunkRequest":
        return SubChunkRequest()
    elif custom_packet_name == "LevelChunk":
        return LevelChunk()
    return SubChunk()
