import grpc
import json
import uuid
import importlib

from ....constants import PacketIDS
from ....internal.types import UnreadyPlayer, Abilities
from ....mc_bytes_packet.pool import is_bytes_packet

utils_pb2 = importlib.import_module(".proto.utils_pb2", package=__package__)
reversaler_pb2 = importlib.import_module(".proto.reversaler_pb2", package=__package__)
listener_pb2 = importlib.import_module(".proto.listener_pb2", package=__package__)
playerkit_pb2 = importlib.import_module(".proto.playerkit_pb2", package=__package__)

from .proto.listener_pb2_grpc import ListenerServiceStub
from .proto.reversaler_pb2_grpc import FateReversalerServiceStub
from .proto.utils_pb2_grpc import UtilsServiceStub
from .proto.playerkit_pb2_grpc import PlayerKitServiceStub


grpc_con: grpc.Channel | None = None
utils_stub: UtilsServiceStub | None = None
listener_stub: ListenerServiceStub | None = None
playerkit_stub: PlayerKitServiceStub | None = None

listen_packets: set[int] = set()


def get_grpc_con():
    global grpc_con
    if grpc_con is None:
        raise Exception("在建立连接前调用")
    return grpc_con


def get_utils_stub():
    global utils_stub
    if utils_stub is None:
        raise Exception("在建立连接前调用")
    return utils_stub


def get_listener_stub():
    global listener_stub
    if listener_stub is None:
        raise Exception("在建立连接前调用")
    return listener_stub


def get_playerkit_stub():
    global playerkit_stub
    if playerkit_stub is None:
        raise Exception("在建立连接前调用")
    return playerkit_stub


def connect(address: str) -> None:
    global grpc_con, listener_stub, playerkit_stub, utils_stub
    grpc_con = grpc.insecure_channel(address)
    utils_stub = UtilsServiceStub(grpc_con)
    listener_stub = ListenerServiceStub(grpc_con)
    playerkit_stub = PlayerKitServiceStub(grpc_con)


def login(
    auth_server: str,
    fbtoken: str,
    server_code: str,
    server_password: str,
) -> tuple[int, str, str]:
    request = reversaler_pb2.NewFateReversalerRequest(
        auth_server=auth_server,
        user_name="",
        user_password="",
        user_token=fbtoken,
        server_code=server_code,
        server_password=server_password,
    )
    resp = FateReversalerServiceStub(get_grpc_con()).NewFateReversaler(request)
    return resp.status, resp.payload, resp.error_msg


def read_output():
    for response in get_listener_stub().ListenFateArk(
        listener_pb2.ListenFateArkRequest()
    ):
        yield response.msg_type, response.msg, response.err_msg


def read_packet():
    for packet in get_listener_stub().ListenPackets(
        listener_pb2.ListenPacketsRequest()
    ):
        pk_payload: str = packet.payload
        if pk_payload == "":
            continue
        yield packet.id, json.loads(packet.payload)

def read_bytes_packet():
    for packet in get_listener_stub().ListenBytesPackets(
        listener_pb2.ListenBytesPacketsRequest()
    ):
        pk_payload: bytes = packet.payload
        if pk_payload == b"":
            continue
        yield packet.id, pk_payload

def sendPacket(pkID: int, pk: dict):
    get_utils_stub().SendPacket(
        utils_pb2.SendPacketRequest(
            packet_id=pkID, json_str=json.dumps(pk, ensure_ascii=False)
        )
    )


def set_listen_packets(pkIDs: set[int]):
    global listen_packets
    for i in pkIDs:
        if i not in listen_packets:
            if is_bytes_packet(i):
                resp = get_listener_stub().ListenTypedBytesPacket(
                    listener_pb2.ListenTypedBytesPacketRequest(packet_id=i)
                )
                if resp.status != 0:
                    raise Exception(f"设置字节流数据包监听错误: {resp.error_msg}")
            else:
                resp = get_listener_stub().ListenTypedPacket(
                    listener_pb2.ListenTypedPacketRequest(packet_id=i)
                )
                if resp.status != 0:
                    raise Exception(f"设置普通数据包监听错误: {resp.error_msg}")
            listen_packets.add(i)


def sendcmd_and_get_uuid(cmd: str):
    ud = str(uuid.uuid4())
    sendPacket(
        PacketIDS.CommandRequest,
        {
            "CommandLine": cmd,
            "CommandOrigin": {
                "Origin": 0,
                "UUID": ud,
                "RequestID": ud,
                "PlayerUniqueID": 0,
            },
            "Internal": False,
            "Version": 0x24,
            "UnLimited": False,
        },
    )
    return ud


def sendwscmd_and_get_uuid(cmd: str):
    ud = str(uuid.uuid4())
    sendPacket(
        PacketIDS.CommandRequest,
        {
            "CommandLine": cmd,
            "CommandOrigin": {
                "Origin": 5,
                "UUID": ud,
                "RequestID": ud,
                "PlayerUniqueID": 0,
            },
            "Internal": False,
            "Version": 0x24,
            "UnLimited": False,
        },
    )
    return ud


def sendwocmd(cmd: str):
    sendPacket(
        PacketIDS.SettingsCommand,
        {"CommandLine": cmd, "SuppressOutput": False},
    )


def get_online_player_uuids() -> list[str]:
    return json.loads(
        get_playerkit_stub()
        .GetAllOnlinePlayers(playerkit_pb2.GetAllOnlinePlayersRequest())
        .payload
    )


def get_unready_player(uuid: str) -> UnreadyPlayer:
    stub = get_playerkit_stub()
    ab = Abilities(
        stub.GetPlayerCanBuild(
            playerkit_pb2.GetPlayerCanBuildRequest(uuid_str=uuid)
        ).payload,
        stub.GetPlayerCanDig(
            playerkit_pb2.GetPlayerCanDigRequest(uuid_str=uuid)
        ).payload,
        stub.GetPlayerCanDoorsAndSwitches(
            playerkit_pb2.GetPlayerCanDoorsAndSwitchesRequest(uuid_str=uuid)
        ).payload,
        stub.GetPlayerCanOpenContainers(
            playerkit_pb2.GetPlayerCanOpenContainersRequest(uuid_str=uuid)
        ).payload,
        stub.GetPlayerCanAttackPlayers(
            playerkit_pb2.GetPlayerCanAttackPlayersRequest(uuid_str=uuid)
        ).payload,
        stub.GetPlayerCanAttackMobs(
            playerkit_pb2.GetPlayerCanAttackMobsRequest(uuid_str=uuid)
        ).payload,
        stub.GetPlayerCanOperatorCommands(
            playerkit_pb2.GetPlayerCanOperatorCommandsRequest(uuid_str=uuid)
        ).payload,
        stub.GetPlayerCanTeleport(
            playerkit_pb2.GetPlayerCanTeleportRequest(uuid_str=uuid)
        ).payload,
        0,  # TODO: player_permission 现在固定为 0
        (
            3
            if stub.GetPlayerIsOP(
                playerkit_pb2.GetPlayerIsOPRequest(uuid_str=uuid)
            ).payload
            else 1
        ),  # TODO: 除非玩家为 OP, 否则命令等级恒为 1
    )
    return UnreadyPlayer(
        uuid=uuid,
        unique_id=stub.GetPlayerEntityUniqueID(
            playerkit_pb2.GetPlayerEntityUniqueIDRequest(uuid_str=uuid)
        ).payload,
        name=stub.GetPlayerName(
            playerkit_pb2.GetPlayerNameRequest(uuid_str=uuid)
        ).payload,
        xuid=uuid[-8:],
        platform_chat_id=stub.GetPlayerPlatformChatID(
            playerkit_pb2.GetPlayerPlatformChatIDRequest(uuid_str=uuid)
        ).payload,
        device_id=stub.GetPlayerDeviceID(
            playerkit_pb2.GetPlayerDeviceIDRequest(uuid_str=uuid)
        ).payload,
        build_platform=stub.GetPlayerBuildPlatform(
            playerkit_pb2.GetPlayerBuildPlatformRequest(uuid_str=uuid)
        ).payload,
        online=stub.GetPlayerOnline(
            playerkit_pb2.GetPlayerOnlineRequest(uuid_str=uuid)
        ).payload,
        abilities=ab,
    )


def get_bot_name():
    return json.loads(
        UtilsServiceStub(get_grpc_con())
        .GetClientMaintainedBotBasicInfo(
            utils_pb2.GetClientMaintainedBotBasicInfoRequest()
        )
        .payload
    )["BotName"]
