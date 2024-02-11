from tooldelta.injected_plugin import player_message, sendcmd, tellrawText


def find_mentions(text, player_list):
    return [player for player in player_list if f"@{player}" in text]


@player_message()
async def _(message, playername):
    # 如果文字包含@
    if "@" in message:
        mentioned_players = find_mentions(message, globals.allplayer)
        for i in mentioned_players:
            tellrawText(i, "§awling§eBot§r", "§l§a有人提及了你！")
            sendcmd(f"""/title {i} title §b§l有人提及了你""")
            sendcmd(f'''/title {i} subtitle "§7{playername} > §e§l{message}"''')
            sendcmd(
                r"""/execute """
                + i
                + """ ~ ~ ~ playsound block.bell.hit @s ~ ~ ~ 1 1 1"""
            )
