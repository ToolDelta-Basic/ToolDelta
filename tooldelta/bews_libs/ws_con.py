import asyncio
import uuid

import ujson
import websockets
from websockets.legacy.server import WebSocketServerProtocol


class Server:
    def __init__(self, port: int):
        self.port = port
        self.is_conn = False

    def set_event_cbs(self, on_inject, on_data_recv):
        self.on_inject = on_inject
        self.on_data_recv = on_data_recv

    async def wait_connection(self):
        async with websockets.serve(
            self.connect_once, "0.0.0.0", self.port
        ) as ws_server:
            self.ws_server = ws_server
            await asyncio.Future()

    async def connect_once(self, ws: WebSocketServerProtocol):
        if self.is_conn:
            await ws.close()
        else:
            self.ws = ws
            await self.handle(ws)

    async def handle(self, ws: WebSocketServerProtocol):
        while 1:
            self.on_data_recv(await ws.recv())

    async def send(self, request: dict):
        await self.ws.send(ujson.dumps(request, ensure_ascii=False))

    async def subscribe(self, event_name: str):
        await self.send(
            {"body": {"eventName": event_name}, "header": build_header("subscribe")}
        )

    async def unsubscribe(self, event_name):
        await self.send(
            {"body": {"eventName": event_name}, "header": build_header("unsubscribe")}
        )

    async def sendcmd(self, command: str):
        request = {
            "body": {"commandLine": command},
            "header": build_header("commandRequest"),
        }
        await self.send(request)
        return request["header"]["requestId"]


def build_header(message_purpose, request_id=None):
    if not request_id:
        request_id = str(uuid.uuid4())
    return {
        "requestId": request_id,
        "messagePurpose": message_purpose,
        "version": "1",
        "messageType": "commandRequest",
    }
