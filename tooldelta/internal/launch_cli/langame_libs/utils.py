import os
import platform

from ....constants.tooldelta_cli import TOOLDELTA_BIN_PATH
from ....utils import fmts


def get_bin_path():
    sys_machine = platform.machine().lower()
    sys_type = platform.uname().system

    # Mapping architecture names to common naming
    arch_map = {"x86_64": "amd64", "aarch64": "arm64"}
    sys_machine = arch_map.get(sys_machine, sys_machine)

    # Mapping system types to library file names
    if sys_type == "Windows":
        exe_fn = f"NEMCLanGame_windows_{sys_machine}.exe"
    elif "TERMUX_VERSION" in os.environ:
        exe_fn = "NEMCLanGame_linux_arm64"
    elif sys_type == "Linux":
        exe_fn = f"NEMCLanGame_linux_{sys_machine}"
    else:
        fmts.print_err(f"暂不支持的操作系统: {sys_machine}")
        raise SystemExit
    return TOOLDELTA_BIN_PATH / exe_fn
