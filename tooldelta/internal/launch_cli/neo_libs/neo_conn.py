import ctypes
import enum
import json
import msgpack
import os.path
import platform
import threading
from collections.abc import Callable
from dataclasses import dataclass
from threading import Thread
from typing import Any, ClassVar, Optional

from ....utils import fmts, thread_func, ToolDeltaThread
from ....packets import Packet_CommandOutput

CInt = ctypes.c_int
CLongLong = ctypes.c_longlong
CString = ctypes.c_void_p
CBytes = ctypes.c_void_p

# Give an initial value
LIB: Any = None


APIVersion: int = 0
OldAccessPointVersion = False

def NewAccessPointVersionCheck(attr_name: str):
    global OldAccessPointVersion
    if OldAccessPointVersion:
        raise AttributeError(attr_name + " 在旧版 NeOmega 接入点不被支持。")

def toCString(string: str):
    return ctypes.c_char_p(string.encode(errors="replace"))


def toGoUint8(b: bool):
    return ctypes.c_uint8(1 if b else 0)


def to_GoInt(i: int):
    return CInt(i)


def toPyString(c_string: CString | None):
    if c_string is None:
        return ""
    result = ctypes.string_at(c_string).decode(encoding="utf-8")
    LIB.FreeMem(c_string)
    return result


def toByteCSlice(bs: bytes) -> CBytes:
    return ctypes.cast(ctypes.c_char_p(bs), CBytes)


def as_python_bytes(bs: CBytes, length: int | CInt) -> bytes:
    return ctypes.string_at(bs, int(length))


# define lib path and how to load it


def ConnectOmega(address: str):
    r = LIB.ConnectOmega(toCString(address))
    if r is not None:
        raise Exception(toPyString(r))


@dataclass
class AccountOptions:
    AuthServer: str = "https://api.fastbuilder.pro"
    UserToken: str = ""
    UserName: str = ""
    UserPassword: str = ""
    ServerCode: str = ""
    ServerPassword: str = ""


def StartOmega(address: str, options: AccountOptions):
    r = LIB.StartOmega(toCString(address), toCString(json.dumps(options.__dict__)))
    if r is not None:
        raise Exception(toPyString(r))


def OmegaAvailable():
    if LIB.OmegaAvailable() != 1:
        raise Exception("omega Core disconnected")


# end lib core functions: connect


# lib core: event basic
class Event(ctypes.Structure):
    type: CString
    retriever: CString
    _fields_: ClassVar[list[tuple[str, Any]]] = [
        ("type", CString),
        ("retriever", CString),
    ]


def EventPoll() -> tuple[str, str]:
    event = LIB.EventPoll()
    return toPyString(event.type), toPyString(event.retriever)


def OmitEvent():
    LIB.OmitEvent()


# end lib core: event

# event retrievers


class ConsumeSoftData_return(ctypes.Structure):
    bs: CBytes
    length: CInt
    _fields_ = (("bs", CBytes), ("length", CInt))


class ConsumeSoftCall_return(ctypes.Structure):
    bs: CBytes
    length: CInt
    _fields_ = (("bs", CBytes), ("length", CInt))


def SoftCallWithJSON(api: str, json_args: str, retrieverID: str):
    OmegaAvailable()
    LIB.SoftCall(toCString(api), toCString(json_args), toCString(retrieverID))
    LIB.SoftCall(
        toCString(api),
        0,
        toByteCSlice(json_args.encode(encoding="utf-8")),
        len(json_args),
        toCString(retrieverID),
    )


def SoftCallWithBytes(api: str, message: bytes, retrieverID: str):
    OmegaAvailable()
    LIB.SoftCall(
        toCString(api), 1, toByteCSlice(message), len(message), toCString(retrieverID)
    )


def SoftListen(api: str, listen_bytes_message: bool):
    OmegaAvailable()
    LIB.SoftListen(toCString(api), int(listen_bytes_message))


def SoftPubJSON(
    api: str,
    json_args: str,
):
    OmegaAvailable()
    LIB.SoftPub(
        toCString(api),
        0,
        toByteCSlice(json_args.encode(encoding="utf-8")),
        len(json_args),
    )


def SoftPubBytes(
    api: str,
    message: bytes,
):
    OmegaAvailable()
    LIB.SoftPub(toCString(api), 1, toByteCSlice(message), len(message))


def SoftReg(api: str, is_bytes_api: bool):
    OmegaAvailable()
    LIB.SoftReg(toCString(api), int(is_bytes_api))


class MCPacketEvent(ctypes.Structure):
    packetDataAsJsonStr: CString
    convertError: CString
    _fields_: ClassVar[list[tuple[str, Any]]] = [
        ("packetDataAsJsonStr", CString),
        ("convertError", CString),
    ]


class MCMsgpackPacketEvent(ctypes.Structure):
    packetDataAsMsgpack: CString
    bs_len: CInt
    convertError: CString
    _fields_: ClassVar[list[tuple[str, Any]]] = [
        ("packetDataAsMsgpack", CString),
        ("bs_len", CInt),
        ("convertError", CString),
    ]


class ConsumeMCBytesPacket_return(ctypes.Structure):
    pktBytes: CBytes
    length: CInt
    _fields_ = (("pktBytes", CBytes), ("length", CInt))


# Async Actions
# cmds


def SendWebSocketCommandNeedResponse(cmd: str, retrieverID: str):
    OmegaAvailable()
    LIB.SendWebSocketCommandNeedResponse(toCString(cmd), toCString(retrieverID))


def SendPlayerCommandNeedResponse(cmd: str, retrieverID: str):
    OmegaAvailable()
    LIB.SendPlayerCommandNeedResponse(toCString(cmd), toCString(retrieverID))


# OneWay Actions


def SendSettingsCommand(cmd: str):
    OmegaAvailable()
    LIB.SendWOCommand(toCString(cmd))


def SendWebSocketCommandOmitResponse(cmd: str):
    OmegaAvailable()
    LIB.SendWebSocketCommandOmitResponse(toCString(cmd))


def SendPlayerCommandOmitResponse(cmd: str):
    OmegaAvailable()
    LIB.SendPlayerCommandOmitResponse(toCString(cmd))


# Instance Actions


class JsonStrAsIsGamePacketBytes_return(ctypes.Structure):
    pktBytes: CBytes
    length: CInt
    err: CString
    _fields_: ClassVar[list[tuple[str, Any]]] = [
        ("pktBytes", CBytes),
        ("length", CInt),
        ("err", CString),
    ]


def JsonStrAsIsGamePacketBytes(packetID: int, jsonStr: str) -> bytes:
    r: JsonStrAsIsGamePacketBytes_return = LIB.JsonStrAsIsGamePacketBytes(
        to_GoInt(packetID), toCString(jsonStr)
    )
    if toPyString(r.err) != "":
        raise ValueError(toPyString(r.err))
    bs = as_python_bytes(r.pktBytes, r.length)
    LIB.FreeMem(r.pktBytes)
    return bs


def SendGamePacket(packetID: int, payload: str | bytes) -> None:
    if type(payload) is str:
        r = LIB.SendGamePacket(
            to_GoInt(packetID),
            toByteCSlice(payload.encode(encoding="utf-8")),
            len(payload),
        )
        if toPyString(r) != "":
            raise ValueError(toPyString(r))
        return
    r = LIB.SendGamePacket(to_GoInt(packetID), toByteCSlice(payload), len(payload))  # type: ignore
    if toPyString(r) != "":
        raise ValueError(toPyString(r))


# ClientMaintainedBotBasicInfo will not change
@dataclass
class ClientMaintainedBotBasicInfo:
    BotName: str = ""
    BotRuntimeID: int = 0
    BotUniqueID: int = 0
    BotIdentity: str = ""
    BotUUIDStr: str = ""
    BotUID: str = ""


class LoadBlobCache_return(ctypes.Structure):
    bs: CBytes
    length: CInt
    _fields_ = (("bs", CBytes), ("length", CInt))


@dataclass
class ClientMaintainedExtendInfo:
    CompressThreshold: int | None = None
    WorldGameMode: int | None = None
    WorldDifficulty: int | None = None
    Time: int | None = None
    DayTime: int | None = None
    TimePercent: float | None = None
    GameRules: dict[str, Any] | None = None


class Counter:
    def __init__(self, prefix: str) -> None:
        self.current_i = 0
        self.prefix = prefix

    def __next__(self) -> str:
        self.current_i += 1
        return f"{self.prefix}_{self.current_i}"


@dataclass
class CommandOrigin:
    Origin: int = 0
    UUID: str = ""
    RequestID: str = ""
    PlayerUniqueID: int = 0


@dataclass
class OutputMessage:
    Success: bool = False
    Message: str = ""
    Parameters: list[Any] | None = None


@dataclass
class CommandOutput:
    CommandOrigin: Optional["CommandOrigin"] = None
    OutputType: int = 0
    SuccessCount: int = 0
    OutputMessages: list[OutputMessage] | None = None
    DataSet: Any | None = None


def unpackCommandOutput(jsonStr: str | None) -> Packet_CommandOutput | None:
    return None if jsonStr is None else Packet_CommandOutput(json.loads(jsonStr))


@dataclass
class CommandBlockPlaceOption:
    X: int = 0
    Y: int = 0
    Z: int = 0
    BlockName: str = ""
    BockState: str = ""
    NeedRedStone: bool = False
    Conditional: bool = False
    Command: str = ""
    Name: str = ""
    TickDelay: int = 0
    ShouldTrackOutput: bool = False
    ExecuteOnFirstTick: bool = False


@dataclass
class CommandBlockNBTData:
    """指代一个命令块的原始 NBT 数据 (ToolDelta 专有实现类)

    Args
        Command (str; TAG_String): 命令块所包含的命令，默认为 空字符串
        CustomName (str; TAG_String): 命令方块的悬浮文本，默认为 空字符串
        TickDelay (int; TAG_Int): 命令块使用的延迟，默认为 0
        ExecuteOnFirstTick (bool; TAG_Byte): 是否在该命令块上使用第一个已选项 (仅重复型命令块适用)，默认 启用
        TrackOutput (bool; TAG_Byte): 是否在该命令块上启用命令执行输出，默认 启用
        ConditionalMode (bool; TAG_Byte): 命令块是否是“有条件的”，默认为 无条件
        Auto (bool; TAG_Byte): 命令块是否自动运行 (无需红石控制)，默认为 自动运行 (无需红石控制)
    """

    Command: str = ""
    CustomName: str = ""
    TickDelay: int = 0
    ExecuteOnFirstTick: bool = True
    TrackOutput: bool = True
    ConditionalMode: bool = False
    Auto: bool = True


@dataclass
class QueriedPlayerPos:
    dimension: int = 0
    x: float = 0
    y: float = 0.0
    z: float = 0.0
    yRot: float = 0.0


class PlayerKit:
    def __init__(self, uuid: str, parent: "ThreadOmega") -> None:
        self.parent = parent
        self._uuid = uuid
        self._c_uuid = toCString(self._uuid)
        LIB.AddGPlayerUsingCount(self._c_uuid, 1)

    @property
    def uuid(self) -> str:
        return self._uuid

    @property
    def name(self) -> str:
        OmegaAvailable()
        return toPyString(LIB.PlayerName(self._c_uuid))

    @property
    def entity_unique_id(self) -> int:
        OmegaAvailable()
        return int(LIB.PlayerEntityUniqueID(self._c_uuid))

    @property
    def op(self) -> bool:
        OmegaAvailable()
        return bool(LIB.PlayerIsOP(self._c_uuid))

    @property
    def online(self) -> bool:
        OmegaAvailable()
        return bool(LIB.PlayerOnline(self._c_uuid))

    @property
    def login_time(self) -> int:
        OmegaAvailable()
        return int(LIB.PlayerLoginTime(self._c_uuid))

    @property
    def platform_chat_id(self) -> str:
        OmegaAvailable()
        return toPyString(LIB.PlayerPlatformChatID(self._c_uuid))

    @property
    def build_platform(self) -> int:
        OmegaAvailable()
        return int(LIB.PlayerBuildPlatform(self._c_uuid))

    @property
    def skin_id(self) -> str:
        OmegaAvailable()
        return toPyString(LIB.PlayerSkinID(self._c_uuid))

    @property
    def device_id(self) -> str:
        OmegaAvailable()
        return toPyString(LIB.PlayerDeviceID(self._c_uuid))

    @property
    def can_build(self) -> bool:
        OmegaAvailable()
        return bool(LIB.PlayerCanBuild(self._c_uuid))

    def set_build_permission(self, allow: bool):
        OmegaAvailable()
        LIB.PlayerSetBuild(self._c_uuid, toGoUint8(allow))

    @property
    def can_mine(self) -> bool:
        OmegaAvailable()
        return bool(LIB.PlayerCanMine(self._c_uuid))

    def set_mine_permission(self, allow: bool):
        OmegaAvailable()
        LIB.PlayerSetMine(self._c_uuid, toGoUint8(allow))

    @property
    def can_doors_and_switches(self) -> bool:
        OmegaAvailable()
        return bool(LIB.PlayerCanDoorsAndSwitches(self._c_uuid))

    def set_doors_and_switches_permission(self, allow: bool):
        OmegaAvailable()
        LIB.PlayerSetDoorsAndSwitches(self._c_uuid, toGoUint8(allow))

    @property
    def can_open_containers(self) -> bool:
        OmegaAvailable()
        return bool(LIB.PlayerCanOpenContainers(self._c_uuid))

    def set_containers_permission(self, allow: bool):
        OmegaAvailable()
        LIB.PlayerSetOpenContainers(self._c_uuid, toGoUint8(allow))

    @property
    def can_attack_players(self) -> bool:
        OmegaAvailable()
        return bool(LIB.PlayerCanAttackPlayers(self._c_uuid))

    def set_attack_players_permission(self, allow: bool):
        OmegaAvailable()
        LIB.PlayerSetAttackPlayers(self._c_uuid, toGoUint8(allow))

    @property
    def can_attack_mobs(self) -> bool:
        OmegaAvailable()
        return bool(LIB.PlayerCanAttackMobs(self._c_uuid))

    def set_attack_mobs_permission(self, allow: bool):
        OmegaAvailable()
        LIB.PlayerSetAttackMobs(self._c_uuid, toGoUint8(allow))

    @property
    def can_operator_commands(self) -> bool:
        OmegaAvailable()
        return bool(LIB.PlayerCanOperatorCommands(self._c_uuid))

    def set_operator_commands_permission(self, allow: bool):
        OmegaAvailable()
        LIB.PlayerSetOperatorCommands(self._c_uuid, toGoUint8(allow))

    @property
    def can_teleport(self) -> bool:
        OmegaAvailable()
        return bool(LIB.PlayerCanTeleport(self._c_uuid))

    def set_teleports_permission(self, allow: bool):
        OmegaAvailable()
        LIB.PlayerSetTeleport(self._c_uuid, toGoUint8(allow))

    @property
    def is_invulnerable(self) -> bool:
        OmegaAvailable()
        return bool(LIB.PlayerStatusInvulnerable(self._c_uuid))

    @property
    def is_flying(self) -> bool:
        OmegaAvailable()
        return bool(LIB.PlayerStatusFlying(self._c_uuid))

    @property
    def can_fly(self) -> bool:
        OmegaAvailable()
        return bool(LIB.PlayerStatusMayFly(self._c_uuid))

    @property
    def entity_runtime_id(self) -> int:
        OmegaAvailable()
        return int(LIB.PlayerEntityRuntimeID(self._c_uuid))

    @property
    def entity_metadata(self) -> bool:
        OmegaAvailable()
        return json.loads(toPyString(LIB.PlayerEntityMetadata(self._c_uuid)))

    def query(self, conditions: None | str | list[str] = None) -> Packet_CommandOutput:
        query_str = f'querytarget @a[name="{self.name}"'
        if conditions is None:
            query_str += "]"
        elif isinstance(conditions, str):
            query_str += f",{conditions}]"
        else:
            query_str += "," + ",".join(conditions) + "]"
        return self.parent.send_websocket_command_need_response(query_str)

    def check_conditions(self, conditions: None | str | list[str] = None) -> bool:
        return self.query(conditions).SuccessCount > 0

    def __repr__(self) -> str:
        return (
            f"uuid={self.uuid},name={self.name},"
            f"entity_unique_id={self.entity_unique_id},op={self.op},"
            f"online={self.online}"
        )

    def __del__(self):
        LIB.AddGPlayerUsingCount(toCString(self._uuid), -1)


class ConnectType(enum.Enum):
    Remote = "Remote"  # 连接到一个 neOmega Access Point
    Local = "Local"  # 在内部启动一个单独的 neOmega Core


class TranslateChunkNBT_return(ctypes.Structure):
    bs: CBytes
    length: CInt
    _fields_ = (("bs", CBytes), ("length", CInt))


# GOMEGA_HAD_LISTENED_PACKETS = False
# GOMEGA_HAD_LISTENED_PLAYER_CHANGE = False


class ThreadOmega:
    def __init__(
        self,
        connect_type: ConnectType,
        address: str,
        accountOption: AccountOptions | None,
    ) -> None:
        self._thread_counter = Counter("thread")
        self._running_threads: dict[str, Thread] = {}
        self.connect_type = connect_type
        self.address = address
        self.accountOption = accountOption
        self._omega_disconnected_lock = threading.Event()
        self._omega_disconnected_reason: str
        self._cmd_callback_retriever_counter: Counter
        self._omega_cmd_callback_events: dict[str, Callable]
        self._packet_listeners: dict[str, set[Callable[[str, Any], None]]]
        self._player_change_listeners: list[Callable[[PlayerKit, str], None]]
        self._bot_basic_info: ClientMaintainedBotBasicInfo
        self._soft_call_counter = Counter("soft_call")
        self._soft_call_cbs: dict[str, Callable] = {}
        self._soft_call_cbs_is_bytes_result: dict[str, bool] = {}
        self._soft_listeners: dict[str, list[Callable[[Any], None]]] = {}
        self._soft_listeners_is_listen_bytes: dict[str, bool] = {}
        self._soft_reg: dict[str, Callable[[Any], Any]] = {}
        self._soft_reg_is_bytes_api: dict[str, bool] = {}
        self._soft_resp_counter = Counter("soft_resp")

    def connect(self):
        if self.connect_type == ConnectType.Local:
            if self.accountOption is None:
                raise ValueError("accountOption is None")
            StartOmega(self.address, self.accountOption)
            fmts.print_inf(f"Omega 接入点已启动，在 {self.address} 开放接口")
        elif self.connect_type == ConnectType.Remote:
            ConnectOmega(self.address)

        # disconnect event
        self._omega_disconnected_lock.clear()  # lock
        self._omega_disconnected_reason = ""

        # cmd events
        self._cmd_callback_retriever_counter = Counter("cmd_callback")
        self._omega_cmd_callback_events: dict[str, Callable] = {}

        # packet listeners
        self._packet_listeners: dict[str, set[Callable[[str, Any], None]]] = {}

        # setup actions
        # make LIB listen to all packets and new packets will have eventType="MCPacket"

        LIB.ListenAllPackets()

        mapping = json.loads(toPyString(LIB.GetPacketNameIDMapping()))
        self._packet_name_to_id_mapping: dict[str, int] = mapping
        self._packet_id_to_name_mapping = {}
        for packet_name, packet_id in self._packet_name_to_id_mapping.items():
            self._packet_id_to_name_mapping[packet_id] = packet_name
            self._packet_listeners[packet_name] = set()

        LIB.ListenPlayerChange()

        self._player_change_listeners: list[Callable[[PlayerKit, str], None]] = []

        # get bot basic info (this info will not change so we need to get it only once)
        self._bot_basic_info = ClientMaintainedBotBasicInfo(
            **json.loads(toPyString(LIB.GetClientMaintainedBotBasicInfo()))
        )

        # start routine
        return self._react()

    @thread_func("接入点反应核心", ToolDeltaThread.SYSTEM)
    def _react(self):
        while True:
            eventType, retriever = EventPoll()

            if eventType == "OmegaConnErr":
                self._handle_omega_conn_err()
                break

            if eventType == "CommandResponseCB":
                self._handle_command_response_cb(retriever)

            elif eventType == "SoftCallResp":
                self._handle_soft_call_resp(retriever)

            elif eventType == "SoftListen":
                self._handle_soft_listen(retriever)

            elif eventType == "SoftAPICall":
                self._handle_soft_api_call(retriever)

            elif eventType == "MCPacket":
                self._handle_mc_packet(retriever)

            elif eventType == "MCBytesPacket":
                self._handle_mc_bytes_packet(retriever)

            elif eventType == "PlayerChange":
                self._handle_player_change(retriever)

            elif eventType in ["PlayerInterceptInput", "Chat"]:
                self._handle_player_intercept_or_chat()

    def _handle_omega_conn_err(self):
        self._omega_disconnected_reason = toPyString(LIB.ConsumeOmegaConnError())
        self._omega_disconnected_lock.set()

    def _handle_command_response_cb(self, retriever: str):
        cmdResp = unpackCommandOutput(toPyString(LIB.ConsumeCommandResponseCB()))
        if callback_event := self._omega_cmd_callback_events.get(retriever):
            callback_event(cmdResp)
        else:
            fmts.print_war(
                f"接入点核心进程：指令返回 {retriever} 没有对应的回调，已忽略"
            )

    def _handle_soft_call_resp(self, retriever: str):
        softResp: ConsumeSoftData_return = LIB.ConsumeSoftData()
        bs: bytes = as_python_bytes(softResp.bs, softResp.length)
        LIB.FreeMem(softResp.bs)
        if (
            retriever not in self._soft_call_cbs_is_bytes_result
            or retriever not in self._soft_call_cbs
        ):
            return
        if self._soft_call_cbs_is_bytes_result[retriever]:
            self._soft_call_cbs[retriever](bs)
        else:
            self._soft_call_cbs[retriever](json.loads(bs.decode(encoding="utf-8")))

    def _handle_soft_listen(self, retriever: str):
        api_name = retriever
        listeners = self._soft_listeners.get(api_name, [])
        softResp: ConsumeSoftData_return = LIB.ConsumeSoftData()
        bs: bytes = as_python_bytes(softResp.bs, softResp.length)
        LIB.FreeMem(softResp.bs)
        if self._soft_listeners_is_listen_bytes:
            for listener in listeners:
                ToolDeltaThread(
                    listener,
                    (bs,),
                    usage="Soft (JSON) Listen Callback Thread",
                    thread_level=ToolDeltaThread.SYSTEM,
                )
        else:
            json_dict = json.loads(bs.decode(encoding="utf-8"))
            for listener in listeners:
                ToolDeltaThread(
                    listener,
                    (json_dict,),
                    usage="Soft (Bytes) Listen Callback Thread",
                    thread_level=ToolDeltaThread.SYSTEM,
                )

    def _handle_soft_api_call(self, retriever: str):
        api_name = retriever
        handler = self._soft_reg[api_name]
        resp_id = next(self._soft_resp_counter)

        softData: ConsumeSoftCall_return = LIB.ConsumeSoftCall(toCString(resp_id))
        bs: bytes = as_python_bytes(softData.bs, softData.length)
        LIB.FreeMem(softData.bs)

        def wrapper(data, resp_id):
            try:
                ret = handler(data)
                if self._soft_reg_is_bytes_api[api_name]:
                    LIB.FinishSoftCall(
                        toCString(resp_id), 1, toByteCSlice(ret), len(ret), ""
                    )
                else:
                    json_ret = json.dumps(ret)
                    LIB.FinishSoftCall(
                        toCString(resp_id),
                        0,
                        toByteCSlice(json_ret.encode(encoding="utf-8")),
                        len(json_ret),
                        "",
                    )
            except Exception as e:
                es = f"{e}"
                LIB.FinishSoftCall(
                    toCString(resp_id),
                    int(self._soft_reg_is_bytes_api[api_name]),
                    toByteCSlice(b""),
                    0,
                    toCString(es),
                )

        if self._soft_reg_is_bytes_api[api_name]:
            ToolDeltaThread(
                wrapper,
                (bs, resp_id),
                usage="Finish Soft Call (Bytes) Thread",
                thread_level=ToolDeltaThread.SYSTEM,
            )
        else:
            json_represents = json.loads(bs.decode(encoding="utf-8"))
            ToolDeltaThread(
                wrapper,
                (json_represents, resp_id),
                usage="Finish Soft Call (JSON) Thread",
                thread_level=ToolDeltaThread.SYSTEM,
            )

    def _handle_mc_packet(self, packetTypeName):
        if packetTypeName == "":
            LIB.OmitEvent()
        elif listeners := self._packet_listeners.get(packetTypeName, []):
            if APIVersion >= 100:
                msgpack_ret: MCMsgpackPacketEvent = LIB.ConsumeMCPacketToMsgpack()
                if convertError := toPyString(msgpack_ret.convertError):
                    fmts.print_err(f"数据包 {packetTypeName} 处理出错: {convertError}")
                    return
                try:
                    pkt = msgpack.unpackb(
                        as_python_bytes(msgpack_ret.packetDataAsMsgpack, msgpack_ret.bs_len),
                        strict_map_key=False
                    )
                except Exception as e:
                    # use fallback
                    pk_ret: MCPacketEvent = LIB.ConsumeMCPacket()
                    pk_jsonstr = toPyString(pk_ret.packetDataAsJsonStr)
                    try:
                        pkt = json.loads(pk_jsonstr)
                        fmts.print_war(f"数据包 {packetTypeName} 处理出错 ({e}), 使用默认处理方式, 包体: {pk_jsonstr[:1000]}")
                    except Exception as e2:
                        # thats strange
                        fmts.print_err(f"数据包 {packetTypeName} 处理出错 ({e}, {e2}), 无法处理数据包 JSON: {pk_jsonstr[:1000]}")
                        return
                for listener in listeners:
                    ToolDeltaThread(
                        listener,
                        (packetTypeName, pkt),
                        usage="Packet Callback Thread",
                        thread_level=ToolDeltaThread.SYSTEM,
                    )
            else:
                json_ret: MCPacketEvent = LIB.ConsumeMCPacket()
                if convertError := toPyString(json_ret.convertError):
                    fmts.print_err(f"数据包 {packetTypeName} 处理出错: {convertError}")
                    return
                jsonPkt = json.loads(toPyString(json_ret.packetDataAsJsonStr))
                for listener in listeners:
                    ToolDeltaThread(
                        listener,
                        (packetTypeName, jsonPkt),
                        usage="Packet Callback Thread",
                        thread_level=ToolDeltaThread.SYSTEM,
                    )

        else:
            LIB.OmitEvent()

    def _handle_mc_bytes_packet(self, customPacketTypeName):
        if OldAccessPointVersion:
            # New end point & old access point
            return
        customPacketTypeName = customPacketTypeName
        listeners = self._packet_listeners.get(customPacketTypeName, [])
        if len(listeners) == 0:
            LIB.OmitEvent()
        else:
            ret: ConsumeMCBytesPacket_return = LIB.ConsumeMCBytesPacket()
            bs: bytes = as_python_bytes(ret.pktBytes, ret.length)
            LIB.FreeMem(ret.pktBytes)
            for listener in listeners:
                ToolDeltaThread(
                    listener,
                    (customPacketTypeName, bs),
                    usage="Packet Bytes Callback Thread",
                    thread_level=ToolDeltaThread.SYSTEM,
                )

    def _handle_player_change(self, playerUUID):
        if not self._player_change_listeners:
            LIB.OmitEvent()
        else:
            action = toPyString(LIB.ConsumePlayerChange())
            for callback in self._player_change_listeners:
                ToolDeltaThread(
                    callback,
                    (self._get_bind_player(playerUUID), action),
                    usage="Player Change Callback Thread",
                )

    @staticmethod
    def _handle_player_intercept_or_chat():
        LIB.OmitEvent()

    def wait_disconnect(self) -> str:
        """return: disconnect reason"""
        self._omega_disconnected_lock.wait()
        return self._omega_disconnected_reason

    @staticmethod
    def _create_lock_and_result_setter():
        lock = threading.Lock()
        lock.acquire()
        ret = [None]

        def result_setter(result):
            ret[0] = result
            lock.release()

        def result_getter(timeout: float = -1) -> Any:
            lock.acquire(timeout=timeout)
            return ret[0]

        return result_setter, result_getter

    def send_websocket_command_need_response(
        self, cmd: str, timeout: float = -1
    ) -> Packet_CommandOutput:
        setter, getter = self._create_lock_and_result_setter()
        try:
            retriever_id = next(self._cmd_callback_retriever_counter)
        except StopIteration as err:
            raise ValueError("retriever counter overflow") from err
        self._omega_cmd_callback_events[retriever_id] = setter
        SendWebSocketCommandNeedResponse(cmd, retriever_id)
        return self.send_cmd_resp(getter, timeout, retriever_id)

    def send_player_command_need_response(
        self, cmd: str, timeout: float = -1
    ) -> Packet_CommandOutput | None:
        setter, getter = self._create_lock_and_result_setter()
        try:
            retriever_id = next(self._cmd_callback_retriever_counter)
        except StopIteration as e:
            raise ValueError("retriever counter overflow") from e
        self._omega_cmd_callback_events[retriever_id] = setter
        SendPlayerCommandNeedResponse(cmd, retriever_id)
        return self.send_cmd_resp(getter, timeout, retriever_id)

    def soft_call_with_json(self, api: str, args: Any, timeout: int = -1) -> Any | None:
        setter, getter = self._create_lock_and_result_setter()
        retriever_id = next(self._soft_call_counter)
        self._soft_call_cbs[retriever_id] = setter
        self._soft_call_cbs_is_bytes_result[retriever_id] = False
        SoftCallWithJSON(api, json.dumps(args), retriever_id)
        res = getter(timeout=timeout)
        del self._soft_call_cbs[retriever_id]
        del self._soft_call_cbs_is_bytes_result[retriever_id]
        return res

    def soft_call_with_bytes(
        self, api: str, args: bytes, timeout: int = -1
    ) -> Any | None:
        setter, getter = self._create_lock_and_result_setter()
        retriever_id = next(self._soft_call_counter)
        self._soft_call_cbs[retriever_id] = setter
        self._soft_call_cbs_is_bytes_result[retriever_id] = True
        SoftCallWithBytes(api, args, retriever_id)
        res = getter(timeout=timeout)
        del self._soft_call_cbs[retriever_id]
        del self._soft_call_cbs_is_bytes_result[retriever_id]
        return res

    def soft_pub_json(self, api: str, args: Any) -> None:
        SoftPubJSON(api, json.dumps(args))

    def soft_pub_bytes(self, api: str, message: bytes) -> None:
        SoftPubBytes(api, message)

    def soft_listen(
        self, api: str, listen_bytes_message: bool, callback: Callable[[Any], None]
    ):
        if api not in self._soft_listeners:
            self._soft_listeners[api] = []
            SoftListen(api, listen_bytes_message)
        self._soft_listeners[api].append(callback)
        self._soft_listeners_is_listen_bytes[api] = listen_bytes_message

    def soft_reg(self, api: str, is_bytes_api: bool, handler: Callable[[Any], Any]):
        self._soft_reg[api] = handler
        self._soft_reg_is_bytes_api[api] = is_bytes_api
        SoftReg(api, is_bytes_api)

    def send_cmd_resp(self, getter, timeout, retriever_id):
        res = getter(timeout=timeout)
        del self._omega_cmd_callback_events[retriever_id]
        return res

    @staticmethod
    def send_settings_command(cmd: str):
        SendSettingsCommand(cmd)

    @staticmethod
    def send_websocket_command_omit_response(cmd: str):
        SendWebSocketCommandOmitResponse(cmd)

    @staticmethod
    def send_player_command_omit_response(cmd: str):
        SendPlayerCommandOmitResponse(cmd)

    def get_packet_name_to_id_mapping(
        self, requires: list[str] | str | None = None
    ) -> dict[str, int] | int:
        if requires is None:
            return dict(self._packet_name_to_id_mapping.items())
        if isinstance(requires, list):
            return {k: self._packet_name_to_id_mapping[k] for k in requires}
        return self._packet_name_to_id_mapping[requires]

    def get_packet_id_to_name_mapping(
        self, requires: list[int] | int | None = None
    ) -> dict[int, str] | str:
        if requires is None:
            return dict(self._packet_id_to_name_mapping.items())
        if isinstance(requires, list):
            return {k: self._packet_id_to_name_mapping[k] for k in requires}
        return self._packet_id_to_name_mapping[requires]

    def listen_packets(
        self,
        targets: str | int | list[dict[int, str] | str],
        callback: Callable[[str, Any], None],
        do_clean_listeners: bool = True,
    ):
        if do_clean_listeners:
            for k in self._packet_listeners.copy():
                self._packet_listeners[k].clear()
        if isinstance(targets, str):
            targets = [targets]
        if isinstance(targets, int):
            targets = [f"{targets}"]
        res = []
        for t in targets:
            if isinstance(t, int):
                res.append(self.get_packet_id_to_name_mapping(t))
                continue
            res.append(t)
        for t in res:
            self._packet_listeners[t].add(callback)

    def construct_game_packet_bytes_in_json_as_is(
        self, packet_type: int, content: Any
    ) -> tuple[int, bytes]:
        return packet_type, JsonStrAsIsGamePacketBytes(packet_type, json.dumps(content))

    def send_game_packet_in_json_as_is(self, packet_type: int, content: Any):
        OmegaAvailable()
        SendGamePacket(packet_type, json.dumps(content))

    def send_game_packet_in_bytes(self, packet_type: int, content: bytes):
        OmegaAvailable()
        SendGamePacket(packet_type, content)

    def get_bot_basic_info(self) -> ClientMaintainedBotBasicInfo:
        return self._bot_basic_info

    def get_bot_name(self) -> str:
        return self._bot_basic_info.BotName

    def get_bot_runtime_id(self) -> int:
        return self._bot_basic_info.BotRuntimeID

    def get_bot_unique_id(self) -> int:
        return self._bot_basic_info.BotUniqueID

    def get_bot_identity(self) -> str:
        return self._bot_basic_info.BotIdentity

    def get_bot_uuid_str(self) -> str:
        return self._bot_basic_info.BotUUIDStr

    @staticmethod
    def get_extend_info() -> ClientMaintainedExtendInfo:
        OmegaAvailable()
        return ClientMaintainedExtendInfo(
            **json.loads(toPyString(LIB.GetClientMaintainedExtendInfo()))
        )

    def load_blob_cache(self, hash: int) -> bytes:
        NewAccessPointVersionCheck("load_blob_cache")
        OmegaAvailable()
        ret: LoadBlobCache_return = LIB.LoadBlobCache(CLongLong(hash))
        payload: bytes = as_python_bytes(ret.bs, ret.length)
        LIB.FreeMem(ret.bs)
        return payload

    def update_blob_cache(self, hash: int, payload: bytes) -> bool:
        NewAccessPointVersionCheck("update_blob_cache")
        OmegaAvailable()
        if (
            LIB.UpdateBlobCache(CLongLong(hash), toByteCSlice(payload), len(payload))
            == 1
        ):
            return True
        return False

    def _get_bind_player(self, uuidStr: str) -> PlayerKit | None:
        return None if uuidStr is None or not uuidStr else PlayerKit(uuidStr, self)

    def get_all_online_players(self):
        OmegaAvailable()
        playerUUIDS = json.loads(toPyString(LIB.GetAllOnlinePlayers()))
        ret: list[PlayerKit] = []
        for uuidStr in playerUUIDS:
            if r := self._get_bind_player(uuidStr):
                ret.append(r)
        return ret

    def get_player_by_name(self, name: str) -> PlayerKit | None:
        OmegaAvailable()
        playerUUID = toPyString(LIB.GetPlayerByName(toCString(name)))
        return self._get_bind_player(playerUUID)

    def get_player_by_uuid(self, uuidStr: str) -> PlayerKit | None:
        OmegaAvailable()
        playerUUID = toPyString(LIB.GetPlayerByUUID(toCString(uuidStr)))
        return self._get_bind_player(playerUUID)

    def listen_player_change(self, callback: Callable[[PlayerKit, str], None]):
        for player in self.get_all_online_players():
            callback(player, "exist")
        self._player_change_listeners.append(callback)

    @staticmethod
    def place_command_block(place_option: CommandBlockPlaceOption):
        LIB.PlaceCommandBlock(toCString(json.dumps(place_option.__dict__)))

    # hi level bot action

    @staticmethod
    def use_hotbar_item(slotID: int) -> None:
        LIB.UseHotbarItem(slotID)

    @staticmethod
    def drop_item_from_hotbar(slotID: int) -> None:
        LIB.DropItemFromHotBar(slotID)

    @staticmethod
    def reset_omega_status():
        LIB.ResetListenPlayerChangeStatus()
        LIB.ResetListenPacketsStatus()

    def __del__(self):
        for t in self._running_threads.values():
            t.join()


def load_lib():
    global LIB, APIVersion, OldAccessPointVersion

    sys_machine = platform.machine().lower()
    sys_type = platform.uname().system
    sys_fn = os.path.join(os.getcwd(), "tooldelta")

    # Mapping architecture names to common naming
    arch_map = {"x86_64": "amd64", "aarch64": "arm64"}
    sys_machine = arch_map.get(sys_machine, sys_machine)

    # Mapping system types to library file names
    if sys_type == "Windows":
        lib_path = f"neomega_windows_{sys_machine}.dll"
    elif "TERMUX_VERSION" in os.environ:
        lib_path = "neomega_android_arm64.so"
    elif sys_type == "Linux":
        lib_path = f"neomega_linux_{sys_machine}.so"
    else:
        lib_path = f"neomega_macos_{sys_machine}.dylib"

    lib_path = os.path.join(sys_fn, "bin", lib_path)
    LIB = (
        ctypes.CDLL(lib_path)
        if sys_type != "Windows"
        else ctypes.cdll.LoadLibrary(lib_path)
    )

    # define lib functions

    # lib core functions: connect
    LIB.ConnectOmega.argtypes = [CString]
    LIB.ConnectOmega.restype = CString
    LIB.StartOmega.argtypes = [CString, CString]
    LIB.StartOmega.restype = CString
    LIB.OmegaAvailable.restype = ctypes.c_uint8
    LIB.EventPoll.restype = Event
    LIB.ConsumeOmegaConnError.restype = CString
    LIB.ConsumeCommandResponseCB.restype = CString
    LIB.ConsumeSoftData.restype = ConsumeSoftData_return
    LIB.SoftCall.argtypes = [CString, CInt, CBytes, CInt, CString]
    LIB.SoftReg.argtypes = [CString, CInt]
    LIB.SoftListen.argtypes = [CString, CInt]
    LIB.FinishSoftCall.argtypes = [CString, CInt, CBytes, CInt, CString]
    LIB.SoftPub.argtypes = [CString, CInt, CBytes, CInt]
    LIB.ConsumeSoftCall.argtypes = [CString]
    LIB.ConsumeSoftCall.restype = ConsumeSoftCall_return
    LIB.ConsumeMCPacket.restype = MCPacketEvent
    LIB.SendWebSocketCommandNeedResponse.argtypes = [CString, CString]
    LIB.SendPlayerCommandNeedResponse.argtypes = [CString, CString]
    LIB.SendWOCommand.argtypes = [CString]
    LIB.SendWebSocketCommandOmitResponse.argtypes = [CString]
    LIB.SendPlayerCommandOmitResponse.argtypes = [CString]
    LIB.FreeMem.argtypes = [ctypes.c_void_p]
    LIB.ListenAllPackets.argtypes = []
    LIB.GetPacketNameIDMapping.restype = CString
    LIB.JsonStrAsIsGamePacketBytes.argtypes = [CInt, CString]
    LIB.JsonStrAsIsGamePacketBytes.restype = JsonStrAsIsGamePacketBytes_return
    LIB.SendGamePacket.argtypes = [CInt, CBytes, CInt]
    LIB.SendGamePacket.restype = CString
    LIB.GetClientMaintainedBotBasicInfo.restype = CString
    LIB.GetClientMaintainedExtendInfo.restype = CString
    LIB.GetAllOnlinePlayers.restype = CString
    LIB.AddGPlayerUsingCount.argtypes = [CString, CInt]
    LIB.ForceReleaseBindPlayer.argtypes = [CString]
    LIB.PlayerName.argtypes = [CString]
    LIB.PlayerName.restype = CString
    LIB.PlayerEntityUniqueID.argtypes = [CString]
    LIB.PlayerEntityUniqueID.restype = ctypes.c_int64
    LIB.PlayerLoginTime.argtypes = [CString]
    LIB.PlayerLoginTime.restype = ctypes.c_int64
    LIB.PlayerPlatformChatID.argtypes = [CString]
    LIB.PlayerPlatformChatID.restype = CString
    LIB.PlayerBuildPlatform.argtypes = [CString]
    LIB.PlayerBuildPlatform.restype = ctypes.c_int32
    LIB.PlayerSkinID.argtypes = [CString]
    LIB.PlayerSkinID.restype = CString
    LIB.PlayerDeviceID.argtypes = [CString]
    LIB.PlayerDeviceID.restype = CString
    LIB.PlayerEntityRuntimeID.argtypes = [CString]
    LIB.PlayerEntityRuntimeID.restype = ctypes.c_uint64
    LIB.PlayerEntityMetadata.argtypes = [CString]
    LIB.PlayerEntityMetadata.restype = CString
    LIB.PlayerIsOP.argtypes = [CString]
    LIB.PlayerIsOP.restype = ctypes.c_uint8
    LIB.PlayerOnline.argtypes = [CString]
    LIB.PlayerOnline.restype = ctypes.c_uint8
    LIB.PlayerCanBuild.argtypes = [CString]
    LIB.PlayerCanBuild.restype = ctypes.c_uint8
    LIB.PlayerSetBuild.argtypes = [CString, ctypes.c_uint8]
    LIB.PlayerCanMine.argtypes = [CString]
    LIB.PlayerCanMine.restype = ctypes.c_uint8
    LIB.PlayerSetMine.argtypes = [CString, ctypes.c_uint8]
    LIB.PlayerCanDoorsAndSwitches.argtypes = [CString]
    LIB.PlayerCanDoorsAndSwitches.restype = ctypes.c_uint8
    LIB.PlayerSetDoorsAndSwitches.argtypes = [CString, ctypes.c_uint8]
    LIB.PlayerCanOpenContainers.argtypes = [CString]
    LIB.PlayerCanOpenContainers.restype = ctypes.c_uint8
    LIB.PlayerSetOpenContainers.argtypes = [CString, ctypes.c_uint8]
    LIB.PlayerCanAttackPlayers.argtypes = [CString]
    LIB.PlayerCanAttackPlayers.restype = ctypes.c_uint8
    LIB.PlayerSetAttackPlayers.argtypes = [CString, ctypes.c_uint8]
    LIB.PlayerCanAttackMobs.argtypes = [CString]
    LIB.PlayerCanAttackMobs.restype = ctypes.c_uint8
    LIB.PlayerSetAttackMobs.argtypes = [CString, ctypes.c_uint8]
    LIB.PlayerCanOperatorCommands.argtypes = [CString]
    LIB.PlayerCanOperatorCommands.restype = ctypes.c_uint8
    LIB.PlayerSetOperatorCommands.argtypes = [CString, ctypes.c_uint8]
    LIB.PlayerCanTeleport.argtypes = [CString]
    LIB.PlayerCanTeleport.restype = ctypes.c_uint8
    LIB.PlayerSetTeleport.argtypes = [CString, ctypes.c_uint8]
    LIB.PlayerStatusInvulnerable.argtypes = [CString]
    LIB.PlayerStatusInvulnerable.restype = ctypes.c_uint8
    LIB.PlayerStatusFlying.argtypes = [CString]
    LIB.PlayerStatusFlying.restype = ctypes.c_uint8
    LIB.PlayerStatusMayFly.argtypes = [CString]
    LIB.PlayerStatusMayFly.restype = ctypes.c_uint8
    LIB.GetPlayerByUUID.argtypes = [CString]
    LIB.GetPlayerByUUID.restype = CString
    LIB.GetPlayerByName.argtypes = [CString]
    LIB.GetPlayerByName.restype = CString
    LIB.ConsumePlayerChange.restype = CString
    LIB.PlaceCommandBlock.argtypes = [CString]
    LIB.UseHotbarItem.argtypes = [ctypes.c_uint8]
    LIB.DropItemFromHotBar.argtypes = [ctypes.c_uint8]

    # Older access point version compatible
    try:
        LIB.LoadBlobCache.argtypes = [CLongLong]
        LIB.LoadBlobCache.restype = LoadBlobCache_return
        LIB.UpdateBlobCache.argtypes = [CLongLong, CBytes, CInt]
        LIB.UpdateBlobCache.restype = CInt
        LIB.TranslateChunkNBT.argtypes = [CBytes, CInt]
        LIB.TranslateChunkNBT.restype = TranslateChunkNBT_return
        LIB.ConsumeMCBytesPacket.restype = ConsumeMCBytesPacket_return
        OldAccessPointVersion = False
    except Exception:
        OldAccessPointVersion = True

    if hasattr(LIB, "OmegaAPIVersion"):
        LIB.OmegaAPIVersion.restype = ctypes.c_int32
        APIVersion = LIB.OmegaAPIVersion()
    else:
        APIVersion = 0

    if APIVersion >= 100:
        LIB.ConsumeMCPacketToMsgpack.restype = MCMsgpackPacketEvent
