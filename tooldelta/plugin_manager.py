import os, shutil

from .color_print import Print
from .builtins import Builtins

class PluginData:
    def __init__(self, name: str, plugin_data: dict):
        self.name: str = name
        self.version: tuple = tuple(int(i) for i in plugin_data["version"].split("."))
        self.author: str = plugin_data["author"]
        self.plugin_type: str = plugin_data["plugin-type"]
        self.description: str = plugin_data["description"]
        self.pre_plugins: dict[str, str] = plugin_data["pre-plugins"]
        self.enabled = plugin_data["enabled"]
        self.is_registered = plugin_data["registered"]

class PluginManager:
    def plugin_manage(self):
        ...

    def list_all_plugins(self):
        ...


plugin_manager = PluginManager()
plugin_manager.plugin_manage()