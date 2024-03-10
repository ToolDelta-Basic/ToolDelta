NON_FUNC = lambda *_: None


class PluginSkip(EOFError):
    ...

class PluginRegData:
    def __init__(self, name: str, plugin_data: dict = None, is_registered=True, is_enabled=True):
        if plugin_data is None:
            plugin_data = {}
        self.name: str = name
        if isinstance(plugin_data.get("version"), str):
            self.version: tuple = tuple(
                int(i) for i in plugin_data.get("version", "0.0.0").split(".")
            )
        else:
            self.version = plugin_data.get("version", (0, 0, 0))
        self.author: str = plugin_data.get("author", "unknown")
        self.plugin_type: str = plugin_data.get("plugin-type", "unknown")
        self.description: str = plugin_data.get("description", "")
        self.pre_plugins: dict[str, str] = plugin_data.get("pre-plugins", [])
        self.is_registered = is_registered
        if plugin_data.get("enabled") is not None:
            self.is_enabled = plugin_data.get("enabled")
        else:
            self.is_enabled = is_enabled

    def dump(self):
        return {
            "author": self.author,
            "version": ".".join([str(i) for i in self.version]),
            "plugin-type": self.plugin_type,
            "description": self.description,
            "pre-plugins": self.pre_plugins,
            "enabled": self.is_enabled
        }

    @property
    def version_str(self):
        return ".".join(str(i) for i in self.version)

    @property
    def plugin_type_str(self):
        return {
            "classic": "组合式",
            "injected": "注入式",
            "dotcs": "DotCS",
            "unknown": "未知类型",
        }.get(self.plugin_type, "未知类型")

def plugin_is_enabled(pname: str):
    return not pname.endswith("+disabled")