"注入式执行函数"

import time
from typing import TYPE_CHECKING, Any, Optional
from ...color_print import Print
from ...packets import Packet_CommandOutput
from ...game_utils import getTarget, getPos

if TYPE_CHECKING:
    from tooldelta.frame import ToolDelta, GameCtrl


def check_avaliable(sth: "GameCtrl") -> Optional[AttributeError]:
    """
    检查给定的 "GameCtrl" 对象是否可用

    参数:
        sth: 要检查的 "GameCtrl" 对象
    """
    if sth is None:
        raise AttributeError(f"无法使用 {sth.__class__.__name__}, 因为其还未被初始化")


game_control: "GameCtrl"
movent_frame: "ToolDelta"


def set_frame(my_Frame: "ToolDelta") -> None:
    """
    全局初始化框架

    参数:
        my_Frame: 要设置的框架对象
    """
    global movent_frame, game_control  # pylint: disable=global-statement
    movent_frame = my_Frame
    game_control = my_Frame.get_game_control()


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
    check_avaliable(game_control)
    return game_control.sendcmd(cmd, waitForResp, timeout)


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
    check_avaliable(game_control)
    return game_control.sendwscmd(cmd, waitForResp, timeout)


def sendwocmd(cmd: str) -> None:
    """
    发送 WO 命令到游戏控制器

    参数:
        cmd: 要发送的 WO 命令
    """
    check_avaliable(game_control)
    game_control.sendwocmd(cmd)


def sendPacket(pktID: int, pkt: str) -> None:
    """
    发送数据包给游戏控制器

    参数:
        pktID: 数据包 ID
        pkt: 数据包内容
    """
    check_avaliable(game_control)
    game_control.sendPacket(pktID, pkt)


def rawText(playername: str, text: str) -> None:
    """
    向指定玩家发送原始文本消息

    参数:
        playername: 玩家名称
        text: 要发送的文本
    """
    game_control.say_to(playername, text)


def tellrawText(playername: str, title: str | None = None, text: str = "") -> None:
    """
    向指定玩家发送 tellraw 消息

    参数:
        playername: 玩家名称
        title: 标题文本（可选）
        text: 消息文本
    """
    if title is None:
        game_control.say_to(playername, text)
    else:
        game_control.say_to(playername, f"<{title}§r> {text}")


def get_all_player() -> list:
    """获取所有玩家列表"""
    check_avaliable(game_control)
    return game_control.allplayers


def is_op(playername: str) -> bool | None:
    """
    判断玩家是否为 OP

    参数:
        playername: 玩家名称
    """
    check_avaliable(game_control)
    if playername not in get_all_player():
        return False
    # 检测框架是否为"Frame"NeOmg
    if movent_frame.launcher.is_op is not None:
        return movent_frame.launcher.is_op(playername)
    return None


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
    return None


def get_robotname() -> str:
    """获取机器人名称。"""
    check_avaliable(game_control)
    return game_control.bot_name


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
    获取指定坐标的方块的 ID

    参数:
        x: X 坐标
        y: Y 坐标
        z: Z 坐标
    """
    res = sendwscmd(f"/testforblock {x} {y} {z} air", True)
    if isinstance(res, type(None)):
        raise ValueError("Failed to get the block.")
    if res.SuccessCount:
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
