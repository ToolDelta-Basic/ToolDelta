"获取 ToolDelta 的版本号"


def get_tool_delta_version() -> tuple[int, ...]:
    """获取 ToolDelta 的版本号

    Returns:
        tuple[int, ...]: 版本号
    """
    try:
        with open("version", "r", encoding="utf-8") as file:
            return tuple(int(v) for v in file.read().strip().split("."))
    except Exception:
        # 该返回值不必手动修改，
        # 它会由 GitHub Action 自动从 version 文件同步
        return (0, 7, 13)
