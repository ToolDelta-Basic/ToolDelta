import grpc
import json
import uuid
import importlib

from .... import constants
from ....internal.types import UnreadyPlayer, Abilities
from ....mc_bytes_packet.pool import is_bytes_packet

command_pb2 = importlib.import_module(".proto.command_pb2", package=__package__)
listener_pb2 = importlib.import_module(".proto.listener_pb2", package=__package__)
playerkit_pb2 = importlib.import_module(".proto.playerkit_pb2", package=__package__)
reversaler_pb2 = importlib.import_module(".proto.reversaler_pb2", package=__package__)
utils_pb2 = importlib.import_module(".proto.utils_pb2", package=__package__)

from .proto.command_pb2_grpc import CommandServiceStub
from .proto.listener_pb2_grpc import ListenerServiceStub
from .proto.playerkit_pb2_grpc import PlayerKitServiceStub
from .proto.reversaler_pb2_grpc import FateReversalerServiceStub
from .proto.utils_pb2_grpc import UtilsServiceStub


grpc_con: grpc.Channel | None = None
command_stub: CommandServiceStub | None = None
listener_stub: ListenerServiceStub | None = None
playerkit_stub: PlayerKitServiceStub | None = None
core_stub: FateReversalerServiceStub | None = None
utils_stub: UtilsServiceStub | None = None

listen_packets: set[int] = set()


def get_grpc_con():
    global grpc_con
    if grpc_con is None:
        raise Exception("在建立连接前调用")
    return grpc_con


def get_command_stub():
    global command_stub
    if command_stub is None:
        raise Exception("在建立连接前调用")
    return command_stub


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


def get_core_stub():
    global core_stub
    if core_stub is None:
        raise Exception("在建立连接前调用")
    return core_stub


def get_utils_stub():
    global utils_stub
    if utils_stub is None:
        raise Exception("在建立连接前调用")
    return utils_stub


def connect(address: str) -> None:
    global grpc_con, command_stub, listener_stub, playerkit_stub, core_stub, utils_stub
    grpc_con = grpc.insecure_channel(address)
    command_stub = CommandServiceStub(grpc_con)
    listener_stub = ListenerServiceStub(grpc_con)
    playerkit_stub = PlayerKitServiceStub(grpc_con)
    core_stub = FateReversalerServiceStub(grpc_con)
    utils_stub = UtilsServiceStub(grpc_con)


def wait_dead():
    wait_dead_request = reversaler_pb2.WaitDeadRequest()
    res = next(get_core_stub().WaitDead(wait_dead_request))
    return res.reason


def ping():
    return get_core_stub().Ping(reversaler_pb2.PingRequest()).success


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
    resp = get_core_stub().NewFateReversaler(request)
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
        yield packet.id, json.loads(pk_payload)


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


def send_wo_command(cmd: str):
    get_command_stub().SendWOCommand(command_pb2.SendWOCommandRequest(cmd=cmd))


def send_ws_command(cmd: str):
    get_command_stub().SendWSCommand(command_pb2.SendWSCommandRequest(cmd=cmd))


def send_player_command(cmd: str):
    get_command_stub().SendPlayerCommand(command_pb2.SendPlayerCommandRequest(cmd=cmd))


def send_ai_command(cmd: str):
    get_command_stub().SendAICommand(command_pb2.SendAICommandRequest(cmd=cmd))


def send_ws_command_with_response(cmd: str, timeout: float):
    res = get_command_stub().SendWSCommandWithResponse(
        command_pb2.SendWSCommandWithResponseRequest(cmd=cmd, timeout=timeout)
    )
    res_status: int = res.status
    res_payload: str = res.payload
    res_error_msg: str = res.error_msg
    if res_status == 0:
        return json.loads(res_payload), ""
    return {}, res_error_msg


def send_player_command_with_response(cmd: str, timeout: float):
    res = get_command_stub().SendPlayerCommandWithResponse(
        command_pb2.SendPlayerCommandWithResponseRequest(cmd=cmd, timeout=timeout)
    )
    res_status: int = res.status
    res_payload: str = res.payload
    res_error_msg: str = res.error_msg
    if res_status == 0:
        return json.loads(res_payload), ""
    return {}, res_error_msg


def send_ai_command_with_response(cmd: str, timeout: float):
    res = get_command_stub().SendAICommandWithResponse(
        command_pb2.SendAICommandWithResponseRequest(cmd=cmd, timeout=timeout)
    )
    res_status: int = res.status
    res_payload: str = res.payload
    res_error_msg: str = res.error_msg
    if res_status == 0:
        return json.loads(res_payload), ""
    return {}, res_error_msg


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
        runtime_id=stub.GetPlayerEntityRuntimeID(
            playerkit_pb2.GetPlayerEntityRuntimeIDRequest(uuid_str=uuid)
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
