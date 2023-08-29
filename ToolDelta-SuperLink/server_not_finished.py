import websockets
import json
import asyncio
import rich.console
import time
from websockets.legacy.client import WebSocketClientProtocol
from websockets.exceptions import *

# 联机大厅信息转发协议格式
# 0 chatmsg 1 playerjoin 2 playerleave 3 playerbc 4 cliconn 5 clidisconn
# 6 custom_msg, 7 err_msg, 8 console_msg

MAX_MSG_STR_LEN = 2048
_console_print = rich.console.Console().print

class ConnectionDeniedError(Exception):...

class RentalServer:
    def __init__(self, ws: WebSocketClientProtocol, server_name: str, in_channel: str):
        self.ws = ws
        self.name = server_name
        self.channel = in_channel
        self.ip = ws.remote_address[0]

class SingleChannel:
    def __init__(self, name: str, members: dict[str, RentalServer]):
        self.members = members
        self.name = name
        self.update()

    def update(self):
        self.members_count = len(self.members)

    def join(self, client: RentalServer):
        self.members[client.ip] = client

    def exit(self, ip: str):
        if self.members.get(ip):
            del self.members[ip]
            self.update()
            return True
        else:
            return False
        
    async def broadcast(self, data_type, data, noip: str = ""):
        for ip, client in self.members.items():
            if ip != noip:
                await client.ws.send(make_data_msg(data_type, data))  

    async def trans_chat_msg(self, from_cli: RentalServer, sender: str, msg: str, noip: str = ""):
        for ip in self.members.keys():
            if ip != noip:
                await self.send_chat_msg(ip, from_cli, sender, msg)

    async def send_chat_msg(self, ip: str, from_cli: RentalServer, sender: str, msg: str):
        msg = make_data_msg(
            0, {"channel": from_cli.channel, "server": from_cli.name, "sender": sender, "msg": msg}
        )
        await self.members[ip].ws.send(msg)

channels: dict[str, SingleChannel] = {}

async def connection(ws: WebSocketClientProtocol, path):
    console_log(f"客户端 [#00FF00]{ws.remote_address[0]}[#FFFFFF] 请求连入, 正在获取基本信息")
    data = await ws.recv()
    my_addr = ws.remote_address[0]
    my_cli = None
    try:
        try:
            auth_msg = json.loads(data)
        except json.JSONDecodeError:
            raise ConnectionDeniedError("json not valid")
        if not test_is_valid_cli_name(auth_msg["ServerName"]):
            raise ConnectionDeniedError("Invalid name.")
        my_cli = RentalServer(
            ws, auth_msg["ServerName"], auth_msg["Channel"]
        )
        await join_chan(my_cli)
        my_chan = get_chan(my_cli.channel)
        console_log(f"客户端 [#00FFFF]{my_cli.name}[#00FF00]({ws.remote_address[0]})[#FFFFFF] 已登录到频道 [#FFFF00]{my_cli.channel}")
        while 1:
            async for msg in ws:
                if len(msg) > MAX_MSG_STR_LEN:
                    raise ConnectionDeniedError("Msg is too long.")
                msg_recv = json.loads(str(msg))
                msg_type = msg_recv["data_type"]
                msg_data = json.loads(msg_recv["data"])
                match msg_type:
                    case 0:
                        await my_chan.trans_chat_msg(
                            my_cli, msg_data["sender"], msg_data["msg"]
                        )
                    case 1:
                        console_log(f"[#FFFF00]{my_chan} [#00FFFF]{my_cli.name} [#999900]{msg_data['player']}[#FFFFFF]: {msg_data['msg']}")
                        await my_chan.broadcast(1, {"server": my_cli, "player": msg_data["player"]}, my_cli.ip)
                    case 2 | 3:
                        await my_chan.broadcast(1, {"server": my_cli, "player": msg_data["player"]}, my_cli.ip)
                    case 6:
                        await my_chan.broadcast(1, msg_data, my_cli.ip)
    except ConnectionDeniedError as err:
        if my_cli is None:
            console_log(f"客户端 {my_addr} 错误地断开连接: {err}")
        else:
            console_log(f"客户端 [#00FFFF]{my_cli.name}[#00FF00]({my_addr}) 错误地断开连接: {err}")
        #await ws.send(make_data_msg(7, {"msg": str(err)}))
        await safe_close(ws)
        return
    except (ConnectionClosedOK, ConnectionClosedError):
        ...
    if my_chan is not None:
        console_log(f"客户端 [#FFFF00]{my_chan.name}:[#00FFFF]{my_cli.name}[#00FF00]({my_cli.ip}) [#FFFFFF]已退出")
        await get_chan(my_cli.channel).broadcast(5, {"server": my_cli.name}, my_cli.ip)
        exit_chan(my_cli)
    else:
        console_log(f"客户端 {my_addr} 断开连接")

def console_log(msg: str, **print_args):
    msg = time.strftime("[%m-%d %H:%M] ") + msg
    _console_print(msg, style = None)

def get_chan(chan: str):
    return channels[chan]

def make_data_msg(data_type, data):
    return json.dumps({"data_type": data_type, "data": json.dumps(data, ensure_ascii = False)}, ensure_ascii = False)

async def join_chan(cli: RentalServer):
    if channels.get(cli.channel):
        get_chan(cli.channel).join(cli)
    else:
        create_chan(cli.channel, cli)
    await get_chan(cli.channel).broadcast( 4, cli.name)

async def safe_close(ws: WebSocketClientProtocol):
    try:
        await ws.close()
    except ConnectionClosedOK:...

def exit_chan(cli: RentalServer):
    get_chan(cli.channel).exit(cli.ip)
    if get_chan(cli.channel).members_count == 0:
        del channels[cli.channel]

def create_chan(name: str, hostone: RentalServer):
    channels[name] = SingleChannel(name, {hostone.ip: hostone})

def test_is_valid_cli_name(name: str):
    return len(name) in range(3, 15)

this_server = websockets.serve(connection, "localhost", 24014)
console_log("服务器已就绪.")
asyncio.get_event_loop().run_until_complete(this_server)
asyncio.get_event_loop().run_forever()
