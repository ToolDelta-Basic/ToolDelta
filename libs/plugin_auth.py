import websockets, asyncio, rsa, base64
from websockets.legacy.client import WebSocketClientProtocol
import time, random

async def GetAuthServerCallback(ws, data: str):
    await ws.send(data)
    return await ws.recv()
    
def GetRandomBytes(times):
    return "".join([chr(random.randint(10, 120)) for _ in range(times)]).encode('ascii')

def EncryptDataWithEnc():
    pub_key, pri_key = rsa.newkeys(256, poolsize=4)
    return f"{pub_key.n}|{pub_key.e}|", pub_key, pri_key

async def AuthAndGetPluginsList(ip = "127.0.0.1:23000"):
    enc_str, pub_key, pri_key = EncryptDataWithEnc()
    async with websockets.connect("ws://" + ip) as ws_server:
        await ws_server.send()