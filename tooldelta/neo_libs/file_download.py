import json
import os
import platform

import requests

from tooldelta import constants
from tooldelta.cfg import Config
from tooldelta.color_print import Print
from tooldelta.sys_args import sys_args_to_dict
from tooldelta.urlmethod import download_file_singlethreaded


def download_libs() -> bool:
    """根据系统架构和平台下载所需的库。"""
    if "no-download-libs" in sys_args_to_dict():
        Print.print_war("将不会进行依赖库的下载和检测更新。")
        return True
    cfgs = Config.get_cfg("ToolDelta基本配置.json", constants.LAUNCH_CFG_STD)
    is_mir: bool = cfgs["是否使用github镜像"]
    if is_mir:
        mirror_src = (
            constants.TDSPECIFIC_MIRROR
            + "/https://raw.githubusercontent.com/ToolDelta/ToolDelta/main/"
        )
        depen_url = (
            constants.TDSPECIFIC_MIRROR
            + "/https://raw.githubusercontent.com/ToolDelta/DependencyLibrary/main/"
        )
    else:
        mirror_src = "https://raw.githubusercontent.com/ToolDelta/ToolDelta/main/"
        depen_url = (
            "https://raw.githubusercontent.com/ToolDelta/DependencyLibrary/main/"
        )
    try:
        require_depen = json.loads(
            requests.get(f"{mirror_src}require_files.json", timeout=5).text
        )
    except Exception as err:
        Print.print_err(f"获取依赖库表出现问题：{err}")
        return False
    sys_machine = platform.machine().lower()
    if sys_machine == "x86_64":
        sys_machine = "amd64"
    elif sys_machine == "aarch64":
        sys_machine = "arm64"
    if "TERMUX_VERSION" in os.environ:
        sys_info_fmt: str = f"Android:{sys_machine.lower()}"
    else:
        sys_info_fmt: str = f"{platform.uname().system}:{sys_machine.lower()}"
    source_dict: list[str] = require_depen[sys_info_fmt]
    commit_remote = requests.get(f"{depen_url}commit", timeout=5).text
    commit_file_path = os.path.join(os.getcwd(), "tooldelta", "neo_libs", "commit")
    replace_file = False
    if os.path.isfile(commit_file_path):
        with open(commit_file_path, "r", encoding="utf-8") as f:
            commit_local = f.read()
        if commit_local != commit_remote:
            Print.print_war("依赖库版本过期，将重新下载")
            replace_file = True
    else:
        replace_file = True
    for v in source_dict:
        pathdir = os.path.join(os.getcwd(), "tooldelta", "neo_libs", v)
        url = depen_url + v
        if not os.path.isfile(pathdir) or replace_file:
            Print.print_with_info(f"正在下载依赖库 {pathdir} ...", "§a 下载 §r")
            try:
                download_file_singlethreaded(url, pathdir)
            except Exception as err:
                Print.print_err(f"下载依赖库出现问题：{err}")
                return False
    if replace_file:
        # 写入 commit_remote，文字写入
        with open(commit_file_path, "w", encoding="utf-8") as f:
            f.write(commit_remote)
        Print.print_suc("已完成 NeOmega框架 的依赖更新！")
    return True
