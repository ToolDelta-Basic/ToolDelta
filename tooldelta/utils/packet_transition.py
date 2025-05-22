from typing import TYPE_CHECKING
from ..constants import TextType
from . import fmts
from .basic import to_plain_name

if TYPE_CHECKING:
    from .. import ToolDelta


def get_playername_and_msg_from_text_packet(
    frame: "ToolDelta", pkt: dict
) -> tuple[str, str, bool] | tuple[None, None, bool]:
    """
    将 Text 数据包转换为玩家名与消息

    Args:
        frame (ToolDelta): ToolDelta 框架
        pkt (dict): 数据包

    Returns:
        tuple[str, str, bool] | tuple[None, None, bool]: 玩家名, 消息, 是否确认为玩家消息
    """
    msg: str = pkt["Message"]
    sender_name = ""

    if (extraData := pkt["NeteaseExtraData"]) and len(extraData) > 1:
        sender_uqID = int(extraData[1])
        if sender_player := frame.get_players().getPlayerByUniqueID(sender_uqID):
            sender_name = sender_player.name
    if len(sender_name) == 0 and (sender_xuid := pkt["XUID"]):
        if sender_player := frame.get_players().getPlayerByXUID(sender_xuid):
            sender_name = sender_player.name

    match pkt["TextType"]:
        case TextType.TextTypeTranslation:
            return None, None, False
        case TextType.TextTypeChat | TextType.TextTypeWhisper:
            src_name = pkt["SourceName"]
            playername = sender_name or src_name
            if src_name == "":
                # /me 消息
                msg_list = msg.split(" ")
                if len(msg_list) >= 3:
                    playername = to_plain_name(playername or msg_list[1])
                    msg = " ".join(msg_list[2:])
                else:
                    fmts.print_war(
                        f"[internal] 无法获取发言中的玩家名与消息: {playername}: {msg}"
                    )
                    return None, None, False
            return playername, msg, sender_name != ""
        case TextType.TextTypeAnnouncement:
            # /say 消息
            src_name = pkt["SourceName"]
            playername = sender_name or pkt["SourceName"]
            msg = msg.removeprefix(f"[{src_name}] ")
            return playername, msg, sender_name != ""
        case TextType.TextTypeObjectWhisper:
            # /tellraw 消息
            return None, None, False
        case _:
            return None, None, False
