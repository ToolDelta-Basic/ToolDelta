from tooldelta import GameCtrl, Frame
frame = Frame()
game_control = GameCtrl(frame)
game_control.init_funcs()
game_control.set_listen_packets()

def sendcmd(*arg):
    game_control.sendcmd(*arg)


def sendwscmd(*arg):
    game_control.sendwscmd(*arg)


def sendwocmd(*arg):
    game_control.sendwocmd(*arg)


def sendPacket(*arg):
    game_control.sendPacket(*arg)


def sendPacketJson(*arg):
    game_control.sendPacketJson(*arg)


def sendfbcmd(*arg):
    game_control.sendfbcmd(*arg)


def tellrawText(playername: str, title: str | None = None, text: str = ""):
    """
    发送tellraw消息
    ---
    playername:str 玩家名.
    title:str 说话人.
    text:str 内容.
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
