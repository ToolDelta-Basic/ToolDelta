"获取 ToolDelta 的版本号"

VERSION = tuple[int, int, int]


class SystemVersionException(SystemError):
    """系统版本异常"""


def get_tool_delta_version() -> VERSION:
    """获取 ToolDelta 的版本号

    Returns:
        VERSION: 版本号
    """
    # 由 Github 自动同步
    return (1, 2, 0)


def check_tooldelta_version(need_vers: VERSION):
    """检查 ToolDelta 系统的版本

    Args:
        need_vers (VERSION): 需要的版本

    Raises:
        self.linked_frame.SystemVersionException: 该组件需要的 ToolDelta 系统版本
    """
    if need_vers >= get_tool_delta_version():
        raise SystemVersionException(
            f"ToolDelta 版本不匹配, 需要最低 {version_str(need_vers)} 版本, 当前 {version_str(get_tool_delta_version())}"
        )


def version_str(ver: VERSION):
    return ".".join(map(str, ver))
