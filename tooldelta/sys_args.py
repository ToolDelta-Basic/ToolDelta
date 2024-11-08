"解析启动参数"

import sys

_cached_sys_args_dict: dict | None = None


def sys_args_to_dict(argv: list[str] = sys.argv) -> dict[str, str | None]:
    """将启动参数转换为字典

    Args:
        argv (list[str], optional): 启动参数

    Returns:
        dict[str, str | None]: 启动参数字典
    """
    # 为什么不用 argsparser? 因为这样可以支持混合型启动参数
    global _cached_sys_args_dict
    if _cached_sys_args_dict is None:
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
        _cached_sys_args_dict = d
        return d
    else:
        return _cached_sys_args_dict


def print_help():
    print("启动参数帮助：")
    print("    -h, -help  查看帮助 (当前页)")
    print("    -v, --version  获取当前程序版本")
    print("    -title <文本> 在开始界面显示指定的文本 (支持mc彩色符号)")
    print(
        '    -optadd "<选项名>: <执行的cmd>" 添加额外的启动选项, 使用分号分割多个选项'
    )
    print("    -no-update-check  禁用自动更新")
    print("    -no-download-libs  禁用自动更新依赖库")
    print("    -no-download-neomega 在NeOmega混合启动模式下, 禁用自动更新NeOmega启动器")
    print("    -l <启动模式>  按照特定的启动模式，跳过启动页面")
    print("    -user-token <token>  使用传入的而非本地的token来登录验证服务器")


def parse_addopt(opt_str: str):
    arg2cmds: dict[str, str] = {}
    for val in opt_str.split(";"):
        split_res = val.split(":")
        if len(split_res) < 2:
            print('无效的添加选项命令, 应为 -optadd "<选项名>: <执行的cmd>", 如:')
            print('  -optadd "§b管理您的账号: ./acc_mana"')
            print('  -optadd "§b管理您的账号: ./acc_mana; §6自动更新: ./update.sh"')
            raise SystemExit
        opt_str = split_res[0].removeprefix(" ")
        opt_cmd = ":".join(split_res[1:])
        arg2cmds[opt_str] = opt_cmd
    return arg2cmds
