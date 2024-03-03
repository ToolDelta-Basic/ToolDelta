import sys

def sys_args_to_dict(argv: list[str] = sys.argv):
    # 将启动参数分割为 -键=值 或 -键=None
    # 为什么不用 argsparser? 因为这样可以支持混合型启动参数
    d: dict[str, str] = {}
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg.startswith("-"):
            arg = arg.strip("--").strip("-")
            try:
                val = argv[i + 1]
                if val.startswith("-"):
                    val = None
                else:
                    i += 1
            except IndexError:
                val = None
            d[arg] = val
        i += 1
    return d
