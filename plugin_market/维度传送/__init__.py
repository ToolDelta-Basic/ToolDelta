import asyncio
from tooldelta.plugin_load.injected_plugin import init
from tooldelta import Print
from tooldelta.plugin_load.injected_plugin.movent import (
    get_robotname,
    getBlockTile,
    getPos,
    getTarget,
    sendcmd,
    countdown,
    getTickingAreaList,
)

__plugin_meta__ = {
    "name": "维度传送",
    "version": "0.0.1",
    "author": "wling/7912",
}


def tp(target, *, x, y, z, dimension):
    if dimension == 0:
        sendcmd(
            f"/execute @e[type=armor_stand, name=td_overworld, c=1] ~ ~ ~ /tp {target} {x} {y} {z}"
        )
        return
    if dimension == 1:
        sendcmd(
            f"/execute @e[type=armor_stand, name=td_the_nether, c=1] ~ ~ ~ /tp {target} {x} {y} {z}"
        )
        return
    if dimension == 2:
        sendcmd(
            f"/execute @e[type=armor_stand, name=td_the_end, c=1] ~ ~ ~ /tp {target} {x} {y} {z}"
        )
        return
    raise ValueError("dimension参数仅可以是0, 1或2.")


@init()
async def _() -> None:
    Print.print_load("§e正在配置跨维度传送.")
    robotDim = getPos(get_robotname())["dimension"]
    if robotDim != 0:
        Print.print_load("§e机器人不在主世界, 正在传到主世界.")
        while getPos(get_robotname())["dimension"] != 0:
            sendcmd("/tp @r", True)
            countdown(5, "等待世界加载")
            Print.print_war("§e机器人不在主世界, 正在重新传到主世界.")
        sendcmd("/tp @s 77912 1 77912", True)
        await asyncio.sleep(3)
        robotDim = getPos(get_robotname())["dimension"]
        if getBlockTile(77912, 0, 77912) != "seaLantern":
            sendcmd("/fill 77904 0 77904 77919 5 77919 sealantern 0 hollow")
        if robotDim == 1:
            if getBlockTile(77905, 1, 77905) != "portal":
                sendcmd("/setblock 77905 1 77905 portal")
            sendcmd("/tp @s 77905 0 77905")
            cout = 0
            while getPos(get_robotname())["dimension"] != 0:
                await asyncio.sleep(0.1)
                if cout == 5:  # 试错次数
                    Print.print_err("§c无法将机器人传到主世界.")
                    return
        if robotDim == 2:
            if getBlockTile(77905, 1, 77905) != "end_portal":
                sendcmd("/setblock 77905 1 77905 end_portal")
            sendcmd("/tp @s 77905 0 77905")
            cout = 0
            while getPos(get_robotname())["dimension"] != 0:
                await asyncio.sleep(0.1)
                if cout == 5:  # 试错次数
                    Print.print_err("§c无法将机器人传到主世界.")
                    return
        sendcmd("/tp @s 100000 100000 100000", True)
        Print.print_suc("§a成功将机器人传到主世界.")
    Print.print_load("§e检测常加载区块数量.")
    tickareaList = getTickingAreaList()
    tickareaAvaliableNum = 10 - len(tickareaList)
    for tickareaName in ["td_overworld", "td_the_nether", "td_the_end"]:
        if tickareaName in tickareaList:
            tickareaAvaliableNum += 1
        else:
            countdown(5, "等待世界加载")

    if tickareaAvaliableNum < 3:
        Print.print_err("§c可创建的常加载区块数量不够.")
        return

    for dimension in range(3):
        if dimension == 0:
            if "td_the_end" not in tickareaList:
                Print.print_load("§e主世界常加载不存在, 正在添加.")
                sendcmd("/tickingarea add 77904 0 77904 77919 0 77919 td_overworld")
                sendcmd("/tp @s 77912 1 77912", True)
                await asyncio.sleep(2)
                if getBlockTile(77912, 0, 77912) != "seaLantern":
                    sendcmd("/fill 77904 0 77904 77919 5 77919 sealantern 0 hollow")
            if not getTarget("@e[type=armor_stand, name=td_overworld]"):
                Print.print_load("§e主世界盔甲架不存在, 正在生成.")
                if getBlockTile(77912, 0, 77912) != "seaLantern":
                    sendcmd("/fill 77904 0 77904 77919 5 77919 sealantern 0 hollow")
                sendcmd("/summon armor_stand td_overworld 77912 1 77912")
                await asyncio.sleep(1)
        elif dimension == 1:
            if "td_the_nether" not in tickareaList:
                Print.print_load("§e地狱常加载不存在, 正在添加.")
                sendcmd("/tp @s 77912 1 77912", True)
                await asyncio.sleep(2)
                if getBlockTile(77905, 1, 77905) != "portal":
                    sendcmd("/setblock 77905 1 77905 portal")
                await asyncio.sleep(1)
                sendcmd("/tp @s 77905 0 77905")
                await asyncio.sleep(1)
                await asyncio.sleep(1)
                sendcmd("/tickingarea add 77904 0 77904 77919 0 77919 td_the_nether")
                await asyncio.sleep(1)
                sendcmd("/tp @s 77912 1 77912", True)
                await asyncio.sleep(1)
                if getBlockTile(77912, 0, 77912) != "seaLantern":
                    sendcmd("/fill 77904 0 77904 77919 5 77919 sealantern 0 hollow")
            if not getTarget("@e[type=armor_stand, name=td_the_nether]"):
                Print.print_load("§e地狱盔甲架不存在, 正在生成.")
                if getPos(get_robotname())["dimension"] == 0:
                    sendcmd("/tp @s 77912 1 77912", True)
                    await asyncio.sleep(2)
                    if getBlockTile(77905, 1, 77905) != "portal":
                        sendcmd("/setblock 77905 1 77905 portal")
                        await asyncio.sleep(1)
                    sendcmd("/tp @s 77905 1 77905")
                    await asyncio.sleep(1)
                    sendcmd("/tp @s 77905 2 77905")
                    await asyncio.sleep(1)
                    sendcmd("/tp @s 77905 1 77905")
                    await asyncio.sleep(1)
                    await asyncio.sleep(1)
                await asyncio.sleep(2)
                sendcmd("/tp @s 77912 1 77912", True)
                await asyncio.sleep(2)
                if getBlockTile(77912, 0, 77912) != "seaLantern":
                    sendcmd("/fill 77904 0 77904 77919 5 77919 sealantern 0 hollow")
                sendcmd("/summon armor_stand td_the_nether 77912 1 77912")
            if getPos(get_robotname())["dimension"] == 1:
                sendcmd("/tp @s @e[type=armor_stand, name=td_overworld]", True)
        await asyncio.sleep(1)
        if dimension == 2:
            if "td_the_end" not in tickareaList:
                Print.print_load("§e末地常加载不存在, 正在添加.")
                sendcmd("/tp @s 77912 1 77912", True)
                await asyncio.sleep(2)
                if getBlockTile(77918, 1, 77918) != "end_portal":
                    sendcmd("/setblock 77918 1 77918 end_portal")
                    await asyncio.sleep(1)
                sendcmd("/tp @s 77918 0 77918")
                await asyncio.sleep(1)
                await asyncio.sleep(1)
                sendcmd("/tickingarea add 77904 0 77904 77919 0 77919 td_the_end")
                await asyncio.sleep(1)
                sendcmd("/tp @s 77912 1 77912", True)
                await asyncio.sleep(2)
                if getBlockTile(77912, 0, 77912) != "seaLantern":
                    sendcmd("/fill 77904 0 77904 77919 5 77919 sealantern 0 hollow")
            if not getTarget("@e[type=armor_stand, name=td_the_end]"):
                Print.print_load("§e末地盔甲架不存在, 正在生成.")
                if getPos(get_robotname())["dimension"] == 0:
                    sendcmd("/tp @s 77912 1 77912", True)
                    await asyncio.sleep(1)
                    if getBlockTile(77918, 1, 77918) != "end_portal":
                        sendcmd("/setblock 77918 1 77918 end_portal")
                    await asyncio.sleep(1)
                sendcmd("/tp @s 77918 0 77918")
                await asyncio.sleep(1)
                await asyncio.sleep(1)
                sendcmd("/tp @s 77912 1 77912", True)
                await asyncio.sleep(2)
                if getBlockTile(77912, 0, 77912) != "seaLantern":
                    sendcmd("/fill 77904 0 77904 77919 5 77919 sealantern 0 hollow")
                sendcmd("/summon armor_stand td_the_end 77912 1 77912")
        if getPos(get_robotname())["dimension"] == 2:
            sendcmd("/tp @s @e[type=armor_stand, name=td_overworld]", True)

    Print.print_suc("§a成功配置跨维度传送.")
