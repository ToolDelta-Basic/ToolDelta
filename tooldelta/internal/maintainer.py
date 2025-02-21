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
        self.players: dict[str, Player] = {}
        self.uq_map: dict[int, Player] = {}
        self.player_abilities: dict[int, player_abilities.Abilities] = {}

    def hook(self, packet_handler: "PacketHandler"):
        packet_handler.add_packet_listener(
            packet_id=PacketIDS.PlayerList,
            cb=self.hook_playerlist,
        )

    def get_player_by_unique_id(self, uqID: int) -> Player | None:
        return self.uq_map.get(uqID)

    def get_player_by_uuid(self, uuid: str):
        for player in self.players.values():
            if player.uuid == uuid:
                return player
        return None

    def hook_update_abilities(self, packet: dict):
        ab_data = packet["AbilityData"]
        uqID = ab_data["EntityUniqueID"]
        if uqID not in self.player_abilities:
            player = self.get_player_by_unique_id(uqID)
            if player is None:
                fmts.print_war(
                    f"[internal] PlayerInfoMaintainer: hook_update_abilities: playerUQ not found: {uqID}"
                )
                return
            player_abilities.update_player_ability_from_server(
                self, player, packet
            )

    def hook_add_player(self, entry: dict):
        unique_id = entry["EntityUniqueID"]
        playername = entry["Username"]
        self.uq_map[unique_id] = self.players[playername] = Player(
            _parent=self,
            uuid=entry["UUID"],
            unique_id=unique_id,
            name=playername,
            xuid=entry["XUID"],
            platform_chat_id=entry["PlatformChatId"],
            build_platform=entry["BuildPlatform"],
            online=True,
        )
        return False

    def hook_remove_player(self, entry: dict):
        if player := self.get_player_by_uuid(entry["UUID"]):
            del self.players[player.name]
            del self.uq_map[player.unique_id]
            if player.unique_id in self.player_abilities:
                del self.player_abilities[player.unique_id]
            player.online = False
        else:
            fmts.print_war(
                f"[internal] PlayerInfoMaintainer: remove_player: player uuid not found: {entry['UUID']}"
            )

    def hook_playerlist(self, packet: dict):
        if packet["ActionType"] == 0:
            for entry in packet["Entries"]:
                self.hook_add_player(entry)
        else:
            for entry in packet["Entries"]:
                self.hook_remove_player(entry)
        return False
