if 0:
    from ...source import Plugin, plugins, Frame, Config, Print

import websockets, json, threading, asyncio
from websockets.legacy.client import WebSocketClientProtocol, Connect as WSClient_Connect

plugins.checkSystemVersion((0, 1, 8))

class SuperServerLink(Plugin):
    name = "服服互通v3-Beta"
    version = (0, 0, 2)
    def __init__(self, frame: Frame):
        self.frame = frame
        self.game_ctrl = frame.get_game_control()
        CFG_STD = {
            "互通服务器IP地址列表(不可用时自动切换)": [r"%list", str],
            "互通配置": {
                "加入的频道名(不同频道相互不互通)": str,
                "此频道密码(没有请填空)": str,
                "此租赁服的频道名": str,
                "附加数据": {r"%any": [int, bool, float, str, type(None)]}
            }
        }
        CFG_DEF = {
            "互通服务器IP地址列表(不可用时自动切换)": ["47.101.71.192:24014"],
            "互通配置": {
                "加入的频道名(不同频道相互不互通)": "默认大区",
                "此频道密码(没有请填空)": "空",
                "此租赁服的频道名": "未命名租赁服",
                "附加数据": {}
            }
        }
        self.cfg = Config.getPluginConfigAndVersion(self.name, CFG_STD, CFG_DEF, self.version)

    def on_inject(self):
        self.frame.ClassicThread(asyncio.run, self.connection())

    async def find_conn(self):
        link_cfgs = self.cfg["互通配置"]
        headers = {"server_link_authmsg": {
            "Channel": link_cfgs["加入的频道名(不同频道相互不互通)"],
            "ServerName": link_cfgs["此租赁服的频道名"],
            "Password": link_cfgs["此频道密码(没有请填空)"],
            "ExtraDatas": link_cfgs["附加数据"]
        }}
        for conn_addr in self.cfg["互通服务器IP地址列表(不可用时自动切换)"]:
            try:
                async with WSClient_Connect("ws://" + conn_addr, extra_headers = headers) as websocket:
                    self.ws = websocket
                    self.conn_addr_avaliable = conn_addr
                    await self.connection()
            except:
                Print.print_war(f"连接服服互通服务器: {conn_addr} 失败, 切换到下一个")
        Print.print_err(f"全部服服互通线路都不可用, 不予启用")

    async def connection(self):
        Print.print_inf(f"连接到服服互通服务器: {self.conn_addr_avaliable}")
        
