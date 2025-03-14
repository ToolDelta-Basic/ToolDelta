from typing import TYPE_CHECKING
from threading import Event

from ..utils import fmts
from .types.player import Player, UnreadyPlayer
from .types import player_abilities
from ..constants import PacketIDS

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
        self.inited_event = Event()

    def hook_packet_handler(self, packet_handler: "PacketHandler"):
        packet_handler.add_packet_listener(
            packet_id=PacketIDS.PlayerList,
            cb=self._hook_playerlist,
            priority=100
        )
        packet_handler.add_packet_listener(
            packet_id=PacketIDS.UpdateAbilities,
            cb=self._hook_update_abilities,
            priority=100
        )

    def block_init(self):
        # 载入初始玩家数据
        if not self.name_to_player:
            playerinfs = self.frame.launcher.get_players_info()
            if playerinfs:
                for playername, unready_player in playerinfs.items():
                    self.uq_to_player[unready_player.unique_id] = self.name_to_player[
                        playername
                    ] = self.uuid_to_player[unready_player.uuid] = unready_player.ready(
                        self
                    )
                fmts.print_suc("已从接入点获取全局玩家数据")
            else:
                self._block_until_inited()

    def getBotInfo(self) -> Player:
        """
        获取机器人本身的玩家对象。

        Raises:
            ValueError: 无法通过机器人名称获取信息

        Returns:
            Player: 玩家对象
        """
        bot_inf = self.name_to_player.get(self.frame.launcher.bot_name)
        if bot_inf is None:
            raise ValueError("无法获取机器人信息")
        return bot_inf

    def getPlayerByName(self, name: str) -> Player | None:
        """
        通过玩家名称获取玩家对象。

        Args:
            name (str): 玩家名

        Returns:
            Player | None: 玩家对象
        """
        return self.name_to_player.get(name)

    def getPlayerByUniqueID(self, uqID: int) -> Player | None:
        """
        通过玩家uniqueID获取玩家对象。

        Args:
            uqID (int): uniqueID

        Returns:
            Player | None: 玩家对象
        """
        return self.uq_to_player.get(uqID)

    def getPlayerByUUID(self, uuid: str) -> Player | None:
        """
        通过玩家UUID获取玩家对象。
        Args:
            uuid (str): UUID

        Returns:
            Player | None: 玩家对象
        """
        return self.uuid_to_player.get(uuid)

    def getAllPlayers(self) -> list[Player]:
        """
        获取所有当前在线的玩家的玩家对象列表。

        Returns:
            list[Player]: 玩家对象列表
        """
        return list(self.name_to_player.values())

    def add_player(self, player: UnreadyPlayer):
        self.uq_to_player[player.unique_id] = self.name_to_player[
            player.name
        ] = self.uuid_to_player[player.uuid] = player.ready(self)

    def remove_player(self, player: Player):
        del self.name_to_player[player.name]
        del self.uq_to_player[player.unique_id]
        del self.uuid_to_player[player.uuid]
        if player.unique_id in self.player_abilities:
            del self.player_abilities[player.unique_id]
        player.online = False

    def _block_until_inited(self):
        # 阻塞直到获取到包含全局玩家身份的 PlayerList 数据包
        fmts.print_inf("正在等待获取全局玩家数据..")
        ok = self.inited_event.wait(30)
        if ok:
            fmts.print_suc("已收到全局玩家数据")
        else:
            raise SystemExit("全局玩家数据获取超时")

    def _hook_update_abilities(self, packet: dict):
        ab_data = packet["AbilityData"]
        uqID = ab_data["EntityUniqueID"]
        player = self.getPlayerByUniqueID(uqID)
        if player is None:
            fmts.print_war(
                f"[internal] PlayerInfoMaintainer: hook_update_abilities: 找不到玩家的 uniqueUD: {uqID}"
            )
            return False
        player_abilities.update_player_ability_from_server(self, player, packet)
        return False

    def _hook_playerlist(self, packet: dict):
        self.inited_event.set()
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
        self.add_player(
            UnreadyPlayer(
                uuid=entry["UUID"],
                unique_id=unique_id,
                name=playername,
                xuid=entry["XUID"],
                platform_chat_id=entry["PlatformChatID"],
                build_platform=entry["BuildPlatform"],
                online=True,
            )
        )

    def _hook_remove_player(self, entry: dict):
        if player := self.getPlayerByUUID(entry["UUID"]):
            self.remove_player(player)
        else:
            fmts.print_war(
                f"[internal] PlayerInfoMaintainer: remove_player: 找不到玩家的 UUID: {entry['UUID']}"
            )
