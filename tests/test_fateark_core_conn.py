import json
from types import SimpleNamespace

import grpc
import pytest

from tooldelta import game_utils
from tooldelta.constants import PacketIDS
from tooldelta.internal.launch_cli.fateark_libs import core_conn


def successful_response(payload=""):
    return SimpleNamespace(status=0, payload=payload, error_msg="")


def test_send_packet_propagates_bytes_payload(monkeypatch):
    captured = {}

    class Stub:
        def SendPacket(self, request, timeout):
            captured["request"] = request
            captured["timeout"] = timeout
            return successful_response()

    monkeypatch.setattr(core_conn, "get_utils_stub", lambda: Stub())
    core_conn.sendPacket(175, b"payload")

    assert captured["request"].packet_id == 175
    assert captured["request"].payload == b"payload"
    assert captured["timeout"] == core_conn.DEFAULT_RPC_TIMEOUT


def test_get_unready_player_uses_single_complete_snapshot(monkeypatch):
    calls = []
    info = {
        "uuid": "uuid",
        "unique_id": 10,
        "name": "Steve",
        "xuid": "real-xuid",
        "platform_chat_id": "chat",
        "runtime_id": 11,
        "device_id": "device",
        "build_platform": 7,
        "online": True,
        "abilities": {
            "build": True,
            "mine": True,
            "doors_and_switches": True,
            "open_containers": True,
            "attack_players": True,
            "attack_mobs": True,
            "operator_commands": False,
            "teleport": False,
            "player_permissions": 2,
            "command_permissions": 1,
        },
    }

    class Stub:
        def GetPlayerInfo(self, request, timeout):
            calls.append((request.uuid_str, timeout))
            return successful_response(json.dumps(info))

    monkeypatch.setattr(core_conn, "get_playerkit_stub", lambda: Stub())
    player = core_conn.get_unready_player("uuid")

    assert calls == [("uuid", core_conn.DEFAULT_RPC_TIMEOUT)]
    assert player.xuid == "real-xuid"
    assert player.abilities is not None
    assert player.abilities.player_permissions == 2
    assert player.abilities.command_permissions == 1


def test_command_deadline_is_reported_as_timeout():
    class DeadlineExceeded(grpc.RpcError):
        def code(self):
            return grpc.StatusCode.DEADLINE_EXCEEDED

        def details(self):
            return "deadline"

    def call(_request, timeout):
        assert timeout == 3
        raise DeadlineExceeded

    payload, error = core_conn._command_with_response(call, object(), 2)
    assert payload == {}
    assert error == "timeout"


def test_get_item_forwards_timeout(monkeypatch):
    calls = []
    output = SimpleNamespace(
        OutputMessages=[
            SimpleNamespace(Message="commands.clear.failure.no.items", Parameters=[])
        ]
    )
    controller = SimpleNamespace(
        allplayers=["Steve"],
        bot_name="Bot",
        sendwscmd_with_resp=lambda command, timeout: (
            calls.append((command, timeout)) or output
        ),
    )
    monkeypatch.setattr(game_utils, "_get_game_ctrl", lambda: controller)

    assert game_utils.getItem("Steve", "stone", timeout=1.25) == 0
    assert calls == [('/clear @a[name="Steve"] stone -1 0', 1.25)]


def test_error_response_is_not_silently_ignored():
    response = SimpleNamespace(status=1, payload="", error_msg="write failed")
    with pytest.raises(RuntimeError, match="write failed"):
        core_conn._ensure_success(response, "发送失败")


def test_packet_ids_match_current_fateark_protocol():
    assert PacketIDS.AgentAction == 179
    assert PacketIDS.ChangeMobProperty == 180
    assert PacketIDS.DimensionData == 181
    assert PacketIDS.TickingAreasLoadStatus == 182
    assert PacketIDS.ItemRegistry == PacketIDS.ItemComponent == 162
    assert PacketIDS.ModEffect == PacketIDS.MobEffectV2 == 230


def test_connect_resets_listener_cache_and_closes_previous_channel(monkeypatch):
    class Channel:
        def __init__(self):
            self.closed = False

        def close(self):
            self.closed = True

    class Ready:
        def result(self, timeout):
            assert timeout == 0.5

    previous = Channel()
    replacement = Channel()
    old_channel = core_conn.grpc_con
    old_generation = core_conn.connection_generation
    old_stubs = (
        core_conn.command_stub,
        core_conn.listener_stub,
        core_conn.playerkit_stub,
        core_conn.core_stub,
        core_conn.utils_stub,
    )
    core_conn.grpc_con = previous
    core_conn.listen_packets.add(9)
    monkeypatch.setattr(
        core_conn.grpc, "insecure_channel", lambda _address: replacement
    )
    monkeypatch.setattr(
        core_conn.grpc, "channel_ready_future", lambda _channel: Ready()
    )
    for name in (
        "CommandServiceStub",
        "ListenerServiceStub",
        "PlayerKitServiceStub",
        "FateReversalerServiceStub",
        "UtilsServiceStub",
    ):
        monkeypatch.setattr(core_conn, name, lambda channel: channel)

    try:
        core_conn.connect("localhost:1", timeout=0.5)
        assert previous.closed
        assert core_conn.listen_packets == set()
        assert core_conn.connection_generation == old_generation + 1
    finally:
        core_conn.grpc_con = old_channel
        core_conn.connection_generation = old_generation
        (
            core_conn.command_stub,
            core_conn.listener_stub,
            core_conn.playerkit_stub,
            core_conn.core_stub,
            core_conn.utils_stub,
        ) = old_stubs
