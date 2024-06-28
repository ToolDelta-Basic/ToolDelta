"解析启动参数"

import sys


def sys_args_to_dict(argv: list[str] = sys.argv) -> dict[str, str | None]:
    """将启动参数转换为字典

    Args:
        argv (list[str], optional): 启动参数

    Returns:
        dict[str, str | None]: 启动参数字典
    """
    # 为什么不用 argsparser? 因为这样可以支持混合型启动参数
    d: dict[str, str | None] = {}
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


def print_help():
    print("启动参数帮助：")
    print("    -help  查看帮助 (当前页)")
    print("    -no-update-check  禁用自动更新")
    print("    -no-download-libs  禁用自动更新依赖库")
    print("    -l <启动模式>  按照特定的启动模式，跳过启动页面")
