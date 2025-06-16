class PluginSkip(EOFError):
    """跳过插件加载"""


class NotValidPluginError(AssertionError):
    """仅加载插件时引发，不是合法插件的报错"""


class PluginAPINotFoundError(ModuleNotFoundError):
    """插件 API 未找到错误"""
    api_name: str

    def __init__(self, api_name: str):
        self.api_name = api_name


class PluginAPIVersionError(ModuleNotFoundError):
    """插件 API 版本错误"""

    def __init__(self, name, m_ver, n_ver):
        self.name = name
        self.m_ver = m_ver
        self.n_ver = n_ver
