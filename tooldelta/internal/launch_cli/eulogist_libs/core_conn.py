import uuid
import msgpack
import threading
import traceback
from collections.abc import Callable
from typing import Any
from websocket import WebSocketApp, WebSocket
from dataclasses import dataclass
from .... import utils
from ....packets import Packet_CommandOutput
from ....utils import fmts


class MessageType:
    CMD_SET_SERVER_PKTS = "SetServerListenPackets"
    CMD_SET_CLIENT_PKTS = "SetClientListenPackets"
    CMD_SET_SERVER_BLOCK_PKTS = "SetBlockingServerPackets"
    CMD_SET_CLIENT_BLOCK_PKTS = "SetBlockingClientPackets"
    MSG_SERVER_PKT = "ServerMCPacket"
    MSG_CLIENT_PKT = "ClientMCPacket"
    MSG_SET_BOT_BASIC_INFO = "SetBotBasicInfo"
    MSG_UPDATE_UQ = "UpdateUQ"


@dataclass
class Message:
    type: str
    content: Any

    def dumps(self):
        return {"type": self.type, "content": self.content}


@dataclass
class PlayerUQ:
    name: str
    uuid: str
    xuid: str
    uniqueID: int
    abilities: dict


class Eulogist:
    """赞颂者启动器核心"""

    packet_listener: Callable[[int, dict], None] | None = None
    connected = False
    bot_data_ready_event = threading.Event()
    uq_data_ready_event = threading.Event()
    launch_event = threading.Event()
    exit_event = threading.Event()

    def __init__(self) -> None:
        self.command_cbs: dict[bytes, Callable[[dict], None]] = {}
        self.bot_name = ""
        self.bot_unique_id = 0
        self.bot_runtime_id = 0
        self.bot_uuid = ""
        self.uqs: dict[str, PlayerUQ] = {}
        self.client_packet_handler: Callable[[int, dict], None] = lambda x, y: None

    @staticmethod
    def make_conn(
        ipaddr: str,
        on_conn: Callable[[WebSocket], None],
        on_msg: Callable[[WebSocket, str], None],
        on_close: Callable[[WebSocket, Any, Any], None],
    ):
        return WebSocketApp(
            ipaddr, on_open=on_conn, on_message=on_msg, on_close=on_close
        )

    def start(self):
        self.conn = self.make_conn(
            "ws://127.0.0.1:10132", self.on_conn, self.on_msg, self.on_clos
        )
        self.conn.run_forever()

    def on_conn(self, ws: WebSocket):
        self.connected = True
        self.on_wait()

    @utils.thread_func("等待赞颂者连接初始化")
    def on_wait(self):
        # 需要一些时间
        fmts.print_inf("正在接收机器人基本信息...")
        self.bot_data_ready_event.wait()
        fmts.print_inf("正在接收在线玩家权限能力信息...")
        self.uq_data_ready_event.wait()
        self.launch_event.set()

    def on_msg(self, ws: WebSocket, msg_raw: str):
        msgdata = msgpack.unpackb(msg_raw)
        # print(msgdata)
        try:
            self.handler(Message(msgdata["type"], msgdata["content"]))
        except Exception:
            fmts.print_err("赞颂者发送的消息解析失败")
            fmts.print_err(traceback.format_exc())

    def on_clos(self, ws: WebSocket, _, _2):
        self.connected = False
        fmts.print_inf("赞颂者和 ToolDelta 断开连接")
        self.exit_event.set()

    def set_listen_server_packets(self, pkIDs: list[int]):
        self.send(Message(MessageType.CMD_SET_SERVER_PKTS, {"PacketsID": pkIDs}))

    def set_listen_client_packets(self, pkIDs: list[int]):
        self.send(Message(MessageType.CMD_SET_CLIENT_PKTS, {"PacketsID": pkIDs}))

    def set_blocking_server_packets(self, pkIDs: list[int]):
        self.send(Message(MessageType.CMD_SET_SERVER_BLOCK_PKTS, {"PacketsID": pkIDs}))

    def set_blocking_client_packets(self, pkIDs: list[int]):
        self.send(Message(MessageType.CMD_SET_CLIENT_BLOCK_PKTS, {"PacketsID": pkIDs}))

    def sendPacket(self, pkID: int, pk: dict):
        pk_bytes: Any = msgpack.packb(pk)
        self.send(
            Message(MessageType.MSG_SERVER_PKT, {"ID": pkID, "Content": pk_bytes})
        )

    def sendClientPacket(self, pkID: int, pk: dict):
        pk_bytes: Any = msgpack.packb(pk)
        self.send(
            Message(MessageType.MSG_CLIENT_PKT, {"ID": pkID, "Content": pk_bytes})
        )

    def sendcmd(self, cmd: str):
        u = uuid.uuid4()
        self.sendPacket(
            77,
            {
                "CommandLine": cmd,
                "CommandOrigin": {
                    "Origin": 0,
                    "UUID": u.bytes,
                    "RequestID": u.bytes,
                    "PlayerUniqueID": 0,
                },
                "Internal": False,
                "Version": 0x24,
                "UnLimited": False,
            },
        )
        return u

    def sendwscmd(self, cmd: str):
        u = uuid.uuid4()
        self.sendPacket(
            77,
            {
                "CommandLine": cmd,
                "CommandOrigin": {
                    "Origin": 5,
                    "UUID": u.bytes,
                    "RequestID": u.bytes,
                    "PlayerUniqueID": 0,
                },
                "Internal": False,
                "Version": 0x24,
                "UnLimited": False,
            },
        )
        return u

    def sendcmd_with_resp(
        self, cmd: str, timeout: float = 5
    ) -> Packet_CommandOutput | None:
        ud = self.sendcmd(cmd)
        getter, setter = utils.create_result_cb(dict)
        self.command_cbs[ud.bytes] = setter
        res = getter(timeout)
        del self.command_cbs[ud.bytes]
        if res is None:
            return None
        else:
            return Packet_CommandOutput(res)

    def sendwscmd_with_resp(
        self, cmd: str, timeout: float = 5
    ) -> Packet_CommandOutput | None:
        ud = self.sendwscmd(cmd)
        getter, setter = utils.create_result_cb(dict)
        self.command_cbs[ud.bytes] = setter
        res = getter(timeout)
        del self.command_cbs[ud.bytes]
        if res is None:
            return None
        else:
            return Packet_CommandOutput(res)

    def sendwocmd(self, cmd: str):
        self.sendPacket(
            140,
            {"CommandLine": cmd, "SuppressOutput": False},
        )

    @utils.thread_func("赞颂者消息处理", utils.ToolDeltaThread.SYSTEM)
    def handler(self, msg: Message) -> None:
        try:
            match msg.type:
                case MessageType.MSG_SET_BOT_BASIC_INFO:
                    self.bot_name = msg.content["bot_name"]
                    self.bot_uuid = msg.content["uuid"]
                    self.bot_unique_id = msg.content["bot_entity_unique_id"]
                    self.bot_runtime_id = msg.content["bot_runtime_id"]
                    self.bot_data_ready_event.set()
                case MessageType.MSG_UPDATE_UQ:
                    self.uqs = {k: PlayerUQ(**v) for k, v in msg.content.items()}
                    self.uq_data_ready_event.set()
                case MessageType.MSG_SERVER_PKT:
                    pkID = msg.content["ID"]
                    pk = msg.content["Content"]
                    if pkID == 79:
                        pkUUID: bytes = pk["CommandOrigin"]["UUID"]
                        if pkUUID in self.command_cbs.keys():
                            self.command_cbs[pkUUID](pk)
                        # else:
                        #    fmts.print_war(f"无效命令返回UUID: {pkUUID} ({self.command_cbs}) {id(self.command_cbs)}")
                    if self.packet_listener:
                        self.packet_listener(pkID, pk)
                case MessageType.MSG_CLIENT_PKT:
                    self.client_packet_handler(
                        msg.content["ID"], msg.content["Content"]
                    )
                case _:
                    fmts.print_war(f"未知数据传输类型: {msg.type}")
        except Exception as err:
            fmts.print_err(f"处理赞颂者通信出错: {err}")
            fmts.print_err(traceback.format_exc())

    def send(self, msg: Message):
        self.conn.send(msgpack.packb(msg.dumps())) # type: ignore
