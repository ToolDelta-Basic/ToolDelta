from collections.abc import Callable
from typing import TYPE_CHECKING
from threading import Event
import uuid

from ...utils import fmts, create_result_cb
from ...utils.basic import validate_uuid
from ..types.player import Player, UnreadyPlayer
from ..types.player_abilities import Abilities, update_player_ability_from_ability_data
from ...constants import PacketIDS

if TYPE_CHECKING:
    from tooldelta import ToolDelta
    from ..packet_handler import PacketHandler

KeyUUID = str
KeyUniqueID = int


class PlayerInfoMaintainer:
    """
    用于维护和更新玩家信息。
    """

    def __init__(self, frame: "ToolDelta"):
        self.frame = frame
        self.name_to_player: dict[str, Player] = {}
        self.uq_to_player: dict[int, Player] = {}
        self.uuid_to_player: dict[str, Player] = {}
        self.xuid_to_player: dict[str, Player] = {}
        self.player_abilities: dict[KeyUniqueID, Abilities] = {}
        self.player_abilities_getter_callback: dict[
            KeyUniqueID, Callable[[bool], None]
        ] = {}
        self.inited_event = Event()
        # pendings
        self.pending_player_abilities_packet: dict[KeyUniqueID, dict] = {}
        self.pending_add_player_packet: dict[KeyUUID, dict] = {}

    def hook_packet_handler(self, packet_handler: "PacketHandler"):
        # PlayerList 的优先级是最高的, 至少需要比 PluginGroup 高
        # 以在插件事件执行完成之前先行完善玩家信息
        packet_handler.add_dict_packet_listener(
            packet_id=PacketIDS.PlayerList, cb=self._hook_playerlist, priority=100
        )
        packet_handler.add_dict_packet_listener(
            packet_id=PacketIDS.UpdateAbilities,
            cb=self._hook_update_abilities,
            priority=100,
        )
        packet_handler.add_dict_packet_listener(
            packet_id=PacketIDS.AddPlayer,
            cb=self._hook_add_player,
            priority=100,
        )

    def block_init(self):
        # 载入初始玩家数据
        if not self.name_to_player:
            playerinfs = self.frame.launcher.get_players_info()
            if playerinfs is not None:
                for unready_player in playerinfs.values():
                    self.add_player(unready_player)
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
        bot_inf = self.name_to_player.get(self.frame.game_ctrl.bot_name)
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

    def getPlayerByUUID(self, _uuid: str | uuid.UUID) -> Player | None:
        """
        通过玩家UUID获取玩家对象。
        Args:
            uuid (str): UUID

        Returns:
            Player | None: 玩家对象
        """
        if isinstance(_uuid, uuid.UUID):
            _uuid = str(_uuid)
        return self.uuid_to_player.get(_uuid)

    def getPlayerByXUID(self, xuid: str) -> Player | None:
        """
        通过玩家XUID获取玩家对象。
        Args:
            xuid (str): XUID

        Returns:
            Player | None: 玩家对象
        """
        return self.xuid_to_player.get(xuid)

    def getAllPlayers(self) -> list[Player]:
        """
        获取所有当前在线的玩家的玩家对象列表。

        Returns:
            list[Player]: 玩家对象列表
        """
        return list(self.name_to_player.values())

    def add_player(self, player: UnreadyPlayer):
        ready_player = player.ready(self)
        self.name_to_player[player.name] = ready_player
        self.uq_to_player[player.unique_id] = ready_player
        self.uuid_to_player[player.uuid] = ready_player
        self.xuid_to_player[player.xuid] = ready_player
        self._lookup_pendings(ready_player)

    def remove_player(self, player: Player):
        del self.name_to_player[player.name]
        del self.uq_to_player[player.unique_id]
        del self.uuid_to_player[player.uuid]
        del self.xuid_to_player[player.xuid]
        if player.unique_id in self.player_abilities:
            del self.player_abilities[player.unique_id]
        player.online = False

    def get_player_ability(self, player: Player) -> Abilities:
        ab = self.player_abilities.get(player.unique_id)
        if ab is None:
            getter, setter = create_result_cb()
            self.player_abilities_getter_callback[player.unique_id] = setter
            res = getter(20)
            del self.player_abilities_getter_callback[player.unique_id]
            if res is None:
                raise ValueError("[internal] 获取玩家能力超时")
            return self.player_abilities[player.unique_id]
        else:
            return ab

    def _block_until_inited(self):
        # 阻塞直到获取到包含全局玩家身份的 PlayerList 数据包
        fmts.print_inf("正在等待获取全局玩家数据..")
        ok = self.inited_event.wait(30)
        if ok:
            fmts.print_suc("已收到全局玩家数据")
        else:
            raise SystemExit("全局玩家数据获取超时")

    def _hook_update_abilities(self, packet: dict):
        uqID = packet["AbilityData"]["EntityUniqueID"]
        player = self.getPlayerByUniqueID(uqID)
        if player is None:
            self.pending_player_abilities_packet[uqID] = packet
        else:
            self._update_player_by_ability_packet(player, packet)
        return False

    def _hook_add_player(self, packet: dict):
        puuid = validate_uuid(packet["UUID"])
        p = self.getPlayerByUUID(puuid)
        if p is None:
            self.pending_add_player_packet[puuid] = packet
        else:
            self._update_player_by_add_player_packet(p, packet)
        return False

    def _hook_playerlist(self, packet: dict):
        self.inited_event.set()
        if packet["ActionType"] == 0:
            for entry in packet["Entries"]:
                self._hook_playerlist_add_player(entry)
        else:
            for entry in packet["Entries"]:
                self._hook_playerlist_remove_player(entry)
        return False

    def _hook_playerlist_add_player(self, entry: dict):
        unique_id = entry["EntityUniqueID"]
        playername = entry["Username"]
        ud = validate_uuid(entry["UUID"])
        self.add_player(
            UnreadyPlayer(
                uuid=ud,
                unique_id=unique_id,
                name=playername,
                xuid=entry["XUID"],
                platform_chat_id=entry["PlatformChatID"],
                device_id=None,
                build_platform=entry["BuildPlatform"],
                online=True,
            )
        )

    def _hook_playerlist_remove_player(self, entry: dict):
        ud = validate_uuid(entry["UUID"])
        if player := self.getPlayerByUUID(ud):
            self.remove_player(player)
        else:
            fmts.print_war(
                f"[internal] PlayerInfoMaintainer: remove_player: 找不到玩家的 UUID: {ud}"
            )

    def _lookup_pendings(self, player: Player):
        if player.uuid in self.pending_add_player_packet:
            self._update_player_by_add_player_packet(
                player, self.pending_add_player_packet.pop(player.uuid)
            )
        if player.unique_id in self.pending_player_abilities_packet:
            self._update_player_by_ability_packet(
                player, self.pending_player_abilities_packet.pop(player.unique_id)
            )

    def _update_player_by_ability_packet(self, player: Player, packet: dict):
        ab_data = packet["AbilityData"]
        uqID = ab_data["EntityUniqueID"]
        update_player_ability_from_ability_data(self, player, ab_data)
        if uqID in self.player_abilities_getter_callback:
            self.player_abilities_getter_callback[uqID](True)

    def _update_player_by_add_player_packet(self, player: Player, packet: dict):
        player.runtime_id = packet["EntityRuntimeID"]
        player.device_id = packet["DeviceID"]
        update_player_ability_from_ability_data(self, player, packet["AbilityData"])

    def __iter__(self):
        "iter online players"
        return iter(self.getAllPlayers())
