"实用函数"
import zipfile
from typing import TYPE_CHECKING
from ..color_print import Print
from ..packets import Packet_CommandOutput

if TYPE_CHECKING:
    from tooldelta import Frame, GameCtrl

game_ctrl: "GameCtrl" = None # type: ignore

__all__ = [
    "getTarget",
    "getPos",
    "getItem",
    "getScore",
    "isCmdSuccess"
]

# set_frame

def check_gamectrl_avali():
    "检查GameCtrl是否可用"
    if game_ctrl is None:
        raise ValueError("GameControl 不可用")

def set_frame(frame: "Frame"):
    "载入系统框架"
    global game_ctrl
    game_ctrl = frame.get_game_control()

# utils

def getTarget(sth: str, timeout: bool | int = 5) -> list:
    """
    获取符合目标选择器实体的列表

    参数:
        sth: 目标选择器
        timeout: 超时时间，默认为5秒
    异常:
        ValueError: 指令返回超时, 或者无法获取目标
    """
    check_gamectrl_avali()
    if not sth.startswith("@"):
        raise ValueError("我的世界目标选择器格式错误(getTarget必须使用目标选择器)")
    result = game_ctrl.sendwscmd(f"/testfor {sth}", True, timeout)
    if result is None:
        raise ValueError("获取目标失败")
    result = (
        result
        .OutputMessages[0]
        .Parameters
    )
    if result:
        result = result[0]
        return result.split(", ")
    raise ValueError("获取目标失败")

def getPos(targetNameToGet: str, timeout: float | int = 5) -> dict:
    """获取目标玩家的位置信息

    参数:
        targetNameToGet: 目标玩家的名称
        timeout: 超时时间（秒）。默认为5秒

    异常:
        ValueError: 当目标玩家不存在时抛出该异常
        ValueError: 当获取位置信息失败时抛出该异常
        AttributeError: 当获取玩家UUID失败时抛出该异常
    """
    check_gamectrl_avali()
    if targetNameToGet not in game_ctrl.allplayers or targetNameToGet.startswith("@"):
        raise ValueError(f"Player {targetNameToGet} does not exist.")
    result = game_ctrl.sendwscmd(
        f'/querytarget @a[name="{targetNameToGet}"]', True, timeout)
    if result is None:
        raise ValueError("Failed to get the position.")
    if not result.OutputMessages[0].Success:
        raise ValueError(
            f"Failed to get the position: {result.OutputMessages[0]}")
    parameter = result.OutputMessages[0].Parameters[0]
    if isinstance(parameter, str):
        raise ValueError("Failed to get the position.")
    result = {}

    if game_ctrl.players_uuid is None:
        raise AttributeError("Failed to get the players_uuid.")
    targetName = targetNameToGet
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
    if targetNameToGet == "@a":
        return result
    if len(result) != 1:
        raise ValueError("Failed to get the position.")
    if targetNameToGet.startswith("@a"):
        return list(result.values())[0]
    return result[targetNameToGet]

def getItem(targetName: str, itemName: str, itemSpecialID: int = -1) -> int:
    """
    获取玩家背包内指定的物品的数量
    参数:
        targetName (str): 玩家选择器 / 玩家名
        itemName (str): 物品ID
        itemSpecialID (int) = -1: 物品特殊值
    """
    if (
        (targetName not in game_ctrl.allplayers)
        and (targetName != game_ctrl.bot_name)
        and (not targetName.startswith("@a"))
    ):
        raise Exception("未找到目标玩家")
    result: Packet_CommandOutput = game_ctrl.sendwscmd(
        f"/clear {targetName} {itemName} {itemSpecialID} 0", True
    ) # type: ignore
    if result.OutputMessages[0].Message == "commands.generic.syntax":
        raise Exception("物品ID错误")
    if result.OutputMessages[0].Message == "commands.clear.failure.no.items":
        return 0
    return int(result.OutputMessages[0].Parameters[1])

def getPosXYZ(player, timeout=30) -> tuple[float, float, float]:
    """
    获取玩家的简略坐标值, 并以坐标三元元组返回
    参数:
        player (str): 玩家名
        timeout (int): 最长超时时间
    返回:
        tuple[float, float, float]
    """
    res = getPos(player, timeout=timeout)["position"]
    return res["x"], res["y"], res["z"]

def getScore(scoreboardNameToGet: str, targetNameToGet: str) -> int:
    """
    获取计分板分数
    参数:
        scoreboardNameToGet: 计分板名
        targetNameToGet: 获取分数的对象/目标选择器
    返回:
        分数: int
    异常:
        ValueError: 无法获取分数
    """
    if scoreboardNameToGet == "*":
        raise ValueError("暂不能使用 * 作为计分板参数")
    resultList = game_ctrl.sendwscmd(
        f"/scoreboard players list {targetNameToGet}", True
    ).OutputMessages # type: ignore
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
        raise Exception(f"获取计分板分数失败: {err}")

def isCmdSuccess(cmd: str, timeout=30):
    """
    获取命令执行成功与否的状态
    参数:
        cmd: MC指令
        timeout: 超时时间
    返回:
        命令执行是否成功: bool
    """
    res = game_ctrl.sendwscmd(cmd, True, timeout).SuccessCount # type: ignore
    return bool(res)