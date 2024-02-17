from ..cfg import Cfg
from ..builtins import Builtins
NON_FUNC = lambda *_: None
from .PluginGroup import Plugin, PluginAPI, PluginGroup

class PluginSkip(EOFError): ...
