import time
import ujson as json
from typing import TYPE_CHECKING, Any
from typing import Optional
from tooldelta.color_print import Print
from tooldelta.packets import Packet_CommandOutput
if TYPE_CHECKING:
    from tooldelta.frame import Frame, GameCtrl


def check_avaliable(sth: "GameCtrl") -> Optional[AttributeError]:
    """
    检查给定的 "GameCtrl" 对象是否可用

    参数:
        sth: 要检查的 "GameCtrl" 对象
    """
    if sth is None:
        raise AttributeError(f"无法使用 {sth.__class__.__name__}, 因为其还未被初始化")


game_control: "GameCtrl"
movent_frame: "Frame"


def set_frame(my_Frame: "Frame") -> None:
    """
    全局初始化框架

    参数:
        my_"Frame": 要设置的框架对象
    """
    global movent_frame, game_control  # pylint: disable=global-statement
    movent_frame = my_Frame
    game_control = my_Frame.get_game_control()


def sendcmd(
    cmd: str, waitForResp: bool = False, timeout: int = 30
) -> None | Packet_CommandOutput:
    """发送命令到游戏控制器，并可选择是否等待响应\n
    如果 waitForResp 为 False,则返回 None,否则返回 Packet_CommandOutput 对象

    参数:
        cmd: 要发送的命令
        waitForResp: 是否等待响应,默认为 False
        timeout: 等待响应的超时时间（秒）,默认为 30
    """
    check_avaliable(game_control)
    if game_control.sendcmd is None:
        raise AttributeError(f"无法使用 {game_control.__class__.__name__}, 因为其还未被初始化")
    return game_control.sendcmd(cmd, waitForResp, timeout)


def sendwscmd(
    cmd: str, waitForResp: bool = False, timeout: int | float = 30
) -> Packet_CommandOutput:
    """
    发送WSCMD命令到游戏控制器

    参数:
        cmd: 要发送的WSCMD命令
        waitForResp: 是否等待响应 默认为False
        timeout: 超时时间（秒） 默认为30
    """
    check_avaliable(game_control)
    return game_control.sendwscmd(cmd, waitForResp, timeout)


def sendwocmd(cmd: str) -> None:
    """
    发送WO命令到游戏控制器

    参数:
        cmd: 要发送的WO命令
    """
    check_avaliable(game_control)
    game_control.sendwocmd(cmd)


def sendPacket(pktID: int, pkt: str) -> None:
    """
    发送数据包给游戏控制器

    参数:
        pktID: 数据包ID
        pkt: 数据包内容
    """
    check_avaliable(game_control)
    game_control.sendPacket(pktID, pkt)


def sendfbcmd(cmd: str) -> None:
    """向FastBuilder发送命令\n
    在除FastBuilder外的其他启动器上不可用

    参数:
        cmd: 要发送的命令。
    """
    check_avaliable(game_control)
    game_control.sendfbcmd(cmd)


def rawText(playername: str, text: str) -> None:
    """
    向指定玩家发送原始文本消息

    参数:
        playername: 玩家名称
        text: 要发送的文本
    """
    sendcmd(r"""/tellraw %s {"rawtext":[{"text":"%s"}]}""" % (playername, text))


def tellrawText(playername: str, title: str | None = None, text: str = "") -> None:
    """
    向指定玩家发送tellraw消息

    参数:
        playername: 玩家名称
        title: 标题文本（可选）
        text: 消息文本
    """
    if title is None:
        sendcmd(r"""/tellraw %s {"rawtext":[{"text":"§r%s"}]}""" % (playername, text))
    else:
        sendcmd(
            r"""/tellraw %s {"rawtext":[{"text":"<%s> §r%s"}]}"""
            % (
                playername,
                title,
                text,
            )
        )


def get_all_player() -> list:
    """获取所有玩家列表"""
    check_avaliable(game_control)
    return game_control.allplayers


def is_op(playername: str) -> bool | None:
    """
    判断玩家是否为OP

    参数:
        playername: 玩家名称
    """
    check_avaliable(game_control)
    if playername not in get_all_player():
        return False
    # 检测框架是否为"Frame"NeOmg
    if movent_frame.launcher.is_op is not None:
        return movent_frame.launcher.is_op(playername)


def getTarget(sth: str, timeout: bool | int = 5) -> list:
    """
    获取符合目标选择器实体的列表

    参数:
        sth: 目标选择器
        timeout: 超时时间，默认为5秒
    """
    check_avaliable(game_control)
    if not sth.startswith("@"):
        raise Exception("Minecraft Target Selector is not correct.")
    result = (
        game_control.sendwscmd(f"/testfor {sth}", True, timeout)
        .OutputMessages[0]
        .Parameters
    )
    if result:
        result = result[0]
        return result.split(", ")
    return []


def find_key_from_value(dic: dict, val: Any) -> Optional[Any]:
    """
    从字典中根据值查找对应的键

    参数:
        dic: 目标字典
        val: 目标值
    """
    for k, v in dic.items():
        if v == val:
            return k


def get_robotname() -> str | None:
    """获取机器人名称。"""
    check_avaliable(game_control)
    return game_control.bot_name


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
    check_avaliable(game_control)
    if targetNameToGet not in get_all_player() or targetNameToGet.startswith("@"):
        raise ValueError(f"Player {targetNameToGet} does not exist.")
    result = sendwscmd(f'/querytarget @a[name="{targetNameToGet}"]', True, timeout)
    if not result.OutputMessages[0].Success:
        raise ValueError(f"Failed to get the position: {result.OutputMessages[0]}")
    parameter = result.OutputMessages[0].Parameters[0]
    if isinstance(parameter, str):
        resultList = json.loads(parameter)
    else:
        resultList = parameter
    result = {}

    if game_control.players_uuid is None:
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


def countdown(delay: int | float, msg: str | None = None) -> None:
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
    获取指定坐标的方块的ID

    参数:
        x: X坐标
        y: Y坐标
        z: Z坐标
    """
    res = sendwscmd(f"/testforblock {x} {y} {z} air", True)
    if res.SuccessCount:
        return "air"
    print(res.OutputMessages[0].Parameters)
    return res.OutputMessages[0].Parameters[4].strip("%tile.").strip(".name")


def getTickingAreaList() -> dict | AttributeError:
    """
    获取 tickingarea 列表

    异常:
        AttributeError: 获取 tickingarea 列表失败
    """
    result = {}
    cmd = sendcmd("/tickingarea list all-dimensions", True)
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
