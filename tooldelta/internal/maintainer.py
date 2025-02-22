from typing import TYPE_CHECKING

from tooldelta.color_print import fmts
from .types.player import Player
from .types import player_abilities
from tooldelta.constants import PacketIDS

if TYPE_CHECKING:
    from tooldelta import ToolDelta
    from .packet_handler import PacketHandler


class PlayerInfoMaintainer:
    def __init__(self, frame: "ToolDelta"):
        self.frame = frame
        self.name_to_player: dict[str, Player] = {}
        self.uq_to_player: dict[int, Player] = {}
        self.uuid_to_player: dict[str, Player] = {}
        self.player_abilities: dict[int, player_abilities.Abilities] = {}

    def hook(self, packet_handler: "PacketHandler"):
        packet_handler.add_packet_listener(
            packet_id=PacketIDS.PlayerList,
            cb=self.hook_playerlist,
        )

    def get_player_by_name(self, name: str) -> Player | None:
        return self.name_to_player.get(name)

    def get_player_by_unique_id(self, uqID: int) -> Player | None:
        return self.uq_to_player.get(uqID)

    def get_player_by_uuid(self, uuid: str) -> Player | None:
       return self.uuid_to_player.get(uuid)

    def hook_update_abilities(self, packet: dict):
        ab_data = packet["AbilityData"]
        uqID = ab_data["EntityUniqueID"]
        player = self.get_player_by_unique_id(uqID)
        if player is None:
            fmts.print_war(
                f"[internal] PlayerInfoMaintainer: hook_update_abilities: playerUQ not found: {uqID}"
            )
            return False
        player_abilities.update_player_ability_from_server(
            self, player, packet
        )
        return False

    def hook_playerlist(self, packet: dict):
        if packet["ActionType"] == 0:
            for entry in packet["Entries"]:
                self._hook_add_player(entry)
        else:
            for entry in packet["Entries"]:
                self._hook_remove_player(entry)
        return False

    def _hook_add_player(self, entry: dict):
        unique_id = entry["EntityUniqueID"]
        playername = entry["Username"]
        self.uq_to_player[unique_id] = self.name_to_player[playername] = Player(
            _parent=self,
            uuid=entry["UUID"],
            unique_id=unique_id,
            name=playername,
            xuid=entry["XUID"],
            platform_chat_id=entry["PlatformChatId"],
            build_platform=entry["BuildPlatform"],
            online=True,
        )

    def _hook_remove_player(self, entry: dict):
        if player := self.get_player_by_uuid(entry["UUID"]):
            del self.name_to_player[player.name]
            del self.uq_to_player[player.unique_id]
            del self.uuid_to_player[player.uuid]
            if player.unique_id in self.player_abilities:
                del self.player_abilities[player.unique_id]
            player.online = False
        else:
            fmts.print_war(
                f"[internal] PlayerInfoMaintainer: remove_player: player uuid not found: {entry['UUID']}"
            )
