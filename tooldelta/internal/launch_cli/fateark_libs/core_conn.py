import importlib
import json
from collections.abc import Callable, Iterator
from typing import Any

import grpc

from ....mc_bytes_packet.pool import is_bytes_packet
from .playerkit_api import PlayerKitAPI

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

DEFAULT_RPC_TIMEOUT = 5.0
LOGIN_RPC_TIMEOUT = 90.0
BLOB_HASH_RPC_TIMEOUT = 30.0

grpc_con: grpc.Channel | None = None
command_stub: CommandServiceStub | None = None
listener_stub: ListenerServiceStub | None = None
playerkit_stub: PlayerKitServiceStub | None = None
core_stub: FateReversalerServiceStub | None = None
utils_stub: UtilsServiceStub | None = None
listen_packets: set[int] = set()
connection_generation = 0


def get_grpc_con() -> grpc.Channel:
    if grpc_con is None:
        raise RuntimeError("在建立连接前调用")
    return grpc_con


def get_command_stub() -> CommandServiceStub:
    if command_stub is None:
        raise RuntimeError("在建立连接前调用")
    return command_stub


def get_listener_stub() -> ListenerServiceStub:
    if listener_stub is None:
        raise RuntimeError("在建立连接前调用")
    return listener_stub


def get_playerkit_stub() -> PlayerKitServiceStub:
    if playerkit_stub is None:
        raise RuntimeError("在建立连接前调用")
    return playerkit_stub


def get_core_stub() -> FateReversalerServiceStub:
    if core_stub is None:
        raise RuntimeError("在建立连接前调用")
    return core_stub


def get_utils_stub() -> UtilsServiceStub:
    if utils_stub is None:
        raise RuntimeError("在建立连接前调用")
    return utils_stub


def connect(address: str, timeout: float = DEFAULT_RPC_TIMEOUT) -> None:
    global grpc_con, command_stub, listener_stub, playerkit_stub, core_stub, utils_stub
    global connection_generation
    channel = grpc.insecure_channel(address)
    try:
        grpc.channel_ready_future(channel).result(timeout=timeout)
    except grpc.FutureTimeoutError as err:
        channel.close()
        raise TimeoutError(f"连接 FateArk 超时: {address}") from err

    previous = grpc_con
    grpc_con = channel
    command_stub = CommandServiceStub(channel)
    listener_stub = ListenerServiceStub(channel)
    playerkit_stub = PlayerKitServiceStub(channel)
    core_stub = FateReversalerServiceStub(channel)
    utils_stub = UtilsServiceStub(channel)
    listen_packets.clear()
    connection_generation += 1
    if previous is not None:
        previous.close()


def get_connection_generation() -> int:
    return connection_generation


def _ensure_success(response: Any, action: str) -> Any:
    if response.status != 0:
        raise RuntimeError(f"{action}: {response.error_msg or 'FateArk 调用失败'}")
    return response


def _payload(response: Any, action: str) -> str:
    return str(_ensure_success(response, action).payload)


def _json_payload(response: Any, action: str) -> Any:
    payload = _payload(response, action)
    try:
        return json.loads(payload)
    except (TypeError, json.JSONDecodeError) as err:
        raise ValueError(f"{action}: 返回了无效 JSON: {payload!r}") from err


def _command_deadline(timeout: float) -> float:
    return (timeout if timeout > 0 else 30.0) + 1.0


def wait_dead() -> str:
    response = next(
        get_core_stub().WaitDead(reversaler_pb2.WaitDeadRequest()),
        None,
    )
    return "FateArk WaitDead 流已结束" if response is None else response.reason


def ping(timeout: float = DEFAULT_RPC_TIMEOUT) -> bool:
    return get_core_stub().Ping(reversaler_pb2.PingRequest(), timeout=timeout).success


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
    response = get_core_stub().NewFateReversaler(request, timeout=LOGIN_RPC_TIMEOUT)
    return response.status, response.payload, response.error_msg


def read_output() -> Iterator[tuple[str, str, str]]:
    for response in get_listener_stub().ListenFateArk(
        listener_pb2.ListenFateArkRequest()
    ):
        yield response.msg_type, response.msg, response.err_msg


def read_packet() -> Iterator[tuple[int, dict[str, Any]]]:
    for packet in get_listener_stub().ListenPackets(
        listener_pb2.ListenPacketsRequest()
    ):
        if packet.payload:
            yield packet.id, json.loads(packet.payload)


def read_bytes_packet() -> Iterator[tuple[int, bytes]]:
    for packet in get_listener_stub().ListenBytesPackets(
        listener_pb2.ListenBytesPacketsRequest()
    ):
        if packet.payload:
            yield packet.id, packet.payload


def sendPacket(pkID: int, pk: dict[str, Any] | bytes) -> None:
    if isinstance(pk, dict):
        request = utils_pb2.SendPacketRequest(
            packet_id=pkID,
            json_str=json.dumps(pk, ensure_ascii=False),
        )
    elif isinstance(pk, bytes):
        request = utils_pb2.SendPacketRequest(packet_id=pkID, payload=pk)
    else:
        raise TypeError("sendPacket() 内容必须是 dict 或 bytes")
    response = get_utils_stub().SendPacket(request, timeout=DEFAULT_RPC_TIMEOUT)
    _ensure_success(response, "发送数据包失败")


def set_listen_packets(pkIDs: set[int]) -> None:
    for packet_id in pkIDs:
        if packet_id in listen_packets:
            continue
        if is_bytes_packet(packet_id):
            response = get_listener_stub().ListenTypedBytesPacket(
                listener_pb2.ListenTypedBytesPacketRequest(packet_id=packet_id),
                timeout=DEFAULT_RPC_TIMEOUT,
            )
            action = "设置字节流数据包监听失败"
        else:
            response = get_listener_stub().ListenTypedPacket(
                listener_pb2.ListenTypedPacketRequest(packet_id=packet_id),
                timeout=DEFAULT_RPC_TIMEOUT,
            )
            action = "设置普通数据包监听失败"
        _ensure_success(response, action)
        listen_packets.add(packet_id)


def _send_command(call: Callable[..., Any], request: Any, action: str) -> None:
    response = call(request, timeout=DEFAULT_RPC_TIMEOUT)
    _ensure_success(response, action)


def send_wo_command(cmd: str) -> None:
    _send_command(
        get_command_stub().SendWOCommand,
        command_pb2.SendWOCommandRequest(cmd=cmd),
        "发送 WO 命令失败",
    )


def send_ws_command(cmd: str) -> None:
    _send_command(
        get_command_stub().SendWSCommand,
        command_pb2.SendWSCommandRequest(cmd=cmd),
        "发送 WS 命令失败",
    )


def send_player_command(cmd: str) -> None:
    _send_command(
        get_command_stub().SendPlayerCommand,
        command_pb2.SendPlayerCommandRequest(cmd=cmd),
        "发送玩家命令失败",
    )


def send_ai_command(cmd: str) -> None:
    _send_command(
        get_command_stub().SendAICommand,
        command_pb2.SendAICommandRequest(cmd=cmd),
        "发送 AI 命令失败",
    )


def _command_with_response(call: Callable[..., Any], request: Any, timeout: float):
    try:
        response = call(request, timeout=_command_deadline(timeout))
    except grpc.RpcError as err:
        if err.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
            return {}, "timeout"
        return {}, err.details() or str(err)
    if response.status == 0:
        return _json_payload(response, "解析命令返回失败"), ""
    return {}, response.error_msg


def send_ws_command_with_response(cmd: str, timeout: float):
    return _command_with_response(
        get_command_stub().SendWSCommandWithResponse,
        command_pb2.SendWSCommandWithResponseRequest(cmd=cmd, timeout=timeout),
        timeout,
    )


def send_player_command_with_response(cmd: str, timeout: float):
    return _command_with_response(
        get_command_stub().SendPlayerCommandWithResponse,
        command_pb2.SendPlayerCommandWithResponseRequest(cmd=cmd, timeout=timeout),
        timeout,
    )


def send_ai_command_with_response(cmd: str, timeout: float):
    return _command_with_response(
        get_command_stub().SendAICommandWithResponse,
        command_pb2.SendAICommandWithResponseRequest(cmd=cmd, timeout=timeout),
        timeout,
    )


def get_bot_name() -> str:
    response = get_utils_stub().GetClientMaintainedBotBasicInfo(
        utils_pb2.GetClientMaintainedBotBasicInfoRequest(),
        timeout=DEFAULT_RPC_TIMEOUT,
    )
    return str(_json_payload(response, "获取机器人信息失败")["BotName"])


def get_packet_name_id_mapping() -> dict[str, int]:
    response = get_utils_stub().GetPacketNameIDMapping(
        utils_pb2.GetPacketNameIDMappingRequest(), timeout=DEFAULT_RPC_TIMEOUT
    )
    return dict(_json_payload(response, "获取数据包映射失败"))


def get_extend_info() -> dict[str, Any]:
    response = get_utils_stub().GetClientMaintainedExtendInfo(
        utils_pb2.GetClientMaintainedExtendInfoRequest(),
        timeout=DEFAULT_RPC_TIMEOUT,
    )
    return dict(_json_payload(response, "获取世界扩展信息失败"))


def get_blob_hash_payloads(
    hashes: list[int], timeout: float = BLOB_HASH_RPC_TIMEOUT
) -> dict[int, bytes]:
    """请求世界缓存哈希对应的二进制数据。"""
    response = get_utils_stub().GetBlobHashPayloads(
        utils_pb2.GetBlobHashPayloadsRequest(hashes=hashes),
        timeout=timeout,
    )
    _ensure_success(response, "获取世界缓存数据失败")
    return {int(item.hash): bytes(item.payload) for item in response.payload}


def read_player_changes() -> Iterator[str]:
    yield from (
        response.action
        for response in get_listener_stub().ListenPlayerChange(
            listener_pb2.ListenPlayerChangeRequest()
        )
    )


def read_chat() -> Iterator[dict[str, Any]]:
    for response in get_listener_stub().ListenChat(listener_pb2.ListenChatRequest()):
        yield json.loads(response.payload)


def read_command_block(name: str) -> Iterator[dict[str, Any]]:
    request = listener_pb2.ListenCommandBlockRequest(name=name)
    for response in get_listener_stub().ListenCommandBlock(request):
        yield json.loads(response.payload)


_playerkit_api = PlayerKitAPI(
    lambda: get_playerkit_stub(),
    playerkit_pb2,
    _ensure_success,
    _payload,
    _json_payload,
    DEFAULT_RPC_TIMEOUT,
)

get_online_player_uuids = _playerkit_api.online_player_uuids
get_unready_player = _playerkit_api.player_info
get_player_by_name = _playerkit_api.player_by_name
get_player_by_uuid = _playerkit_api.player_by_uuid
release_player = _playerkit_api.release_player
get_player_login_time = _playerkit_api.login_time
get_player_skin_id = _playerkit_api.skin_id
get_player_metadata = _playerkit_api.metadata
get_player_status = _playerkit_api.status
set_player_ability = _playerkit_api.set_ability
send_player_chat = _playerkit_api.send_chat
send_player_title = _playerkit_api.send_title
send_player_action_bar = _playerkit_api.send_action_bar
intercept_player_next_input = _playerkit_api.intercept_next_input
