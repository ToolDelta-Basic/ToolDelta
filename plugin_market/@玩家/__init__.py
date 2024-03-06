from tooldelta.plugin_load.injected_plugin import player_message
from tooldelta.plugin_load.injected_plugin.movent import (
    sendcmd,
    tellrawText,
    get_all_player,
)


__plugin_meta__ = {
    "name": "@玩家",
    "version": "0.0.2",
    "description": "当有人提及你时，会收到提醒",
    "author": "wling",
}


def find_mentions(text, player_list):
    return [player for player in player_list if f"@{player}" in text]


@player_message()
async def _(playername, message):
    # 如果文字包含@
    if "@" in message:
        mentioned_players = find_mentions(message, get_all_player())
        for i in mentioned_players:
            tellrawText(i, "§awling§eBot§r", "§l§a有人提及了你！")
            sendcmd(f"""/title {i} title §b§l有人提及了你""")
            sendcmd(f'''/title {i} subtitle "§7{playername} > §e§l{message}"''')
            sendcmd(
                r"""/execute """
                + i
                + """ ~ ~ ~ playsound block.bell.hit @s ~ ~ ~ 1 1 1"""
            )
