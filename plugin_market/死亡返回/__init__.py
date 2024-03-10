import os
import time
import ujson as json
from 维度传送 import tp
from tooldelta.plugin_load.injected_plugin import player_message, player_death
from tooldelta.plugin_load.injected_plugin.movent import (
    get_all_player,
    tellrawText,
    getPos,
)


__plugin_meta__ = {
    "name": "死亡返回",
    "version": "0.0.5",
    "author": "wling/7912",
}


LOG_DEATH_TIME = 30  # 记录最小频率 (秒)
plugin_path = r"插件数据文件/死亡返回"
config_path = plugin_path + r"/死亡位置.json"
os.makedirs(plugin_path, exist_ok=True)
if not os.path.isfile(config_path):
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump({}, f, indent=4, ensure_ascii=False)


def translateDim(dimension):
    if dimension == 0:
        return "主世界"
    if dimension == 1:
        return "地狱"
    if dimension == 2:
        return "末地"
    raise ValueError("维度只能是0, 1或2.")


@player_message()
async def _(playername, msg):
    if msg == ".backdeath":
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if playername not in data:
            tellrawText(f'@a[name="{playername}"]', "§l§4ERROR§r", "§c未找到记录.")
            return
        deathData = data[playername]
        tp(
            f'@a[name="{playername}"]',
            x=deathData["position"]["x"],
            y=deathData["position"]["y"],
            z=deathData["position"]["z"],
            dimension=deathData["dimension"],
        )
        tellrawText(
            f'@a[name="{playername}"]',
            "§l死亡点记录§r",
            f"已传送到上次死亡点: [§l{translateDim(deathData['dimension'])}§r, (§l{deathData['position']['x']}§r, §l{deathData['position']['y']}§r, §l{deathData['position']['z']}§r)]."
        )
        data[playername] = deathData
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)


@player_death()
async def _(playername, killer):
    if playername not in get_all_player():
        return
    deathTime = int(time.time())
    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if playername not in data:
        data[playername] = {}
    deathData_old = data[playername]
    if deathData_old:
        deathTimeDelta = deathTime - deathData_old["time"]
        if deathTimeDelta < LOG_DEATH_TIME:
            tellrawText(
                f'@a[name="{playername}"]',
                "§l§4ERROR§r",
                f"§c时间间隔过短, 未保存此次记录. (冷却时间: §l{LOG_DEATH_TIME - deathTimeDelta}§r§cs)"
            )
            return

    deathData = getPos(playername)
    deathData["time"] = deathTime
    data[playername] = deathData
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    tellrawText(
        f'@a[name="{playername}"]',
        "§l死亡点记录§r",
        f"已记录死亡点: [§l{translateDim(deathData['dimension'])}§r, (§l{deathData['position']['x']}§r, §l{deathData['position']['y']}§r, §l{deathData['position']['z']}§r)], 输入§l.backdeath§r返回.",
    )
