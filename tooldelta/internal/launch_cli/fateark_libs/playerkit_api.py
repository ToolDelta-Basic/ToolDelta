import json
from collections.abc import Callable
from typing import Any

from ....internal.types import Abilities, UnreadyPlayer


class PlayerKitAPI:
    def __init__(
        self,
        stub_provider: Callable[[], Any],
        messages: Any,
        ensure_success: Callable[[Any, str], Any],
        payload: Callable[[Any, str], str],
        json_payload: Callable[[Any, str], Any],
        timeout: float,
    ) -> None:
        self._stub_provider = stub_provider
        self._messages = messages
        self._ensure_success = ensure_success
        self._payload = payload
        self._json_payload = json_payload
        self._timeout = timeout

    def online_player_uuids(self) -> list[str]:
        response = self._stub_provider().GetAllOnlinePlayers(
            self._messages.GetAllOnlinePlayersRequest(), timeout=self._timeout
        )
        return list(self._json_payload(response, "获取在线玩家失败"))

    def player_info(self, uuid: str) -> UnreadyPlayer:
        response = self._stub_provider().GetPlayerInfo(
            self._messages.GetPlayerInfoRequest(uuid_str=uuid), timeout=self._timeout
        )
        info = self._json_payload(response, "获取玩家信息失败")
        abilities = Abilities(**info["abilities"])
        return UnreadyPlayer(
            uuid=info.get("uuid", uuid),
            unique_id=info["unique_id"],
            name=info["name"],
            xuid=info["xuid"],
            platform_chat_id=info["platform_chat_id"],
            runtime_id=info["runtime_id"],
            device_id=info["device_id"],
            build_platform=info["build_platform"],
            online=info["online"],
            abilities=abilities,
        )

    def _string(self, method_name: str, request: Any, action: str) -> str:
        method = getattr(self._stub_provider(), method_name)
        return self._payload(method(request, timeout=self._timeout), action)

    def _ok(self, method_name: str, request: Any, action: str) -> None:
        method = getattr(self._stub_provider(), method_name)
        self._ensure_success(method(request, timeout=self._timeout), action)

    def player_by_name(self, name: str) -> str:
        return self._string(
            "GetPlayerByName",
            self._messages.GetPlayerByNameRequest(name=name),
            "按名称绑定玩家失败",
        )

    def player_by_uuid(self, uuid: str) -> str:
        return self._string(
            "GetPlayerByUUID",
            self._messages.GetPlayerByUUIDRequest(uuid=uuid),
            "按 UUID 绑定玩家失败",
        )

    def release_player(self, uuid: str) -> None:
        self._ok(
            "ReleaseBindPlayer",
            self._messages.ReleaseBindPlayerRequest(uuid_str=uuid),
            "释放玩家绑定失败",
        )

    def login_time(self, uuid: str) -> int:
        response = self._stub_provider().GetPlayerLoginTime(
            self._messages.GetPlayerLoginTimeRequest(uuid_str=uuid),
            timeout=self._timeout,
        )
        return int(self._ensure_success(response, "获取玩家登录时间失败").payload)

    def skin_id(self, uuid: str) -> str:
        return self._string(
            "GetPlayerSkinID",
            self._messages.GetPlayerSkinIDRequest(uuid_str=uuid),
            "获取玩家皮肤失败",
        )

    def metadata(self, uuid: str) -> dict[str, Any]:
        payload = self._string(
            "GetPlayerEntityMetadata",
            self._messages.GetPlayerEntityMetadataRequest(uuid_str=uuid),
            "获取玩家实体数据失败",
        )
        return json.loads(payload)

    def status(self, uuid: str) -> dict[str, bool]:
        stub = self._stub_provider()
        requests = (
            (
                "invulnerable",
                stub.GetPlayerStatusInvulnerable,
                self._messages.GetPlayerStatusInvulnerableRequest,
            ),
            (
                "flying",
                stub.GetPlayerStatusFlying,
                self._messages.GetPlayerStatusFlyingRequest,
            ),
            (
                "may_fly",
                stub.GetPlayerStatusMayFly,
                self._messages.GetPlayerStatusMayFlyRequest,
            ),
        )
        result: dict[str, bool] = {}
        for name, method, request_type in requests:
            response = method(request_type(uuid_str=uuid), timeout=self._timeout)
            result[name] = bool(
                self._ensure_success(response, f"获取玩家状态 {name} 失败").payload
            )
        return result

    def set_ability(self, uuid: str, ability: str, allow: bool) -> None:
        setters = {
            "build": ("SetPlayerCanBuild", self._messages.SetPlayerCanBuildRequest),
            "dig": ("SetPlayerCanDig", self._messages.SetPlayerCanDigRequest),
            "doors_and_switches": (
                "SetPlayerCanDoorsAndSwitches",
                self._messages.SetPlayerCanDoorsAndSwitchesRequest,
            ),
            "open_containers": (
                "SetPlayerCanOpenContainers",
                self._messages.SetPlayerCanOpenContainersRequest,
            ),
            "attack_players": (
                "SetPlayerCanAttackPlayers",
                self._messages.SetPlayerCanAttackPlayersRequest,
            ),
            "attack_mobs": (
                "SetPlayerCanAttackMobs",
                self._messages.SetPlayerCanAttackMobsRequest,
            ),
            "operator_commands": (
                "SetPlayerCanOperatorCommands",
                self._messages.SetPlayerCanOperatorCommandsRequest,
            ),
            "teleport": (
                "SetPlayerCanTeleport",
                self._messages.SetPlayerCanTeleportRequest,
            ),
        }
        try:
            method_name, request_type = setters[ability]
        except KeyError as err:
            raise ValueError(f"未知玩家能力: {ability}") from err
        self._ok(
            method_name,
            request_type(uuid_str=uuid, allow=allow),
            f"设置玩家能力 {ability} 失败",
        )

    def send_chat(self, uuid: str, message: str, raw: bool = False) -> None:
        if raw:
            method_name = "SendPlayerRawChat"
            request = self._messages.SendPlayerRawChatRequest(
                uuid_str=uuid, msg=message
            )
        else:
            method_name = "SendPlayerChat"
            request = self._messages.SendPlayerChatRequest(uuid_str=uuid, msg=message)
        self._ok(method_name, request, "发送玩家消息失败")

    def send_title(self, uuid: str, title: str, subtitle: str = "") -> None:
        self._ok(
            "SendPlayerTitle",
            self._messages.SendPlayerTitleRequest(
                uuid_str=uuid, title=title, sub_title=subtitle
            ),
            "发送玩家标题失败",
        )

    def send_action_bar(self, uuid: str, message: str) -> None:
        self._ok(
            "SendPlayerActionBar",
            self._messages.SendPlayerActionBarRequest(
                uuid_str=uuid, action_bar=message
            ),
            "发送玩家行动栏失败",
        )

    def intercept_next_input(self, uuid: str, retriever_id: str) -> None:
        self._ok(
            "InterceptPlayerJustNextInput",
            self._messages.InterceptPlayerJustNextInputRequest(
                uuid_str=uuid, retriever_id=retriever_id
            ),
            "拦截玩家输入失败",
        )
