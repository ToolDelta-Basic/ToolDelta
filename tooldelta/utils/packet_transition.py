from typing import TYPE_CHECKING
from ..constants import TextType
from . import fmts
from .basic import to_plain_name

if TYPE_CHECKING:
    from .. import ToolDelta


def get_playername_and_msg_from_text_packet(
    frame: "ToolDelta", pkt: dict
) -> tuple[str, str] | tuple[None, None]:
    msg: str = pkt["Message"]
    sender_name = ""
    if xuid := pkt["XUID"]:
        sender_player = frame.get_players().getPlayerByXUID(xuid)
        if sender_player is not None:
            sender_name = sender_player.name
    match pkt["TextType"]:
        case TextType.TextTypeTranslation:
            return None, None
        case TextType.TextTypeChat | TextType.TextTypeWhisper:
            src_name = pkt["SourceName"]
            playername = sender_name or to_plain_name(src_name)
            if src_name == "":
                # /me 消息
                msg_list = msg.split(" ")
                if len(msg_list) >= 3:
                    playername = playername or msg_list[1]
                    msg = " ".join(msg_list[2:])
                else:
                    fmts.print_war(f"无法获取发言中的玩家名与消息: {playername}: {msg}")
                    return None, None
            return playername, msg
        case TextType.TextTypeAnnouncement:
            # /say 消息
            src_name = pkt["SourceName"]
            playername = sender_name or pkt["SourceName"]
            msg = msg.removeprefix(f"[{src_name}] ")
            return playername, msg
        case TextType.TextTypeObjectWhisper:
            # /tellraw 消息
            return None, None
        case _:
            return None, None
