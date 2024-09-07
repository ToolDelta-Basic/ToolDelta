"""
游戏交互实用方法
"""

import time
from typing import TYPE_CHECKING, Optional
from collections.abc import Callable
import json
import threading

from tooldelta.color_print import Print
from tooldelta.constants import PacketIDS

from .packets import Packet_CommandOutput
from .utils import Utils

if TYPE_CHECKING:
    from tooldelta import GameCtrl, ToolDelta

game_ctrl: Optional["GameCtrl"] = None
movent_frame: Optional["ToolDelta"] = None
player_waitmsg_cb: dict[str, Callable[[str], None]] = {}


def _create_lock_and_result_setter():
    """
    创建回调监听器与返回器
    """
    lock = threading.Lock()
    lock.acquire()
    ret = [None]

    def result_setter(result):
        ret[0] = result
        lock.release()

    def result_getter(timeout: float = -1):
        lock.acquire(timeout=timeout)
        return ret[0]

    return result_setter, result_getter


def _set_frame(my_Frame: "ToolDelta") -> None:
    """
    全局初始化框架

    参数:
        my_Frame: 要设置的框架对象
    """
    global movent_frame, game_ctrl  # pylint: disable=global-statement
    movent_frame = my_Frame
    game_ctrl = my_Frame.get_game_control()


def _get_game_ctrl() -> "GameCtrl":
    """检查 GameCtrl 是否可用"""
    if game_ctrl is None:
        raise ValueError("游戏控制框架 不可用")
    return game_ctrl


def _get_frame() -> "ToolDelta":
    """检查 GameCtrl 是否可用"""
    if movent_frame is None:
        raise ValueError("ToolDelta主框架 不可用")
    return movent_frame


def getTarget(sth: str, timeout: int = 5) -> list:
    """
    获取符合目标选择器实体的列表

    参数:
        sth: 目标选择器
        timeout: 超时时间，默认为 5 秒
    异常:
        ValueError: 指令返回超时，或者无法获取目标
    """
    game_ctrl = _get_game_ctrl()
    if not sth.startswith("@"):
        raise ValueError("我的世界目标选择器格式错误 (getTarget 必须使用目标选择器)")
    result = game_ctrl.sendcmd_with_resp(f"/testfor {sth}", timeout)
    if result.SuccessCount:
        result = result.OutputMessages[0].Parameters[0]
        return result.split(", ")
    if result.OutputMessages[0].Message == "commands.generic.syntax":
        raise ValueError(f"getTarget 目标选择器表达式错误：{sth}")
    return []


def getPos(target: str, timeout: float = 5) -> dict:
    """获取目标玩家的详细位置信息

    参数:
        targetNameToGet: 目标玩家的名称
        timeout: 超时时间（秒）。默认为 5 秒

    异常:
        ValueError: 当目标玩家不存在时抛出该异常
        ValueError: 当获取位置信息失败时抛出该异常
        AttributeError: 当获取玩家 UUID 失败时抛出该异常
    """
    game_ctrl = _get_game_ctrl()
    if (
        target not in game_ctrl.allplayers
        and not target.startswith("@")
        and target != game_ctrl.bot_name
    ):
        raise ValueError(f'玩家 "{target}" 不存在')
    resp = game_ctrl.sendcmd_with_resp(f'/querytarget @a[name="{target}"]', timeout)
    if not resp.OutputMessages[0].Success:
        raise ValueError(f"无法获取坐标信息：{resp.OutputMessages[0].Message}")
    parameter = json.loads(resp.OutputMessages[0].Parameters[0])
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
        return next(iter(result.values()))
    return result[target]


def getItem(target: str, itemName: str, itemSpecialID: int = -1) -> int:
    """
    获取玩家背包内指定的物品的数量
    参数:
        targetName (str): 玩家选择器 / 玩家名
        itemName (str): 物品 ID
        itemSpecialID (int): 物品特殊值，默认值 -1
    """
    game_ctrl = _get_game_ctrl()
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
    # TODO!!! 租赁服的/clear指令返回会乘以2
    return int(result.OutputMessages[0].Parameters[1]) // 2


def getPosXYZ(player, timeout: float = 30) -> tuple[float, float, float]:
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
    game_ctrl = _get_game_ctrl()
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


def getScore(scb_name: str, target: str, timeout: float = 30) -> int:
    """获取计分板对应分数
    参数:
        scb_name: 计分板名
        target: 目标选择器
        timeout: 超时时间

    异常:
        ValueError: 计分板错误

    返回:
        int: 计分板分数
    """
    game_ctrl = _get_game_ctrl()
    if target == "*" or scb_name == "*":
        raise ValueError("在此处无法使用 通配符 作为计分板分数获取目标")
    resp = game_ctrl.sendcmd_with_resp(
        f"/scoreboard players test {target} {scb_name} 0 0", timeout
    ).OutputMessages[0]
    if resp.Message == "commands.scoreboard.objectiveNotFound":
        raise ValueError(f"计分板 {scb_name} 未找到")
    if resp.Message == "commands.scoreboard.players.list.player.empty":
        raise ValueError(f"计分板项或玩家 {scb_name}:{target} 未找到")
    if resp.Message == "commands.scoreboard.players.score.notFound":
        raise ValueError(f"计分板项或玩家 {target} 在此计分板没有分数")
    if len(resp.Parameters) < 1:
        raise ValueError(
            f"计分板分数获取的Parameters获取异常: {resp.Message}: {resp.Parameters}"
        )
    return int(resp.Parameters[0])


def isCmdSuccess(cmd: str, timeout: float = 30):
    """
    获取命令执行成功与否的状态
    参数:
        cmd: MC 指令
        timeout: 超时时间
    返回:
        命令执行是否成功：bool
    """
    game_ctrl = _get_game_ctrl()
    res = game_ctrl.sendcmd_with_resp(cmd, timeout).SuccessCount
    return bool(res)


def sendcmd(
    cmd: str, waitForResp: bool = False, timeout: int = 30
) -> None | Packet_CommandOutput:
    r"""发送命令到游戏控制器，并可选择是否等待响应

    如果 waitForResp 为 False，则返回 None，否则返回 Packet_CommandOutput 对象

    参数:
        cmd: 要发送的命令
        waitForResp: 是否等待响应，默认为 False
        timeout: 等待响应的超时时间（秒）,默认为 30
    """
    game_ctrl = _get_game_ctrl()
    return game_ctrl.sendcmd(cmd, waitForResp, timeout)


def sendwscmd(
    cmd: str, waitForResp: bool = False, timeout: float = 30
) -> Packet_CommandOutput | None:
    """
    发送 WSCMD 命令到游戏控制器

    参数:
        cmd: 要发送的 WSCMD 命令
        waitForResp: 是否等待响应 默认为 False
        timeout: 超时时间（秒）默认为 30
    """
    game_ctrl = _get_game_ctrl()
    return game_ctrl.sendwscmd(cmd, waitForResp, timeout)


def sendwocmd(cmd: str) -> None:
    """
    发送 WO 命令到游戏控制器

    参数:
        cmd: 要发送的 WO 命令
    """
    game_ctrl = _get_game_ctrl()
    game_ctrl.sendwocmd(cmd)


def sendPacket(pktID: int, pkt: dict) -> None:
    """
    发送数据包给游戏控制器

    参数:
        pktID: 数据包 ID
        pkt: 数据包内容
    """
    game_ctrl = _get_game_ctrl()
    game_ctrl.sendPacket(pktID, pkt)


def rawText(playername: str, text: str) -> None:
    """
    向指定玩家发送原始文本消息

    参数:
        playername: 玩家名称
        text: 要发送的文本
    """
    game_ctrl = _get_game_ctrl()
    game_ctrl.say_to(playername, text)


def tellrawText(playername: str, title: str | None = None, text: str = "") -> None:
    """
    向指定玩家发送 tellraw 消息

    参数:
        playername: 玩家名称
        title: 标题文本（可选）
        text: 消息文本
    """
    game_ctrl = _get_game_ctrl()
    if title is None:
        game_ctrl.say_to(playername, text)
    else:
        game_ctrl.say_to(playername, f"<{title}§r> {text}")


def get_all_player() -> list:
    """获取所有玩家列表"""
    game_ctrl = _get_game_ctrl()
    return game_ctrl.allplayers


def is_op(playername: str) -> bool:
    """
    判断玩家是否为 OP

    参数:
        playername: 玩家名称
    """
    frame = _get_frame()
    return frame.launcher.is_op(playername)


def get_robotname() -> str:
    """获取机器人名称。"""
    game_ctrl = _get_game_ctrl()
    return game_ctrl.bot_name


def countdown(delay: float, msg: str | None = None) -> None:
    """
    倒计时函数

    参数:
        delay: 延迟时间，可以是整数或浮点数
        msg: 倒计时消息，可选参数，默认为"Countdown"
    """
    if msg is None:
        msg = "Countdown"
    delayStart = time.time()
    delayStop = delayStart + delay
    while delay >= 0:
        if delay >= 0:
            delay = delayStop - time.time()
        else:
            delay = 0
        Print.print_inf(f"{msg}: {delay:.2f}s", end="\r")
        time.sleep(0.01)
    print("", end="\n")


def getBlockTile(x: int, y: int, z: int) -> str:
    """
    获取指定坐标的方块的 ID

    参数:
        x: X 坐标
        y: Y 坐标
        z: Z 坐标
    """
    game_ctrl = _get_game_ctrl()
    res = game_ctrl.sendcmd_with_resp(f"/testforblock {x} {y} {z} air")
    if (
        res.SuccessCount
        or res.OutputMessages[0].Message == "commands.testforblock.outOfWorld"
    ):
        return "air"
    return res.OutputMessages[0].Parameters[4].strip("%tile.").strip(".name")


def getTickingAreaList() -> dict:
    """
    获取 tickingarea 列表

    异常:
        AttributeError: 获取 tickingarea 列表失败
    """
    result = {}
    cmd = sendwscmd("/tickingarea list all-dimensions", True)
    if cmd is not None:
        resultList = cmd.OutputMessages
    else:
        raise AttributeError("Failed to get the tickingarea list.")

    if resultList[0].Success is False:
        return result
    for tickareaData in resultList[1].Message.split("%dimension.dimensionName")[1:]:
        tickareaDimension = tickareaData.split(": \n")[0]
        tickareaList = tickareaData.split(": \n")[1].split("\n")
        for tickarea in tickareaList:
            if not tickarea:
                continue
            tickareaName = tickarea.split("- ", 1)[1].split(": ", 1)[0]
            tickareaPos = {
                "start": tickarea.split(" ")[2:5],
                "end": tickarea.split(" ")[6:9],
            }
            tickareaPos["start"].pop(1)
            tickareaPos["end"].pop(1)
            result[tickareaName] = {"dimension": tickareaDimension}
            result[tickareaName].update(tickareaPos)
    return result


def take_item_out_item_frame(pos: tuple[float, float, float]) -> None:
    """
    从物品展示框取出物品
    参数:
        position: 物品展示框的坐标 (x, y, z)
    返回:
        None
    """
    game_ctrl = _get_game_ctrl()
    BotPos: tuple[float, float, float] = getPosXYZ(game_ctrl.bot_name)
    game_ctrl.sendwocmd(
        f"tp {game_ctrl.bot_name} {str(int(pos[0])) + ' ' + str(int(pos[1])) + ' ' + str(int(pos[2]))}"
    )
    game_ctrl.sendPacket(PacketIDS.IDItemFrameDropItem, {"Position": pos})
    game_ctrl.sendwocmd(
        f"tp {game_ctrl.bot_name} {str(int(BotPos[0])) + ' ' + str(int(BotPos[1])) + ' ' + str(int(BotPos[2]))}"
    )


def __set_effect_while__(
    player_name: str, effect: str, level: int, particle: bool, icon_flicker: bool = True
) -> None:
    """
    内部方法: 设置玩家状态效果
    参数:
        player_name: 玩家名称 (String)
        effect: 效果 ID (String) 参考 EffectIDS 中内容
        level: 效果等级 (int) Max: 255
        particle: 是否显示粒子 (Boolean)
        icon_flicker: 是否使图标闪烁 (Boolean) [仅限ToolDelta运行时]
    返回:
        None
    """
    game_ctrl = _get_game_ctrl()
    command_prefix = f"/effect {player_name} {effect} "
    duration = "2" if icon_flicker else "1000000"
    command = f"{command_prefix}{duration} {level} {particle!s}"

    while True:
        result = game_ctrl.sendcmd_with_resp(command)
        if result.OutputMessages[0].Message == "commands.effect.success":
            time.sleep(1)
        else:
            break


def set_player_effect(
    player_name: str,
    effect: str,
    duration: int,
    level: int,
    particle: bool,
    icon_flicker: bool = True,
    timeout: float = 1.5,
) -> bool | ValueError:
    """
    设置玩家的状态效果

    参数:
        player_name: 玩家名称 (String) 或是选择器 (String)
        effect: 效果 ID (String) 参考 EffectIDS 中内容
        duration: 持续时间 (int) [为0代表永久(仅限ToolDelta运行时)] Max: 1000000
        level: 效果等级 (int) Max: 255
        particle: 是否显示粒子 (Boolean)
        icon_flicker: 是否使图标闪烁 (Boolean) [仅限ToolDelta运行时]
        timeout: 超时时间 (float) [可选]

    返回:
        Bool | ValueError: 是否设置成功
    """
    if level > 255:
        return ValueError(f"你提供的等级 ({level}) 太大了，它最高只能是 255。")
    if duration > 1000000:
        return ValueError(
            f"你提供的持续时间 ({duration}) 太大了，它最高只能是 1000000。"
        )  # type: ignore

    game_ctrl = _get_game_ctrl()
    command = f"/effect {player_name} {effect} {duration} {level} {particle!s}"

    if duration == 0:
        Utils.createThread(
            func=__set_effect_while__,
            args=(player_name, effect, level, particle, icon_flicker),
            usage=f"Set_Effect_Thread_{player_name}",
        )
        return True

    result = game_ctrl.sendcmd_with_resp(command, timeout=timeout)
    match result.OutputMessages[0].Message:
        case "commands.generic.noTargetMatch":
            return ValueError(
                f"没有与选择器匹配的目标! 玩家 {player_name} 可能并不存在。"
            )
        case "commands.effect.success":
            return True
        case _:
            return ValueError(f"未知错误: {result.OutputMessages[0].Message}")


def waitMsg(player: str, timeout: int = 30) -> str | None:
    """
    等待玩家在聊天栏发送消息, 并获取返回内容

    Args:
        player (str): 玩家名
        timeout (int): 超时等待时间

    Returns:
        result (str | None): 返回, 如果超时或玩家中途退出则返回None
    """
    s, g = _create_lock_and_result_setter()
    player_waitmsg_cb[player] = s
    try:
        res = g(timeout)
    finally:
        del player_waitmsg_cb[player]
    return res
