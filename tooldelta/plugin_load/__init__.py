"插件加载主模块"

from typing import Any


def NON_FUNC(*_) -> None:
    "空函数"
    return None


class PluginSkip(EOFError):
    "跳过插件加载"


class NotValidPluginError(AssertionError):
    "仅加载插件时引发, 不是合法插件的报错"


class PluginAPINotFoundError(ModuleNotFoundError):
    "插件API未找到错误"

    def __init__(self, name):
        self.name = name


class PluginAPIVersionError(ModuleNotFoundError):
    "插件API版本错误"

    def __init__(self, name, m_ver, n_ver):
        self.name = name
        self.m_ver = m_ver
        self.n_ver = n_ver


class PluginRegData:
    "插件注册数据"

    def __init__(self, name: str, plugin_data: dict | None = None, is_registered=True, is_enabled=True):
        """插件注册数据

        Args:
            name (str): 插件名
            plugin_data (dict | None, optional): 插件数据
            is_registered (bool, optional): 是否已注册
            is_enabled (bool, optional): 是否启用
        """
        if plugin_data is None:
            plugin_data = {}
        self.name: str = name
        if isinstance(plugin_data.get("version"), str):
            self.version: tuple = tuple(
                int(i) for i in plugin_data.get("version", "0.0.0").split(".")
            )
        else:
            self.version = plugin_data.get("version", (0, 0, 0))
        #  以下的方法或许存在危险
        self.author: str = plugin_data.get("author", "unknown")
        self.plugin_type: str = plugin_data.get("plugin-type", "unknown")
        self.description: str = plugin_data.get("description", "")
        self.pre_plugins: dict[str, str] = plugin_data.get("pre-plugins", [])
        self.plugin_id = plugin_data.get("plugin-id", "???")
        self.is_registered = is_registered
        if plugin_data.get("enabled") is not None:
            self.is_enabled = plugin_data["enabled"]
        else:
            self.is_enabled = is_enabled

    def dump(self) -> dict[str, Any]:
        "转储数据"
        return {
            "author": self.author,
            "version": ".".join([str(i) for i in self.version]),
            "plugin-type": self.plugin_type,
            "description": self.description,
            "pre-plugins": self.pre_plugins,
            "plugin-id": self.plugin_id,
            "enabled": self.is_enabled
        }

    @property
    def version_str(self) -> str:
        """版本字符串

        Returns:
            str: 版本字符串
        """
        return ".".join(str(i) for i in self.version)

    @property
    def plugin_type_str(self) -> str:
        """插件类型字符串

        Returns:
            str: 插件类型字符串
        """
        return {
            "classic": "主类式",
            "injected": "注入式",
            "unknown": "未知类型",
        }.get(self.plugin_type, "未知类型")


def plugin_is_enabled(pname: str) -> bool:
    """插件是否启用

    Args:
        pname (str): 插件名

    Returns:
        bool: 是否启用
    """
    return not pname.endswith("+disabled")
