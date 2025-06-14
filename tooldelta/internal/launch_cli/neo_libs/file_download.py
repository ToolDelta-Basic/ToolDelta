import asyncio
import hashlib
import os
import platform
import brotli
import requests

from ....constants.tooldelta_cli import TDDEPENDENCY_REPO_RAW
from ....utils import fmts, urlmethod, sys_args


def download_libs() -> bool:
    """根据系统架构和平台下载所需的库。"""
    if "no-download-libs" in sys_args.sys_args_to_dict():
        fmts.print_war("将不会进行依赖库的下载和检测更新。")
        return True
    mirror_src, depen_url = get_github_content_url(
        urlmethod.get_global_github_src_url() + "/https://raw.githubusercontent.com"
    )
    require_depen = get_required_dependencies(mirror_src)[0]
    sys_info_fmt = get_system_info()
    source_dict = require_depen.get(sys_info_fmt)
    if source_dict is None:
        raise ValueError(
            f"未知的系统架构版本: {sys_info_fmt} (目前支持: {', '.join(require_depen.keys())})"
        )
    commit_remote = get_remote_commit(depen_url)
    commit_file_path = os.path.join(os.getcwd(), "tooldelta", "bin", "neomega_commit")
    replace_file = check_commit_file(commit_file_path, commit_remote)
    solve_dict = get_required_dependencies_solve_dict(
        source_dict, depen_url, replace_file
    )
    asyncio.run(urlmethod.download_file_urls(solve_dict))
    if replace_file:
        write_commit_file(commit_file_path, commit_remote)
        fmts.print_suc("已完成 NeOmega框架 的依赖更新！")
    return True


def download_neomg() -> bool:
    """根据系统架构和平台下载所需的NeOmega。"""
    if "no-download-neomega" in sys_args.sys_args_to_dict():
        fmts.print_war("将不会进行NeOmega的下载和检测更新。")
        return True
    download_libs()
    mirror_src, _ = get_github_content_url(
        urlmethod.get_global_github_src_url() + "/https://raw.githubusercontent.com"
    )
    require_depen = get_required_dependencies(mirror_src)[1]
    sys_info_fmt = get_system_info()
    source_dict = require_depen[sys_info_fmt][0]
    neomega_file_hash: str = get_file_hash(source_dict["hash_url"])
    if platform.system().lower() == "windows":
        neomega_file_path = os.path.join(
            os.getcwd(),
            "tooldelta",
            "bin",
            f"omega_launcher_{sys_info_fmt.split(':')[0].lower()}_{sys_info_fmt.split(':')[1].lower()}.exe",
        )
    else:
        neomega_file_path = os.path.join(
            os.getcwd(),
            "tooldelta",
            "bin",
            f"omega_launcher_{sys_info_fmt.split(':')[0].lower()}_{sys_info_fmt.split(':')[1].lower()}",
        )
    replace_file = check_file_hash(neomega_file_hash, neomega_file_path)
    if replace_file:
        asyncio.run(
            urlmethod.download_file_urls(
                [
                    (
                        source_dict["url"],
                        os.path.join(
                            os.getcwd(),
                            "tooldelta",
                            "bin",
                            "omega_launcher.brotli",
                        ),
                    )
                ]
            )
        )
        unzip_brotli_file(
            os.path.join(os.getcwd(), "tooldelta", "bin", "omega_launcher.brotli"),
            neomega_file_path,
        )
        fmts.print_suc("已完成 NeOmega框架 的依赖更新！")
    return True


def get_github_content_url(url: str) -> tuple[str, str]:
    mirror_src = url + "/ToolDelta-Basic/ToolDelta/main"
    depen_url = url + f"/{TDDEPENDENCY_REPO_RAW}/main"
    return mirror_src, depen_url


def get_required_dependencies(mirror_src: str) -> tuple[dict, dict]:
    try:
        resp1 = requests.get(f"{mirror_src}/require_files.json", timeout=5)
        resp1.raise_for_status()
        require_depen = resp1.json()["NeOmega"]
        resp2 = requests.get(f"{mirror_src}/neomega_files.json", timeout=5)
        resp2.raise_for_status()
        require_neomega = resp2.json()
    except Exception as err:
        fmts.print_err(f"获取依赖库表出现问题：{err} (镜像: {mirror_src})")
        raise
    return require_depen, require_neomega


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
    return requests.get(f"{depen_url}/commit", timeout=5).text


def check_commit_file(commit_file_path: str, commit_remote: str) -> bool:
    replace_file = False
    if os.path.isfile(commit_file_path):
        with open(commit_file_path, encoding="utf-8") as f:
            commit_local = f.read()
        if commit_local != commit_remote:
            fmts.print_war("依赖库版本过期，将重新下载")
            replace_file = True
    else:
        replace_file = True
    return replace_file


def get_required_dependencies_solve_dict(
    source_dict: list[str], depen_url: str, replace_file: bool
) -> list[tuple[str, str]]:
    solve_dict = []
    for v in source_dict:
        pathdir = os.path.join(os.getcwd(), "tooldelta", "bin", v)
        if not os.path.isfile(pathdir) or replace_file:
            solve_dict.append((depen_url + "/" + v, pathdir))
    return solve_dict


def write_commit_file(commit_file_path: str, commit_remote: str):
    with open(commit_file_path, "w", encoding="utf-8") as f:
        f.write(commit_remote)


def get_file_hash(hash_url: str) -> str:
    return requests.get(f"{hash_url}", timeout=5).text.replace("\n", "")


def calculate_file_hash(file_path: str, algorithm: str = "md5") -> str:
    hash_obj = hashlib.new(algorithm)
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()


def check_file_hash(file_hash: str, file_path: str) -> bool:
    replace_file = False
    if os.path.isfile(file_path):
        hash = calculate_file_hash(file_path)
        if file_hash != hash:
            fmts.print_war("NeOmega 版本过期，将重新下载")
            replace_file = True
    else:
        replace_file = True
    return replace_file


def unzip_brotli_file(file_path: str, save_path: str) -> bool:
    try:
        with open(file_path, "rb") as source_file, open(save_path, "wb") as target_file:
            compressed_data = source_file.read()
            decompressed_data = brotli.decompress(compressed_data)
            target_file.write(decompressed_data)
        os.remove(file_path)
        return True
    except Exception:
        return False
