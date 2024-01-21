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

class ConnectionDeniedError(Exception):
    def __init__(self, msg, exc_tag):
        super().__init__(msg)
        self.msg = msg
        self.exc_tag = exc_tag

class RentalServer:
    def __init__(self, ws: WebSocketClientProtocol, server_name: str, in_channel: str):
        self.ws = ws
        self.name = server_name
        self.channel = in_channel
        self.ips = ws.remote_address

class SingleChannel:
    def __init__(self, name: str, members: dict[str, RentalServer], pwd: str | None = None, is_constant = False):
        self.members = members
        self.name = name
        self.pwd = pwd
        self.constant = is_constant
        self.update()

    def update(self):
        self.members_count = len(self.members)
    def join(self, client: RentalServer):
        self.members[client.ips] = client
        self.update()

    def exit(self, ips: str):
        if self.members.get(ips):
            del self.members[ips]
            self.update()
            return True
        else:
            return False

    async def broadcast(self, data_type, data, noip: str = ""):
        for ips, client in self.members.items():
            if ips != noip:
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
    my_addrs = ws.remote_address
    my_cli = None
    my_chan = None
    try:
        try:
            auth_msg = json.loads(data)
        except json.JSONDecodeError:
            raise ConnectionDeniedError("Not a valid json", "json.not.valid")
        if not test_is_valid_cli_name(auth_msg["ServerName"]):
            raise ConnectionDeniedError("租赁服名不合法", "rentalserver.name.invalid")
        my_cli = RentalServer(
            ws, auth_msg["ServerName"], auth_msg["Channel"]
        )
        pwdok = await join_chan(my_cli, auth_msg["Password"])
        if not pwdok:
            raise ConnectionDeniedError("频道密码错误", "channel.pwd.wrong")
        my_chan = get_chan(my_cli.channel)
        console_log(f"客户端 [#00FFFF]{my_cli.name}[#00FF00]({ws.remote_address[0]})[#FFFFFF] 已登录到频道 [#FFFF00]{my_cli.channel}")
        while 1:
            async for msg in ws:
                if len(msg) > MAX_MSG_STR_LEN:
                    raise ConnectionDeniedError("消息超出长度", "msg.too.long")
                msg_recv = json.loads(str(msg))
                msg_type = msg_recv["data_type"]
                msg_data = json.loads(msg_recv["data"])
                match msg_type:
                    case 0:
                        await my_chan.trans_chat_msg(
                            my_cli, msg_data["sender"], msg_data["msg"], my_cli.ips
                        )
                        console_log(f"[#FFFF00]{my_chan.name} [#00FFFF]{my_cli.name} [#FFFFFF]<{msg_data['sender']}> {msg_data['msg']}")
                    case 1 | 2:
                        if msg_type == 1:
                            console_log(f"[#FFFF00]{my_chan.name} [#00FFFF]{my_cli.name} [#999900]{msg_data['player']} 加入了游戏.")
                        else:
                            console_log(f"[#FFFF00]{my_chan.name} [#00FFFF]{my_cli.name} [#999900]{msg_data['player']} 退出了游戏.")
                        await my_chan.broadcast(1, {"server": my_cli, "player": msg_data["player"]}, my_cli.ips)
                    case 3:
                        await my_chan.broadcast(1, {"server": my_cli, "player": msg_data["player"]}, my_cli.ips)
                    case 6:
                        await my_chan.broadcast(1, msg_data, my_cli.ips)
    except ConnectionDeniedError as err:
        if my_cli is None:
            console_log(f"客户端 {my_addrs[0]} 连接被拒绝: {err.msg}")
            await ws.send(make_data_msg(7, {"msg": err.exc_tag}))
        else:
            console_log(f"客户端 [#00FFFF]{my_cli.name}[#00FF00]({my_addrs[0]}) 错误地断开连接: {err.msg}")
        await safe_close(ws)
        return
    except (ConnectionClosedOK, ConnectionClosedError):
        ...
    if my_chan is not None and my_cli is not None:
        console_log(f"客户端 [#FFFF00]{my_chan.name}:[#00FFFF]{my_cli.name}[#00FF00]({my_cli.ips[0]}) [#FFFFFF]已退出")
        await get_chan(my_cli.channel).broadcast(5, {"server": my_cli.name}, my_cli.ips)
        exit_chan(my_cli)
    else:
        console_log(f"客户端 {my_addrs[0]} 断开连接")

def console_log(msg: str, **print_args):
    msg = time.strftime("[%m-%d %H:%M] ") + msg
    _console_print(msg, style = None, **print_args)

def get_chan(chan: str):
    return channels[chan]

def make_data_msg(data_type, data):
    return json.dumps({"data_type": data_type, "data": json.dumps(data, ensure_ascii = False)}, ensure_ascii = False)

async def join_chan(cli: RentalServer, pwd: str | None = None):
    if channels.get(cli.channel):
        chan = get_chan(cli.channel)
        if chan.pwd is not None and chan.pwd != pwd:
            return False
        chan.join(cli)
    else:
        create_chan(cli.channel, cli, pwd)
    await get_chan(cli.channel).broadcast(4, cli.name)
    return True

async def safe_close(ws: WebSocketClientProtocol):
    try:
        await ws.close()
    except ConnectionClosedOK:...

def exit_chan(cli: RentalServer):
    chan = get_chan(cli.channel)
    chan.exit(cli.ips)
    if chan.members_count == 0 and not chan.constant:
        del channels[cli.channel]
        console_log(f"频道 [#FFFF00]{chan.name} [#FF7777]被自动注销.")

def create_chan(name: str, hostone: RentalServer | None, pwd: str | None = None):
    if hostone is not None:
        channels[name] = SingleChannel(name, {hostone.ips: hostone}, pwd)
    else:
        channels[name] = SingleChannel(name, {}, pwd, True)
    pwd_text = f", 密码:[#FF7777] {pwd}" if pwd is not None else ", 无密码"
    console_log(f"频道 [#FFFF00]{name} [#FFFFFF]被创建{pwd_text}")

def test_is_valid_cli_name(name: str):
    return len(name) in range(3, 15)

this_server = websockets.serve(connection, "localhost", 24014)
console_log("[#00FF00]服务器已就绪.")
create_chan("公共大区", None, None)
create_chan("生存大区", None, None)
create_chan("小游戏大区", None, None)
create_chan("数据化大区", None, None)
create_chan("空岛大区", None, None)
asyncio.get_event_loop().run_until_complete(this_server)
asyncio.get_event_loop().run_forever()
