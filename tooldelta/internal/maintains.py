from tooldelta import fmts
from .types.player import Player
from .types import player_abilities


class PlayerInfoMaintainer:
    def __init__(self):
        self.players: dict[str, Player] = {}
        self.uq_map: dict[int, Player] = {}
        self.player_abilities: dict[str, player_abilities.Abilities] = {}

    def add_raw_player(
        self,
        playername: str,
        uuid: str,
        unique_id: int,
        runtime_id: int,
    ):
        self.uq_map[unique_id] = self.players[playername] = Player(
            name=playername,
            uuid=uuid,
            unique_id=unique_id,
            runtime_id=runtime_id,
        )

    def remove_player(self, playername: str):
        if player := self.players.get(playername):
            del self.players[playername]
            del self.uq_map[player.unique_id]
        if playername in self.player_abilities:
            del self.player_abilities[playername]
        else:
            fmts.print_war(
                f"[internal] PlayerInfoMaintainer: remove_player: player not found: {playername}"
            )

    def get_player_by_unique_id(self, uqID: int) -> Player | None:
        return self.uq_map.get(uqID)

    def hook_update_abilities(self, playername: str, packet: dict):
        if playername not in self.player_abilities:
            player = self.get_player_by_unique_id(
                packet["AbilityData"]["EntityUniqueID"]
            )
            if player is None:
                fmts.print_war(
                    f"[internal] PlayerInfoMaintainer: hook_update_abilities: player not found: {playername}"
                )
                return
            self.player_abilities[playername] = player_abilities.unmarshal_abilities(
                packet["PlayerPermissions"]
            )
