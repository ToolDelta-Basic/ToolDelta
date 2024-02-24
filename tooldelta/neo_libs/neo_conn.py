import ctypes
import json
import os.path
import traceback
import threading
import enum
from typing import Iterable, Tuple, Optional, Union, Any, Callable, List, Dict
from threading import Thread
from dataclasses import dataclass
from ..color_print import Print

CInt = ctypes.c_longlong
CString = ctypes.c_char_p
CBytes = ctypes.POINTER(ctypes.c_char)


class byteCSlice(ctypes.Structure):
    _fields_ = [
        ("data", ctypes.POINTER(ctypes.c_char)),
        ("len", ctypes.c_longlong),
        ("cap", ctypes.c_longlong),
    ]


def toCString(string: str):
    return ctypes.c_char_p(bytes(string, encoding="utf-8"))


def to_GoInt(i: int):
    return ctypes.c_longlong(i)


def toPyString(cstring: bytes):
    if cstring is None:
        return ""
    return cstring.decode(encoding="utf-8")


def toByteCSlice(bs: bytes):
    l = len(bs)
    kwargs = {
        "data": (ctypes.c_char * l)(*bs),
        "len": l,
        "cap": l,
    }
    return byteCSlice(**kwargs)


# define lib path and how to load it
import platform

sys_machine = platform.machine().lower()
sys_type = platform.uname().system
sys_fn = os.path.join(os.getcwd(), "tooldelta")
if sys_machine == "x86_64":
    sys_machine = "amd64"
elif sys_machine == "aarch64":
    sys_machine = "arm64"
if sys_type == "Windows":
    lib_path = f"neomega_windows_{sys_machine}.dll"
    lib_path = os.path.join(sys_fn, "neo_libs", lib_path)
    LIB = ctypes.cdll.LoadLibrary(lib_path)
elif "TERMUX_VERSION" in os.environ:
    lib_path = f"neomega_android_arm64.so"
    lib_path = os.path.join(sys_fn, "neo_libs", lib_path)
    LIB = ctypes.CDLL(lib_path)
elif sys_type == "Linux":
    lib_path = f"neomega_linux_{sys_machine}.so"
    lib_path = os.path.join(sys_fn, "neo_libs", lib_path)
    LIB = ctypes.CDLL(lib_path)
else:
    lib_path = f"neomega_macos_{sys_machine}.dylib"
    lib_path = os.path.join(sys_fn, "neo_libs", lib_path)
    LIB = ctypes.CDLL(lib_path)

# define lib functions

# lib core functions: connect
LIB.ConnectOmega.argtypes = [CString]
LIB.ConnectOmega.restype = CString


def ConnectOmega(address):
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


LIB.StartOmega.argtypes = [CString, CString]
LIB.StartOmega.restype = CString


def StartOmega(address, AccountOptions):
    r = LIB.StartOmega(
        toCString(address), toCString(json.dumps(AccountOptions.__dict__))
    )
    if r is not None:
        raise Exception(toPyString(r))


LIB.OmegaAvailable.restype = ctypes.c_uint8


def OmegaAvailable():
    if LIB.OmegaAvailable() != 1:
        raise Exception("omega Core disconnected")


# end lib core functions: connect


# lib core: event basic
class Event(ctypes.Structure):
    _fields_ = [("type", CString), ("retriever", CString)]


LIB.EventPoll.restype = Event


def EventPoll() -> tuple[str, str]:
    event = LIB.EventPoll()
    return toPyString(event.type), toPyString(event.retriever)


def OmitEvent():
    LIB.OmitEvent()


# end lib core: event

# event retrievers
LIB.ConsumeOmegaConnError.restype = CString
LIB.ConsumeCommandResponseCB.restype = CString


class MCPacketEvent(ctypes.Structure):
    _fields_ = [("packetDataAsJsonStr", CString), ("convertError", CString)]


LIB.ConsumeMCPacket.restype = MCPacketEvent

# Async Actions
# cmds

LIB.SendWebSocketCommandNeedResponse.argtypes = [CString, CString]


def SendWebSocketCommandNeedResponse(cmd: str, retrieverID: str):
    OmegaAvailable()
    LIB.SendWebSocketCommandNeedResponse(toCString(cmd), toCString(retrieverID))


LIB.SendPlayerCommandNeedResponse.argtypes = [CString, CString]


def SendPlayerCommandNeedResponse(cmd: str, retrieverID: str):
    OmegaAvailable()
    LIB.SendPlayerCommandNeedResponse(toCString(cmd), toCString(retrieverID))


# OneWay Actions
LIB.SendWOCommand.argtypes = [CString]


def SendSettingsCommand(cmd: str):
    OmegaAvailable()
    LIB.SendWOCommand(toCString(cmd))


LIB.SendWebSocketCommandOmitResponse.argtypes = [CString]


def SendWebSocketCommandOmitResponse(cmd: str):
    OmegaAvailable()
    LIB.SendWebSocketCommandOmitResponse(toCString(cmd))


LIB.SendPlayerCommandOmitResponse.argtypes = [CString]


def SendPlayerCommandOmitResponse(cmd: str):
    OmegaAvailable()
    LIB.SendPlayerCommandOmitResponse(toCString(cmd))


# Instance Actions
LIB.FreeMem.argtypes = [ctypes.c_void_p]
LIB.ListenAllPackets.argtypes = None
LIB.GetPacketNameIDMapping.restype = CString
LIB.JsonStrAsIsGamePacketBytes.argtypes = [CInt, CString]


class JsonStrAsIsGamePacketBytes_return(ctypes.Structure):
    _fields_ = [("pktBytes", CBytes), ("l", CInt), ("err", CString)]


LIB.JsonStrAsIsGamePacketBytes.restype = JsonStrAsIsGamePacketBytes_return


def JsonStrAsIsGamePacketBytes(packetID: int, jsonStr: str) -> bytes:
    r = LIB.JsonStrAsIsGamePacketBytes(to_GoInt(packetID), toCString(jsonStr))
    if toPyString(r.err) != "":
        raise ValueError(toPyString(r.err))
    bs = r.pktBytes[: r.l]
    LIB.FreeMem(r.pktBytes)
    return bs


LIB.SendGamePacket.argtypes = [CInt, CString]
LIB.SendGamePacket.restype = CString


def SendGamePacket(packetID: int, jsonStr: str) -> None:
    r = LIB.SendGamePacket(to_GoInt(packetID), toCString(jsonStr))
    if toPyString(r) != "":
        raise ValueError(toPyString(r))


LIB.GetClientMaintainedBotBasicInfo.restype = CString


# ClientMaintainedBotBasicInfo will not change
@dataclass
class ClientMaintainedBotBasicInfo:
    BotName: str = ""
    BotRuntimeID: int = 0
    BotUniqueID: int = 0
    BotIdentity: str = ""
    BotUUIDStr: str = ""


LIB.GetClientMaintainedExtendInfo.restype = CString


# any member of ClientMaintainedExtendInfo could be not found(which means related info not currently received from server)
@dataclass
class ClientMaintainedExtendInfo:
    CompressThreshold: Optional[int] = None
    WorldGameMode: Optional[int] = None
    WorldDifficulty: Optional[int] = None
    Time: Optional[int] = None
    DayTime: Optional[int] = None
    TimePercent: Optional[float] = None
    GameRules: Optional[Dict[str, Any]] = None


LIB.GetAllOnlinePlayers.restype = CString
LIB.ReleaseBindPlayer.argtypes = [CString]
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
LIB.PlayerPropertiesFlag.argtypes = [CString]
LIB.PlayerPropertiesFlag.restype = ctypes.c_uint32
LIB.PlayerCommandPermissionLevel.argtypes = [CString]
LIB.PlayerCommandPermissionLevel.restype = ctypes.c_uint32
LIB.PlayerActionPermissions.argtypes = [CString]
LIB.PlayerActionPermissions.restype = ctypes.c_uint32
LIB.PlayerGetAbilityString.argtypes = [CString]
LIB.PlayerGetAbilityString.restype = CString
LIB.PlayerOPPermissionLevel.argtypes = [CString]
LIB.PlayerOPPermissionLevel.restype = ctypes.c_uint32
LIB.PlayerCustomStoredPermissions.argtypes = [CString]
LIB.PlayerCustomStoredPermissions.restype = ctypes.c_uint32
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

LIB.GetPlayerByUUID.argtypes = [CString]
LIB.GetPlayerByUUID.restype = CString

LIB.GetPlayerByName.argtypes = [CString]
LIB.GetPlayerByName.restype = CString

LIB.ConsumePlayerChange.restype = CString
LIB.InterceptPlayerJustNextInput.argtypes = [CString, CString]
LIB.ConsumeChat.restype = CString

LIB.PlayerChat.argtypes = [CString, CString]
LIB.PlayerTitle.argtypes = [CString, CString, CString]
LIB.PlayerActionBar.argtypes = [CString, CString]
LIB.SetPlayerAbility.argtypes = [CString, CString]

LIB.ListenCommandBlock.argtypes = [CString]
LIB.PlaceCommandBlock.argtypes = [CString]


def ConsumeChat() -> "Chat":
    chatData = json.loads(toPyString(LIB.ConsumeChat()))
    return Chat(**chatData)


class Counter:
    def __init__(self, prefix: str) -> None:
        self.current_i = 0
        self.prefix = prefix

    def __next__(self) -> int:
        self.current_i += 1
        return f"{self.prefix}_{self.current_i}"


@dataclass
class ActionPermissionMap:
    ActionPermissionAttackMobs: bool = False
    ActionPermissionAttackPlayers: bool = False
    ActionPermissionBuild: bool = False
    ActionPermissionDoorsAndSwitches: bool = False
    ActionPermissionMine: bool = False
    ActionPermissionOpenContainers: bool = False
    ActionPermissionOperator: bool = False
    ActionPermissionTeleport: bool = False
    ActionPermissionUnknown: bool = False


@dataclass
class AdventureFlagsMap:
    AdventureFlagAllowFlight: bool = False
    AdventureFlagAutoJump: bool = False
    AdventureFlagFlying: bool = False
    AdventureFlagMuted: bool = False
    AdventureFlagNoClip: bool = False
    AdventureFlagWorldBuilder: bool = False
    AdventureFlagWorldImmutable: bool = False
    AdventureSettingsFlagsNoMvP: bool = False
    AdventureSettingsFlagsNoPvM: bool = False
    AdventureSettingsFlagsShowNameTags: bool = False


@dataclass
class Chat:
    Name: str = ""
    Msg: List[str] = ""
    Type: int = 1
    RawMsg: str = ""
    RawName: str = ""
    RawParameters: Optional[Any] = None
    Aux: Optional[Any] = None


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
    Parameters: Optional[List[Any]] = None


@dataclass
class CommandOutput:
    CommandOrigin: Optional[CommandOrigin] = None
    OutputType: int = 0
    SuccessCount: int = 0
    OutputMessages: Optional[List[OutputMessage]] = None
    DataSet: Optional[Any] = None

    @property
    def as_dict(self):
        return _unpack_command_output(self)


def unpackCommandOutput(jsonStr: Optional[str]) -> Optional[CommandOutput]:
    if jsonStr is None:
        return None
    commandOutputData = json.loads(jsonStr)
    commandOrigin = CommandOrigin(**commandOutputData["CommandOrigin"])
    dataset = None
    if (
        "DataSet" in commandOutputData.keys()
        and commandOutputData["DataSet"] is not None
        and commandOutputData["DataSet"] != ""
    ):
        dataset = json.loads(commandOutputData["DataSet"])
    outputMessages = []
    if (
        "OutputMessages" in commandOutputData.keys()
        and commandOutputData["OutputMessages"] is not None
        and commandOutputData["OutputMessages"] != ""
    ):
        outputMessagesData = commandOutputData["OutputMessages"]
        for outputMessageData in outputMessagesData:
            outputMessage = OutputMessage(
                Success=outputMessageData["Success"],
                Message=outputMessageData["Message"],
            )
            parameters = []
            if "Parameters" in outputMessageData.keys():
                parametersData = outputMessageData["Parameters"]
                for parameterData in parametersData:
                    try:
                        parameters.append(json.loads(parameterData))
                    except:
                        parameters.append(parameterData)
            outputMessage.Parameters = parameters
            outputMessages.append(outputMessage)
    return CommandOutput(
        CommandOrigin=commandOrigin,
        OutputType=commandOutputData["OutputType"],
        SuccessCount=commandOutputData["SuccessCount"],
        OutputMessages=outputMessages,
        DataSet=dataset,
    )


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
        return LIB.PlayerIsOP(self._c_uuid) == 1

    @property
    def online(self) -> bool:
        OmegaAvailable()
        return LIB.PlayerOnline(self._c_uuid) == 1

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
    def properties_flag(self) -> int:
        OmegaAvailable()
        return int(LIB.PlayerPropertiesFlag(self._c_uuid))

    @property
    def command_permission_level(self) -> int:
        OmegaAvailable()
        return int(LIB.PlayerCommandPermissionLevel(self._c_uuid))

    @property
    def action_permissions(self) -> int:
        OmegaAvailable()
        return int(LIB.PlayerActionPermissions(self._c_uuid))

    @property
    def op_permissions_level(self) -> int:
        OmegaAvailable()
        return int(LIB.PlayerOPPermissionLevel(self._c_uuid))

    @property
    def custom_permissions(self) -> int:
        OmegaAvailable()
        return int(LIB.PlayerCustomStoredPermissions(self._c_uuid))

    @property
    def ability_map(self) -> Tuple[ActionPermissionMap, AdventureFlagsMap]:
        OmegaAvailable()
        maps = json.loads(toPyString(LIB.PlayerGetAbilityString(self._c_uuid)))
        ActionPermissionMapData = maps["ActionPermissionMap"]
        AdventureFlagsMapData = maps["AdventureFlagsMap"]
        return ActionPermissionMap(**ActionPermissionMapData), AdventureFlagsMap(
            **AdventureFlagsMapData
        )

    @property
    def entity_runtime_id(self) -> int:
        OmegaAvailable()
        return int(LIB.PlayerEntityRuntimeID(self._c_uuid))

    @property
    def entity_metadata(self) -> any:
        OmegaAvailable()
        return json.loads(toPyString(LIB.PlayerEntityMetadata(self._c_uuid)))

    def say(self, msg: str):
        OmegaAvailable()
        LIB.PlayerChat(self._c_uuid, toCString(msg))

    def ask(self, hint: str) -> str:
        OmegaAvailable()
        self.say(hint)
        return self.parent._intercept_player_just_next_input(
            self._c_uuid
        ).RawMsg.strip()

    def title(self, title: str = "", subtitle: str = ""):
        # subtitle 只有在 title 给出时才能实际生效
        LIB.PlayerTitle(self._c_uuid, toCString(title), toCString(subtitle))

    def action_bar(self, msg: str):
        LIB.PlayerActionBar(self._c_uuid, toCString(msg))

    def query(self, conditions: Union[None, str, List[str]] = None) -> CommandOutput:
        query_str = f'querytarget @a[name="{self.name}"'
        if conditions is None:
            query_str += "]"
        elif isinstance(conditions, str):
            query_str += "," + conditions + "]"
        else:
            query_str += "," + ",".join(conditions) + "]"
        ret = self.parent.send_websocket_command_need_response(query_str)
        return ret

    def check_conditions(self, conditions: Union[None, str, List[str]] = None) -> bool:
        return self.query(conditions).SuccessCount > 0

    def get_pos(self) -> QueriedPlayerPos:
        pos = self.query().OutputMessages[0].Parameters[0][0]
        return QueriedPlayerPos(
            dimension=pos["dimension"],
            yRot=pos["yRot"],
            x=pos["position"]["x"],
            y=pos["position"]["y"],
            z=pos["position"]["z"],
        )

    def set_ability_map(
        self, action_permission: ActionPermissionMap, adventure_flag: AdventureFlagsMap
    ):
        jsonFlags = json.dumps(
            {
                "AdventureFlagsMap": adventure_flag.__dict__,
                "ActionPermissionMap": action_permission.__dict__,
            }
        )
        LIB.SetPlayerAbility(self._c_uuid, toCString(jsonFlags))

    def __repr__(self) -> str:
        return f"uuid={self.uuid},name={self.name},entity_unique_id={self.entity_unique_id},op={self.op},online={self.online}"

    def __del__(self):
        LIB.ReleaseBindPlayer(toCString(self._uuid))


class ConnectType(enum.Enum):
    Remote = "Remote"  # 连接到一个 neOmega Access Point
    Local = "Local"  # 在内部启动一个单独的 neOmega Core


class ThreadOmega:
    def __init__(
        self,
        connect_type: ConnectType,
        address: str = "tcp://localhost:24016",
        accountOption: AccountOptions = None,
    ) -> None:
        self._thread_counter = Counter("thread")
        self._running_threads: Dict[str, Thread] = {}
        if connect_type == ConnectType.Local:
            StartOmega(address, accountOption)
            Print.print_inf(f"Omega 接入点已启动, 在 {address} 开放接口")
        elif connect_type == ConnectType.Remote:
            ConnectOmega(address)

        # disconnect event
        self._omega_disconnected_lock = threading.Event()
        self._omega_disconnected_lock.clear()  # lock
        self._omega_disconnected_reason = ""

        # cmd events
        self._cmd_callback_retriever_counter = Counter("cmd_callback")
        self._omega_cmd_callback_events: Dict[str, Callable] = {}

        # packet listeners
        self._packet_listeners: Dict[str, List[Callable[[str, any], None]]] = {}

        # setup actions
        LIB.ListenAllPackets()  # make LIB listen to all packets and new packets will have eventType="MCPacket"
        mapping = json.loads(toPyString(LIB.GetPacketNameIDMapping()))
        self._packet_name_to_id_mapping: dict[str, int] = mapping
        self._packet_id_to_name_mapping = {}
        for packet_name, packet_id in self._packet_name_to_id_mapping.items():
            self._packet_id_to_name_mapping[packet_id] = packet_name
            self._packet_listeners[packet_name] = []

        LIB.ListenPlayerChange()
        self._player_change_listeners: List[Callable[[PlayerKit, str], None]] = []

        # get bot basic info (this info will not change so we need to get it only once)
        self._bot_basic_info = ClientMaintainedBotBasicInfo(
            **json.loads(toPyString(LIB.GetClientMaintainedBotBasicInfo()))
        )

        # player hooks
        self._bind_players: Dict[str, PlayerKit] = {}

        # player chat intercept callbacks
        self._player_chat_intercept_callback_retriever_counter = Counter(
            "player_chat_intercept"
        )
        self._player_chat_intercept_callback_events: Dict[str, Callable] = {}

        # chat
        LIB.ListenChat()
        self._player_chat_listeners: List[Callable[[Chat, PlayerKit], None]] = []
        self._specific_chat_listeners: Dict[
            str, List[Callable[[Chat, PlayerKit], None]]
        ] = {}

        # named command block msg
        self._name_command_block_msg_listeners: Dict[
            str, List[Callable[[Chat], None]]
        ] = {}

        # start routine
        self.start_new(self._react)

    def start_new(self, func: Callable, args: Iterable[Any] = ()):
        thread_i = next(self._thread_counter)

        def clean_up(*args):
            try:
                func(*args)
            except Exception:
                print(traceback.print_exc(limit=None, file=None, chain=True))
            finally:
                del self._running_threads[thread_i]

        t = Thread(target=clean_up, args=args)
        self._running_threads[thread_i] = t
        t.start()

    def _react(self):
        while True:
            eventType, retriever = EventPoll()
            if eventType == "OmegaConnErr":
                self._omega_disconnected_reason = toPyString(
                    LIB.ConsumeOmegaConnError()
                )
                self._omega_disconnected_lock.set()
            elif eventType == "CommandResponseCB":
                cmdResp = unpackCommandOutput(
                    toPyString(LIB.ConsumeCommandResponseCB())
                )
                self._omega_cmd_callback_events[retriever](cmdResp)
            elif eventType == "MCPacket":
                packetTypeName = retriever
                if packetTypeName == "":
                    print("'', ignored")
                listeners = self._packet_listeners.get(packetTypeName, [])
                if len(listeners) == 0:
                    LIB.OmitEvent()
                else:
                    ret = LIB.ConsumeMCPacket()
                    if toPyString(ret.convertError) != "":
                        raise ValueError(toPyString(ret.convertError))
                    else:
                        jsonPkt = json.loads(toPyString(ret.packetDataAsJsonStr))
                        for listener in listeners:
                            self.start_new(listener, (packetTypeName, jsonPkt))
            elif eventType == "PlayerChange":
                playerUUID = retriever
                if len(self._player_change_listeners) == 0:
                    LIB.OmitEvent()
                else:
                    action = toPyString(LIB.ConsumePlayerChange())
                    for callback in self._player_change_listeners:
                        self.start_new(
                            callback, (self._get_bind_player(playerUUID), action)
                        )

            elif eventType == "PlayerInterceptInput":
                chat = ConsumeChat()
                self._player_chat_intercept_callback_events[retriever](chat)

            elif eventType == "Chat":
                chat = ConsumeChat()
                if (
                    not self._player_chat_listeners
                    and not self._specific_chat_listeners.get(chat.Name)
                    and not self._specific_chat_listeners.get(chat.RawName)
                ):
                    LIB.OmitEvent()
                else:
                    player = self.get_player_by_name(chat.Name)
                    if not player:
                        name = chat.Name
                        if name in self._specific_chat_listeners.keys():
                            for callback in self._specific_chat_listeners[name]:
                                self.start_new(callback, (chat,))
                        if chat.Name != chat.RawName:
                            name = chat.RawName
                            if name in self._specific_chat_listeners.keys():
                                for callback in self._specific_chat_listeners[name]:
                                    self.start_new(callback, (chat,))
                    else:
                        for callback in self._player_chat_listeners:
                            self.start_new(callback, (chat, player))

            elif eventType == "NamedCommandBlockMsg":
                blockName = retriever
                listeners = self._name_command_block_msg_listeners[blockName]
                if len(listeners) == 0:
                    LIB.OmitEvent()
                else:
                    chat = ConsumeChat()
                    for l in listeners:
                        self.start_new(l, (chat,))

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

        def result_getter(timeout: int = -1) -> Any:
            lock.acquire(timeout=timeout)
            return ret[0]

        return result_setter, result_getter

    def send_websocket_command_need_response(
        self, cmd: str, timeout: int = -1
    ) -> Optional[CommandOutput]:
        setter, getter = self._create_lock_and_result_setter()
        retriever_id = next(self._cmd_callback_retriever_counter)
        self._omega_cmd_callback_events[retriever_id] = setter
        SendWebSocketCommandNeedResponse(cmd, retriever_id)
        res = getter(timeout=timeout)
        del self._omega_cmd_callback_events[retriever_id]
        return res

    def send_player_command_need_response(
        self, cmd: str, timeout: int = -1
    ) -> Optional[CommandOutput]:
        setter, getter = self._create_lock_and_result_setter()
        retriever_id = next(self._cmd_callback_retriever_counter)
        self._omega_cmd_callback_events[retriever_id] = setter
        SendPlayerCommandNeedResponse(cmd, retriever_id)
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
        self, requires: Optional[Union[List[str], str]] = None
    ) -> Union[Dict[str, int], int]:
        if requires is None:
            return {k: v for k, v in self._packet_name_to_id_mapping.items()}
        if isinstance(requires, list):
            return {k: self._packet_name_to_id_mapping[k] for k in requires}
        return self._packet_name_to_id_mapping[requires]

    def get_packet_id_to_name_mapping(
        self, requires: Optional[Union[List[int], int]] = None
    ) -> Union[Dict[int, str], str]:
        if requires is None:
            return {k: v for k, v in self._packet_id_to_name_mapping.items()}
        if isinstance(requires, list):
            return {k: self._packet_id_to_name_mapping[k] for k in requires}
        return self._packet_id_to_name_mapping[requires]

    def listen_packets(
        self, targets: Union[str, List[str]], callback: Callable[[str, Any], None]
    ):
        if isinstance(targets, str):
            targets = [targets]
        if isinstance(targets, int):
            targets = [f"{targets}"]
        translate_targets = {}
        for t in targets:
            hit = False
            if t == "all":
                translate_targets = {
                    k: True for k in self.get_packet_name_to_id_mapping().keys()
                }
                hit = True
            elif t.startswith("!"):
                rt = t[1:]
                if rt in self._packet_name_to_id_mapping.keys():
                    translate_targets[rt] = False
                    hit = True
                try:
                    packetID = int(rt)
                    packetType = self._packet_id_to_name_mapping(packetID)
                    translate_targets[packetType] = False
                    hit = True
                except:
                    pass
            else:
                if t in self._packet_name_to_id_mapping.keys():
                    translate_targets[t] = True
                    hit = True
                try:
                    packetID = int(t)
                    packetType = self.get_packet_id_to_name_mapping(packetID)
                    translate_targets[packetType] = True
                    hit = True
                except:
                    pass
            if not hit:
                raise ValueError(f"{t}")
        for k, v in translate_targets.items():
            if v:
                self._packet_listeners[k].append(callback)

    def construct_game_packet_bytes_in_json_as_is(
        self, packet_type: Union[int, str], content: Any
    ) -> tuple[int, bytes]:
        if isinstance(packet_type, str):
            packet_type = self.get_packet_name_to_id_mapping(packet_type)
        return packet_type, JsonStrAsIsGamePacketBytes(packet_type, json.dumps(content))

    def send_game_packet_in_json_as_is(
        self, packet_type: Union[int, str], content: Any
    ):
        if isinstance(packet_type, str):
            packet_type = self.get_packet_name_to_id_mapping(packet_type)
        OmegaAvailable()
        SendGamePacket(packet_type, json.dumps(content))

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

    def _get_bind_player(self, uuidStr: str) -> Optional[PlayerKit]:
        if uuidStr is None or uuidStr == "":
            return None
        if uuidStr in self._bind_players.keys():
            return self._bind_players[uuidStr]
        bind_player = PlayerKit(uuidStr, self)
        self._bind_players[uuidStr] = bind_player
        return bind_player

    def get_all_online_players(self):
        OmegaAvailable()
        playerUUIDS = json.loads(toPyString(LIB.GetAllOnlinePlayers()))
        return [self._get_bind_player(uuidStr) for uuidStr in playerUUIDS]

    def get_player_by_name(self, name: str) -> Optional[PlayerKit]:
        OmegaAvailable()
        playerUUID = toPyString(LIB.GetPlayerByName(toCString(name)))
        return self._get_bind_player(playerUUID)

    def get_player_by_uuid(self, uuidStr: str) -> Optional[PlayerKit]:
        OmegaAvailable()
        playerUUID = toPyString(LIB.GetPlayerByUUID(toCString(uuidStr)))
        return self._get_bind_player(playerUUID)

    def listen_player_change(self, callback: Callable[[PlayerKit, str], None]):
        for player in self.get_all_online_players():
            callback(player, "exist")
        self._player_change_listeners.append(callback)

    def _intercept_player_just_next_input(
        self, player_c_uuid: CString, timeout: int = -1
    ) -> Chat:
        setter, getter = self._create_lock_and_result_setter()
        retrieverID = next(self._player_chat_intercept_callback_retriever_counter)
        self._player_chat_intercept_callback_events[retrieverID] = setter
        LIB.InterceptPlayerJustNextInput(player_c_uuid, toCString(retrieverID))
        res = getter(timeout=timeout)
        del self._player_chat_intercept_callback_events[retrieverID]
        return res

    def listen_player_chat(self, callback: Callable[[Chat, PlayerKit], None]):
        self._player_chat_listeners.append(callback)

    def listen_specific_chat(
        self, specific_name: str, callback: Callable[[Chat], None]
    ):
        if not specific_name in self._specific_chat_listeners.keys():
            self._specific_chat_listeners[specific_name] = []
        self._specific_chat_listeners[specific_name].append(callback)

    def listen_named_command_block(
        self, command_block_name: str, callback: Callable[[Chat], None]
    ):
        if not command_block_name in self._name_command_block_msg_listeners.keys():
            self._name_command_block_msg_listeners[command_block_name] = []
        LIB.ListenCommandBlock(toCString(command_block_name))
        self._name_command_block_msg_listeners[command_block_name].append(callback)

    @staticmethod
    def place_command_block(place_option: CommandBlockPlaceOption):
        LIB.PlaceCommandBlock(toCString(json.dumps(place_option.__dict__)))

    def __del__(self):
        for t in self._running_threads.values():
            t.join()


def _unpack_command_output(c: CommandOutput):
    return {
        "CommandOrigin": {
            "Orogin": c.CommandOrigin.Origin,
            "UUID": c.CommandOrigin.UUID,
            "RequestID": c.CommandOrigin.RequestID,
            "PlayerUniqueID": c.CommandOrigin.PlayerUniqueID,
        },
        "OutputMessages": [_unpack_output_msgs(i) for i in c.OutputMessages],
        "OutputType": c.OutputType,
        "SuccessCOunt": c.SuccessCount,
        "DataSet": c.DataSet,
    }


def _unpack_output_msgs(c: OutputMessage):
    return {"Success": c.Success, "Message": c.Message, "Parameters": c.Parameters}
