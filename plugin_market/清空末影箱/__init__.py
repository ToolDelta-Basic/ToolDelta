from tooldelta.plugin_load.injected_plugin import player_message
from tooldelta.plugin_load.injected_plugin.movent import (
    tellrawText,
    sendcmd,
    getTarget,
    is_op,
)

__plugin_meta__ = {
    "name": "清空玩家末影箱",
    "version": "0.0.1",
    "author": "wling",
}


@player_message()
async def _(playername, message):
    if ".encl " not in message:
        return
    sendcmd(f"/tellraw {playername} §l§4ERROR§r §c指令不存在！")
    if is_op(playername):
        player_entity_clear = message.split(".encl ")[1]
        for i in getTarget("@a"):
            if player_entity_clear == i:
                for i in range(0, 27):
                    sendcmd(
                        f"/replaceitem entity {player_entity_clear} slot.enderchest {str(i)} air"
                    )
                tellrawText(playername, text="§l§a清空末影箱  成功")
                return

        tellrawText(playername, "§l§4ERROR§r", "§c目标玩家不存在！")
    else:
        tellrawText(playername, "§l§4ERROR§r", "§c权限不足.")
