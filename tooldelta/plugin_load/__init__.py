from .PluginGroup import Plugin, PluginAPI, PluginGroup
from ..cfg import Cfg
from ..builtins import Builtins
NON_FUNC = lambda *_: None


class PluginSkip(EOFError):
    ...
