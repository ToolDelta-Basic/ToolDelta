from typing import TYPE_CHECKING
from collections.abc import Callable
from ..constants.packets import PacketIDS

if TYPE_CHECKING:
    from tooldelta.frame import ToolDelta

INTERNAL_LISTEN_PACKETS: set[PacketIDS] = {
    PacketIDS.Text,
    PacketIDS.PlayerList,
    PacketIDS.CommandOutput,
    PacketIDS.UpdateAbilities,
}

PacketListener = Callable[[dict], bool]


class PacketHandler:
    def __init__(self, frame: "ToolDelta"):
        self.frame = frame
        self.listen_packets = INTERNAL_LISTEN_PACKETS.copy()
        self.packet_listener_with_priority: dict[
            int, dict[int, list[PacketListener]]
        ] = {}

    def add_packet_listener(
        self, packet_id: PacketIDS, cb: PacketListener, priority: int = 0
    ):
        self.listen_packets.add(packet_id)
        self.packet_listener_with_priority.setdefault(packet_id, {})
        self.packet_listener_with_priority[packet_id].setdefault(priority, [])
        plist = self.packet_listener_with_priority[packet_id][priority]
        if cb not in plist:
            plist.append(cb)

    def entrance(self, packetID: int, packet: dict):
        pkt_cbs = self.packet_listener_with_priority.get(packetID)
        if pkt_cbs:
            for priority in sorted(pkt_cbs.keys(), reverse=True):
                for cb in pkt_cbs[priority]:
                    if cb(packet):
                        return
