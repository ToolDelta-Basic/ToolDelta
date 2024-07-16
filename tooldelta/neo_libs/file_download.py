import asyncio
import json
import os
import platform

import requests

from tooldelta import constants
from tooldelta import urlmethod
from tooldelta.cfg import Config
from tooldelta.color_print import Print
from tooldelta.sys_args import sys_args_to_dict


def download_libs() -> bool:
    """根据系统架构和平台下载所需的库。"""
    if "no-download-libs" in sys_args_to_dict():
        Print.print_war("将不会进行依赖库的下载和检测更新。")
        return True
    cfgs = Config.get_cfg("ToolDelta基本配置.json", constants.LAUNCH_CFG_STD)
    is_mir: bool = cfgs["是否使用github镜像"]
    mirror_src, depen_url = get_mirror_urls(is_mir)
    require_depen = get_required_dependencies(mirror_src)
    sys_info_fmt = get_system_info()
    source_dict = require_depen[sys_info_fmt]
    commit_remote = get_remote_commit(depen_url)
    commit_file_path = os.path.join(os.getcwd(), "tooldelta", "neo_libs", "commit")
    replace_file = check_commit_file(commit_file_path, commit_remote)
    solve_dict = get_solve_dict(source_dict, depen_url, replace_file)
    asyncio.run(urlmethod.download_file_urls(solve_dict))
    if replace_file:
        write_commit_file(commit_file_path, commit_remote)
        Print.print_suc("已完成 NeOmega框架 的依赖更新！")
    return True

def get_mirror_urls(is_mir: bool) -> tuple[str, str]:
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
    return mirror_src, depen_url

def get_required_dependencies(mirror_src: str) -> dict:
    try:
        require_depen = json.loads(
            requests.get(f"{mirror_src}require_files.json", timeout=5).text
        )
    except Exception as err:
        Print.print_err(f"获取依赖库表出现问题：{err}")
        return {}
    return require_depen

def get_system_info() -> str:
    sys_machine = platform.machine().lower()
    if sys_machine == "x86_64":
        sys_machine = "amd64"
    elif sys_machine == "aarch64":
        sys_machine = "arm64"
    if "TERMUX_VERSION" in os.environ:
        sys_info_fmt = f"Android:{sys_machine.lower()}"
    else:
        sys_info_fmt = f"{platform.uname().system}:{sys_machine.lower()}"
    return sys_info_fmt

def get_remote_commit(depen_url: str) -> str:
    return requests.get(f"{depen_url}commit", timeout=5).text

def check_commit_file(commit_file_path: str, commit_remote: str) -> bool:
    replace_file = False
    if os.path.isfile(commit_file_path):
        with open(commit_file_path, encoding="utf-8") as f:
            commit_local = f.read()
        if commit_local != commit_remote:
            Print.print_war("依赖库版本过期，将重新下载")
            replace_file = True
    else:
        replace_file = True
    return replace_file

def get_solve_dict(source_dict: list[str], depen_url: str, replace_file: bool) -> list[tuple[str, str]]:
    solve_dict = []
    for v in source_dict:
        pathdir = os.path.join(os.getcwd(), "tooldelta", "neo_libs", v)
        if not os.path.isfile(pathdir) or replace_file:
            solve_dict.append((depen_url + v, pathdir))
    return solve_dict

def write_commit_file(commit_file_path: str, commit_remote: str):
    with open(commit_file_path, "w", encoding="utf-8") as f:
        f.write(commit_remote)
