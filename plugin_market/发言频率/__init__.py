import time
from tooldelta.frame import Config
from tooldelta.plugin_load.injected_plugin import player_left, player_message
from tooldelta.plugin_load.injected_plugin.movent import get_all_player, is_op
from tooldelta import plugins


__plugin_meta__ = {
    "name": "发言频率",
    "version": "0.0.1",
    "author": "wling/7912",
}

STD_BAN_CFG = {"时间内": int, "在时间内达到多少条": int}
DEFAULT_BAN_CFG = {
    "时间内": 3,
    "在时间内达到多少条": 6,
}

cfg, cfg_version = Config.getPluginConfigAndVersion(
    __plugin_meta__["name"],
    STD_BAN_CFG,
    DEFAULT_BAN_CFG,
    __plugin_meta__["version"].split("."),
)

playerMsgTimeDict = {}
msgSendNunMaxPerTime = cfg["时间内"]
msgSendNumMax = cfg["在时间内达到多少条"]
ban_plugin = plugins.get_plugin_api("封禁系统")
ban = ban_plugin.ban


@player_message()
async def _(playername: str, *arg):
    if is_op(playername) and playername in get_all_player():
        msgSendTime = time.time()
        if playername not in playerMsgTimeDict:
            playerMsgTimeDict[playername] = []
        for i in playerMsgTimeDict[playername][:]:
            if i <= msgSendTime - msgSendNunMaxPerTime:
                playerMsgTimeDict[playername].remove(i)
        playerMsgTimeDict[playername].append(msgSendTime)
        if len(playerMsgTimeDict[playername]) >= msgSendNumMax:
            # 生成时间戳，比现在多五分钟，传参给
            # ban(playername, int(time.time()) + 300, "发信息过快")
            ban(playername, int(time.time()) + 300, "发信息过快")
            playerMsgTimeDict[playername] = []


@player_left()
async def _(playername: str):
    if playername in playerMsgTimeDict:
        del playerMsgTimeDict[playername]
