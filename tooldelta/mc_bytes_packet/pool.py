from tooldelta.mc_bytes_packet.base_bytes_packet import BaseBytesPacket
from tooldelta.mc_bytes_packet.level_chunk import LevelChunk
from tooldelta.mc_bytes_packet.sub_chunk import SubChunk


def bytes_packet_by_name(custom_packet_name: str) -> BaseBytesPacket:
    if custom_packet_name == "LevelChunk":
        return LevelChunk()
    return SubChunk()
