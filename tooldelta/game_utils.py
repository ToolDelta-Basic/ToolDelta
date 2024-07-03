"""
游戏交互实用方法

Methods:
    getTarget (sth, timeout): 获取符合目标选择器实体的列表
    getPos (targetNameToGet, timeout): 获取目标玩家的详细位置信息
    getItem (targetName, itemName, itemSpecialID): 获取玩家背包内指定的物品的数量
    getPosXYZ (player, timeout=30): 获取玩家的简略坐标值，并以坐标三元元组返回
    getScore (scoreboardNameToGet, targetNameToGet): 获取计分板分数
    isCmdSuccess (cmd: str, timeout=30): 获取命令执行成功与否的状态
"""

from typing import TYPE_CHECKING

import json

from .packets import Packet_CommandOutput

if TYPE_CHECKING:
    from tooldelta import GameCtrl, ToolDelta

game_ctrl: "GameCtrl" = None  # type: ignore

# set_frame


def _check_gamectrl_avali():
    """检查 GameCtrl 是否可用"""
    if game_ctrl is None:
        raise ValueError("GameControl 不可用")


def _set_frame(frame: "ToolDelta"):
    """载入系统框架"""
    # skipcq: PYL-W0603
    global game_ctrl
    game_ctrl = frame.get_game_control()


# utils


def getTarget(sth: str, timeout: int = 5) -> list:
    """
    获取符合目标选择器实体的列表

    参数:
        sth: 目标选择器
        timeout: 超时时间，默认为 5 秒
    异常:
        ValueError: 指令返回超时，或者无法获取目标
    """
    _check_gamectrl_avali()
    if not sth.startswith("@"):
        raise ValueError("我的世界目标选择器格式错误 (getTarget 必须使用目标选择器)")
    result = game_ctrl.sendcmd_with_resp(f"/testfor {sth}", timeout)
    if result.SuccessCount:
        result = result.OutputMessages[0].Parameters[0]
        return result.split(", ")
    if result.OutputMessages[0].Message == "commands.generic.syntax":
        raise ValueError(f"getTarget 目标选择器表达式错误：{sth}")
    return []


def getPos(target: str, timeout: float | int = 5) -> dict:
    """获取目标玩家的详细位置信息

    参数:
        targetNameToGet: 目标玩家的名称
        timeout: 超时时间（秒）。默认为 5 秒

    异常:
        ValueError: 当目标玩家不存在时抛出该异常
        ValueError: 当获取位置信息失败时抛出该异常
        AttributeError: 当获取玩家 UUID 失败时抛出该异常
    """
    _check_gamectrl_avali()
    if (
        target not in game_ctrl.allplayers
        and not target.startswith("@")
        and target != game_ctrl.bot_name
    ):
        raise ValueError(f'玩家 "{target}" 不存在')
    result = game_ctrl.sendcmd_with_resp(f'/querytarget @a[name="{target}"]', timeout)
    if not result.OutputMessages[0].Success:
        raise ValueError(f"无法获取坐标信息：{result.OutputMessages[0].Message}")
    parameter = json.loads(result.OutputMessages[0].Parameters[0])
    if isinstance(parameter, str):
        raise ValueError("无法获取坐标信息：" + parameter)
    result = {}
    if game_ctrl.players_uuid is None:
        raise AttributeError("无法获取玩家 UUID 表")
    targetName = target
    x = (
        parameter[0]["position"]["x"]
        if parameter[0]["position"]["x"] >= 0
        else parameter[0]["position"]["x"] - 1
    )
    y = parameter[0]["position"]["y"] - 1.6200103759765
    z = (
        parameter[0]["position"]["z"]
        if parameter[0]["position"]["z"] >= 0
        else parameter[0]["position"]["z"] - 1
    )
    position = {
        "x": float(f"{x:.2f}"),
        "y": float(f"{y:.2f}"),
        "z": float(f"{z:.2f}"),
    }
    dimension = parameter[0]["dimension"]
    yRot = parameter[0]["yRot"]
    result[targetName] = {
        "dimension": dimension,
        "position": position,
        "yRot": yRot,
    }
    if target == "@a":
        return result
    if len(result) != 1:
        raise ValueError("获取坐标失败")
    if target.startswith("@a"):
        return list(result.values())[0]
    return result[target]


def getItem(target: str, itemName: str, itemSpecialID: int = -1) -> int:
    """
    获取玩家背包内指定的物品的数量
    参数:
        targetName (str): 玩家选择器 / 玩家名
        itemName (str): 物品 ID
        itemSpecialID (int): 物品特殊值，默认值 -1
    """
    if (
        (target not in game_ctrl.allplayers)
        and (target != game_ctrl.bot_name)
        and (not target.startswith("@a"))
    ):
        raise ValueError("未找到目标玩家")
    result: Packet_CommandOutput = game_ctrl.sendcmd_with_resp(
        f"/clear {target} {itemName} {itemSpecialID} 0"
    )
    if result.OutputMessages[0].Message == "commands.generic.syntax":
        raise ValueError("物品 ID 错误")
    if result.OutputMessages[0].Message == "commands.clear.failure.no.items":
        return 0
    return int(result.OutputMessages[0].Parameters[1])


def getPosXYZ(player, timeout: int | float = 30) -> tuple[float, float, float]:
    """
    获取玩家的简略坐标值，并以坐标三元元组返回
    参数:
        player (str): 玩家名
        timeout (int): 最长超时时间
    返回:
        tuple[float, float, float]
    """
    res = getPos(player, timeout=timeout)["position"]
    return res["x"], res["y"], res["z"]


def getMultiScore(scoreboardNameToGet: str, targetNameToGet: str) -> int | dict:
    """
    获取单个或多个计分板分数项
    参数:
        scoreboardNameToGet: 计分板名
        targetNameToGet: 获取分数的对象/目标选择器
    返回:
        分数：int
    异常:
        ValueError: 无法获取分数
    """
    resultList = game_ctrl.sendcmd_with_resp(
        f"/scoreboard players list {targetNameToGet}"
    ).OutputMessages
    result = {}
    result2 = {}
    for i in resultList:
        Message = i.Message
        if Message == r"commands.scoreboard.players.list.player.empty":
            continue
        if Message == r"§a%commands.scoreboard.players.list.player.count":
            targetName = i.Parameters[1][1:]
        elif Message == "commands.scoreboard.players.list.player.entry":
            if targetName == "commands.scoreboard.players.offlinePlayerName":
                continue
            scoreboardName = i.Parameters[2]
            targetScore = int(i.Parameters[0])
            if targetName not in result:
                result[targetName] = {}
            result[targetName][scoreboardName] = targetScore
            if scoreboardName not in result2:
                result2[scoreboardName] = {}
            result2[scoreboardName][targetName] = targetScore
    if not (result or result2):
        raise Exception("获取计分板分数失败")
    try:
        if targetNameToGet == "*" or targetNameToGet.startswith("@"):
            return result2[scoreboardNameToGet]
        if scoreboardNameToGet == "*":
            return result[targetNameToGet]
        return result[targetNameToGet][scoreboardNameToGet]
    except KeyError as err:
        raise Exception(f"获取计分板分数失败：{err}")


def getScore(scb_name: str, target: str, timeout=30) -> int:
    _check_gamectrl_avali()
    if target == "*" or scb_name == "*":
        raise ValueError("在此处无法使用 通配符 作为计分板分数获取目标")
    resp = game_ctrl.sendcmd_with_resp(
        f"/scoreboard players test {target} {scb_name} 0 0", timeout
    ).OutputMessages[0]
    if resp.Message == "commands.scoreboard.objectiveNotFound":
        raise ValueError(f"计分板 {scb_name} 未找到")
    if resp.Message == "commands.scoreboard.players.list.player.empty":
        raise ValueError(f"计分板项或玩家 {target} 未找到")
    if resp.Message == "commands.scoreboard.players.score.notFound":
        raise ValueError(f"计分板项或玩家 {target} 在此计分板没有分数")
    return int(resp.Parameters[0])


def isCmdSuccess(cmd: str, timeout=30):
    """
    获取命令执行成功与否的状态
    参数:
        cmd: MC 指令
        timeout: 超时时间
    返回:
        命令执行是否成功：bool
    """
    res = game_ctrl.sendcmd_with_resp(cmd, timeout).SuccessCount
    return bool(res)
