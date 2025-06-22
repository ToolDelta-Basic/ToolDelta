import asyncio
import os
import platform
import requests

from ....constants.tooldelta_cli import TDDEPENDENCY_REPO
from ....utils import fmts
from ....utils.urlmethod import download_file_urls, get_newest_dependency_commit


def get_bin_path():
    sys_machine = platform.machine().lower()
    sys_type = platform.uname().system

    # Mapping architecture names to common naming
    arch_map = {"x86_64": "amd64", "aarch64": "arm64"}
    sys_machine = arch_map.get(sys_machine, sys_machine)

    # Mapping system types to library file names
    if sys_type == "Windows":
        exe_fn = f"FateArk_windows_{sys_machine}.exe"
    elif "TERMUX_VERSION" in os.environ:
        exe_fn = "FateArk_android_arm64"
    elif sys_type == "Linux":
        exe_fn = f"FateArk_linux_{sys_machine}"
    else:
        fmts.print_err(f"暂不支持的操作系统: {sys_machine}")
        raise SystemExit
    return os.path.join(os.getcwd(), "tooldelta", "bin", exe_fn)


def get_fateark_dependency_libs(mirror_src: str) -> list[str]:
    sys_machine = platform.machine().lower()
    sys_type = platform.uname().system

    # Mapping architecture names to common naming
    arch_map = {"x86_64": "amd64", "aarch64": "arm64"}
    sys_machine = arch_map.get(sys_machine, sys_machine)
    try:
        url = f"{mirror_src}/https://raw.githubusercontent.com/ToolDelta-Basic/ToolDelta/main/require_files.json"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        require_depends: dict[str, list[str]] = resp.json()["FateArk"]
    except (Exception, KeyError) as err:
        fmts.print_err(f"获取依赖库表出现问题：{err} (镜像: {url})")
        raise
    if (files := require_depends.get(f"{sys_type}:{sys_machine}")) is None:
        fmts.print_err(f"暂不支持的架构: {sys_type}:{sys_machine}")
        raise SystemExit
    return files


def download_fateark_dependency_libs(
    dependency_mirror_src: str, require_depends: list[str]
):
    url2dst = {
        dependency_mirror_src + "/" + file: os.path.join("tooldelta", "bin", file)
        for file in require_depends
    }
    asyncio.run(download_file_urls(list(url2dst.items())))


def check_update(mirror_src: str):
    fmts.print_inf("正在检测 FateArk 更新..")
    if not os.path.isfile("tooldelta/bin/fateark_commit"):
        commit = ""
    else:
        with open("tooldelta/bin/fateark_commit", encoding="utf-8") as f:
            commit = f.read()
    newest_commit = get_newest_dependency_commit(mirror_src)
    if newest_commit != commit:
        fmts.print_inf("正在下载最新的 FateArk 接入点依赖项..")
        dependency_mir_url = mirror_src + "/" + TDDEPENDENCY_REPO + "/main"
        download_fateark_dependency_libs(
            dependency_mir_url, get_fateark_dependency_libs(mirror_src)
        )
        with open("tooldelta/bin/fateark_commit", "w", encoding="utf-8") as f:
            f.write(newest_commit)
    fmts.print_inf("检测 FateArk 更新完成")
