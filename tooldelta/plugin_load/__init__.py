# NOTE 快捷导入插件函数(待增加)
from .injected_plugin.movent import (
    sendcmd,
    sendfbcmd,
    sendPacket,
    sendPacketJson,
    sendwocmd,
    sendwscmd,
    tellrawText,
    get_all_player,
    getTarget,
    rawText,
    is_op,
    getPos,
    get_robotname,
    countdown,
    getBlockTile,
    getTickingAreaList
)

from .injected_plugin import (
    player_message,
    player_join,
    player_left,
    repeat,
    init,
    player_death,
)
import os, sys, zipfile
from ..cfg import Cfg
from ..builtins import Builtins
NON_FUNC = lambda *_: None
from .PluginGroup import Plugin, PluginAPI, PluginGroup

class PluginSkip(EOFError): ...
