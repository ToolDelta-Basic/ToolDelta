def get_tool_delta_version() -> tuple[int, ...]:
    try:
        return tuple(
            int(v)
            for v in open("version", "r", encoding="utf-8").read().strip()[1:].split(".")
        )
    except:
        # 该返回值不必手动修改，
        # 它会由 GitHub Action 自动从 version 文件同步
        return (0, 3, 13)
