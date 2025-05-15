from typing import TYPE_CHECKING
from collections.abc import Callable

from ..mc_bytes_packet.base_bytes_packet import BaseBytesPacket
from ..constants.packets import PacketIDS
from ..constants.tooldelta_cli import INTERNAL_LISTEN_PACKETS
from ..utils import create_result_cb

if TYPE_CHECKING:
    from tooldelta.frame import ToolDelta


DictPacketListener = Callable[[dict], bool]
BytesPacketListener = Callable[[BaseBytesPacket], bool]
DictPacketWaiter = Callable[[dict], None]


class PacketHandler:
    def __init__(self, frame: "ToolDelta"):
        self.frame = frame
        self.listen_packets = INTERNAL_LISTEN_PACKETS.copy()
        self.dict_packet_listener_with_priority: dict[
            int, dict[int, list[DictPacketListener]]
        ] = {}
        self.bytes_packet_listener_with_priority: dict[
            int, dict[int, list[BytesPacketListener]]
        ] = {}
        self.dict_packet_wait_callbacks: dict[int, list[DictPacketWaiter]] = {}

    def wait_next_packet(self, packet_id: PacketIDS, timeout: float = 30) -> dict | None:
        getter, setter = create_result_cb(dict)
        self.dict_packet_wait_callbacks.setdefault(packet_id, []).append(setter)
        res = getter(timeout)
        self.dict_packet_wait_callbacks[packet_id].remove(setter)
        return res

    def add_dict_packet_listener(
        self,
        packet_id: PacketIDS,
        cb: DictPacketListener,
        priority: int = 0,
    ):
        self.listen_packets.add(packet_id)

        self.dict_packet_listener_with_priority.setdefault(packet_id, {})
        self.dict_packet_listener_with_priority[packet_id].setdefault(priority, [])

        plist = self.dict_packet_listener_with_priority[packet_id][priority]
        if cb not in plist:
            plist.append(cb)

    def add_bytes_packet_listener(
        self,
        packet_id: PacketIDS,
        cb: BytesPacketListener,
        priority: int = 0,
    ):
        self.listen_packets.add(packet_id)

        self.bytes_packet_listener_with_priority.setdefault(packet_id, {})
        self.bytes_packet_listener_with_priority[packet_id].setdefault(priority, [])

        plist = self.bytes_packet_listener_with_priority[packet_id][priority]
        if cb not in plist:
            plist.append(cb)

    def entrance_dict_packet(self, packetID: int, packet: dict):
        self._handle_dict_packet(packetID, packet)

    def entrance_bytes_packet(self, packetID: int, packet: BaseBytesPacket):
        self._handle_bytes_packet(packetID, packet)

    def _handle_dict_packet(self, packetID: int, packet: dict):
        pkt_cbs = self.dict_packet_listener_with_priority.get(packetID)
        if pkt_cbs:
            for priority in sorted(pkt_cbs.keys(), reverse=True):
                for cb in pkt_cbs[priority]:
                    if cb(packet):
                        return

    def _handle_bytes_packet(self, packetID: int, packet: BaseBytesPacket):
        pkt_cbs = self.bytes_packet_listener_with_priority.get(packetID)
        if pkt_cbs:
            for priority in sorted(pkt_cbs.keys(), reverse=True):
                for cb in pkt_cbs[priority]:
                    if cb(packet):
                        return

    def _handle_next_dict_packet(self, packetID: int, packet: dict):
        cbs = self.dict_packet_wait_callbacks.get(packetID, [])
        for cb in cbs.copy():
            cb(packet)
