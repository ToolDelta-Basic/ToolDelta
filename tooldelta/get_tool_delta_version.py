def get_tool_delta_version() -> tuple[int, ...]:
    try:
        with open("version", "r", encoding="utf-8") as file:
            return tuple(int(v) for v in file.read().strip().split("."))
    except:
        # 该返回值不必手动修改，
        # 它会由 GitHub Action 自动从 version 文件同步
        return (0, 4, 5)
