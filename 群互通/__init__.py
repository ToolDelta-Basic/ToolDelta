import json
import traceback
from typing import Any, Dict
import requests
import flask
import re
from tooldelta.color_print import Print
from tooldelta.plugin_load.injected_plugin.movent import get_all_player, rawText, tellrawText
from tooldelta.plugin_load.injected_plugin import (
    player_message,
    player_message_info,init
)
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

__plugin_meta__ = {
    "name": "群互通",
    "version": "0.0.1",
    "author": "wling",
}

connect_link: str = "http://localhost:4311"
recvPort:int = 44522
togroup_id: int = 966016220
groupformat:str = "群 §7<[用户昵称]> [消息]"

async def sendToGroup(group_id: int, message: str, is_cq: bool = False) -> int:
    # 使用QQ群机器人程序的api发送信息.
    if len(message) >= 200:
        message = message[:200]+"[已省略]"
    # 构建json发送post
    result = {
        "group_id": group_id,
        "message": message,
        "auto_escape": is_cq
    }
    # 发送
    try:
        raw_data = requests.post(
            connect_link+"/send_group_msg", json=result, timeout=3)
        if raw_data.status_code == 404:
            raise Exception("发送失败,code: 404")
        if 200 != raw_data.status_code:
            raise Exception("发送失败,code: "+str(raw_data.status_code))
        return json.loads(raw_data.text)["data"]["message_id"]
    except Exception as e:
        Print.print_war(f"发送信息失败: {e}")
        raise e


async def sendToPrivate(user_id: int, group_id: int, message: str, is_cq: bool = False) -> int:
    # 使用QQ群机器人程序的api发送信息.
    if len(message) >= 200:
        message = message[:200]+"[已省略]"
    # 构建json发送post
    result = {
        "user_id": user_id,
        "group_id": group_id,
        "message": message,
        "auto_escape": is_cq
    }
    # 发送
    try:
        raw_data = requests.post(
            connect_link+"/send_private_msg", json=result, timeout=3)
        if raw_data.status_code == 404:
            raise Exception("发送失败,code: 200")
        if 200 != raw_data.status_code:
            raise Exception("发送失败,code: "+str(raw_data.status_code))
        return json.loads(raw_data.text)["data"]["message_id"]
    except Exception as e:
        Print.print_war(f"发送信息失败: {traceback.format_exc()}")


@player_message()
async def _(playermessage: player_message_info):
    playername = playermessage.playername
    msg = playermessage.message
    if playername in get_all_player():
        try:
            await sendToGroup(togroup_id, f"{playername}说: {msg}")
        except Exception as e:
            Print.print_war(f"发送信息失败: {traceback.format_exc()}")
            return


class ArgsReplacement:
    def __init__(self, kw: Dict[str, Any]):
        self.kw = kw

    def replaceTo(self, __sub: str):
        for k, v in self.kw.items():
            if k in __sub:
                __sub = __sub.replace(k, str(v))
        return __sub

@init()
async def run_flask():
    app = flask.Flask(__name__)

    @app.route("/", methods=["POST"])
    def recv_msg():
        recv = flask.request.get_json()
        if recv["post_type"] == "message" or recv["post_type"] == "message_sent":
            send_msg = recv["raw_message"]
            send_user = recv['sender']['nickname']
            send_user_qqid = recv['sender']['user_id']
            send_type = recv['message_type']
            if send_type == "group" and recv['group_id'] == togroup_id:
                msg = ArgsReplacement(
                        {"[用户昵称]": send_user, "[消息]": send_msg, "[用户QQ号]": send_user_qqid}).replaceTo(groupformat)

                rawText("@a",msg)
        return "OK"
    app.run(debug=False, host="0.0.0.0", port=recvPort)
