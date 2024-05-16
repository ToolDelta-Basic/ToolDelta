"""自定义常用URL方法"""
import os
import re
import shutil
import socket
import time
from typing import Union
from concurrent.futures import ThreadPoolExecutor, as_completed
import pyspeedtest
import requests

from .get_tool_delta_version import get_tool_delta_version
from .color_print import Print

# 使用方法 mirror_github[value: int].format(url: str)
mirror_github = ["https://hub.gitmirror.com/{}", "https://gh.con.sh/{}", "https://mirror.ghproxy.com/{}"]

def format_mirror_url(url: str) -> list:
    """填充url到镜像url列表

    Args:
        url (str): 原始URL

    Returns:
        list: 填充原始url后的镜像列表
    """
    mir_url: list = []
    for mirror in mirror_github:mir_url.append(mirror.format(url))
    return mir_url

def githubdownloadurl_to_rawurl(url: str) -> str:
    """将github下载链接转换为原始链接

    Args:
        url (str): 原始链接

    Returns:
        str: 原始链接
    """
    try:
        if url.startswith("https://github.com/"):return requests.head(url, allow_redirects=True).url
        else:return url
    except:return url

def progress_bar(
    current: float | int, total: float | int, length: int | float = 20, color1: str = "§f", color2: str = "§b"
) -> str:
    """执行进度条

    Args:
        current (float | int): 当前进度值
        total (float | int): 总进度值
        length (int): 进度条长度.
        color1 (str): 进度条颜色1.
        color2 (str): 进度条颜色2.

    Returns:
        str: 格式化后的进度条字符串
    """
    pc = round(current / total * length)
    return Print.colormode_replace(
        color1 + " " * pc + color2 + " " * (20 - pc) + "§r ", 7
    )


def download_progress_bar(
    current_bytes: int, total_bytes: int, speed: float = 0
) -> None:
    """构建下载进度条

    Args:
        current_bytes (int): 当前已下载的字节数
        total_bytes (int): 文件总字节数
        speed ( float): 下载速度.
    """
    progressBar = progress_bar(current_bytes, total_bytes)
    b = f"{progressBar} {pretty_kb(current_bytes)}B / {pretty_kb(total_bytes)}B"
    if speed != 0:
        b += f" ({pretty_kb(speed)}B/s)    "
    with Print.lock:Print.print_with_info(b, "§a 下载 ", need_log=False, end="\r")


def pretty_kb(n: float) -> str:
    """将字节数转换为可读性更好的字符串表示形式

    Args:
        n (float): 字节数

    Returns:
        str: 可读性更好的字符串表示形式
    """
    if n >= 1048576:
        return f"{round(n / 1048576, 2)}M"
    if n >= 1024:
        return f"{round(n / 1024, 2)}K"
    return f"{round(n, 1)}"


def is_common_text_file(url_path: str) -> bool:
    """判断是否为常见的文本文件.

    Args:
        url_path (str): 文件路径

    Returns:
        bool: 是否为常见的文本文件
    """
    return any(
        url_path.endswith(i)
        for i in [".txt", ".yml", ".md", ".xml", ".py", ".h", ".c", ".pyi", ".json"]
    )


def get_file_size(url: str) -> Union[int, None]:
    """获取文件大小

    Args:
        url (str): 网址

    Returns:
        Union[int, None]: 文件大小（单位：字节）
    """
    response = requests.head(url, timeout=10)
    if "Content-Length" in response.headers:
        file_size = int(response.headers["Content-Length"])
        return file_size


def download_file_chunk(url: str, start_byte: int, end_byte: int, save_dir: str) -> int:
    """下载文件的代码块

    Args:
        url (str): 文件的URL地址
        start_byte (int): 下载的起始字节位置
        end_byte (int): 下载的结束字节位置
        save_dir (str): 文件保存的目录

    Returns:
        int: 已下载的字节数
    """
    headers = {"Range": f"bytes={start_byte}-{end_byte}"}
    response = requests.get(url, headers=headers, stream=True, timeout=10)
    response.raise_for_status()
    with open(save_dir + ".tmp", "rb+") as dwnf:
        dwnf.seek(start_byte)
        downloaded_bytes = 0
        for chunk in response.iter_content(chunk_size=8192):
            dwnf.write(chunk)
            downloaded_bytes += len(chunk)
        return downloaded_bytes


def download_file_singlethreaded(
    url: str, save_dir: str, ignore_warnings: bool = False
) -> None:
    """下载单个文件

    Args:
        url (str): 文件的URL地址
        save_dir (str): 文件保存的目录
        ignore_warnings (bool, optional): 是否忽略警告
    """
    with requests.get(url, stream=True, timeout=10) as res:
        res.raise_for_status()
        filesize = get_file_size(url)
        if filesize is not None and filesize < 256 and not ignore_warnings:
            Print.print_war(f"下载 {url} 的文件警告: 文件大小异常，不到 0.25KB")
        chunk_size = 8192
        useSpeed: float = 0
        # nowsize: 当前已下载的字节数
        nowsize: int = 0
        lastime: float = 1
        with open(save_dir + ".tmp", "wb") as dwnf:
            for chk in res.iter_content(chunk_size):
                nowtime = time.time()
                if nowtime != lastime:
                    useSpeed = chunk_size / (nowtime - lastime)
                    lastime = nowtime
                nowsize += len(chk)
                dwnf.write(chk)
                if nowsize % 81920 == 0 and filesize:  # 每下载 10 个数据块更新一次进度
                    download_progress_bar(nowsize, filesize, useSpeed)
        shutil.move(save_dir + ".tmp", save_dir)


def download_unknown_file(url: str, save_dir: str) -> None:
    """下载未知文件

    Args:
        url (str): 文件的URL地址
        save_dir (str): 文件保存的目录
    """
    # 鉴于 Content-Length 不一定表示文件原始大小, 二进制文件与文本文件需要分开下载
    # 否则显示的下载条会异常
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    if is_common_text_file(save_dir):
        # 文本文件, 体积可能不大
        with open(save_dir, "wb") as f:
            f.write(resp.content)
    download_file_singlethreaded(url, save_dir)


def test_site_latency(Da: dict) -> list:
    """测试网站延迟

    Args:
        Da (dict): 包含URL和镜像URL的字典

    Returns:
        list: 按延迟排序的URL和延迟时间的元组列表
    """
    tmp_speed = {}
    urls = [Da["url"]] + Da["mirror_url"]

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(measure_latencyt, url) for url in urls]

        for future, url in zip(as_completed(futures), urls):
            try:
                latency = future.result(timeout=5)
                if latency != -1:
                    tmp_speed[url] = latency
            except Exception as e:
                Print.print_war(f"Error measuring latency for {url}: {e}")

    return sorted(tmp_speed.items(), key=lambda x: x[1], reverse=True)


def measure_latencyt(url: str) -> float:
    """测量延迟

    Args:
        url (str): 网址

    Raises:
        ValueError: 无效的网址

    Returns:
        float: 延迟时间
    """
    try:
        # 提取域名
        domain = re.search(
            r"(?<=http[s]://)[.\w-]*(:\d{1,8})?((?=/)|(?!/))", url)
        if isinstance(domain, type(None)):  # 如果没有匹配到域名
            raise ValueError("Invalid URL")
        st = pyspeedtest.SpeedTest(domain.group())  # 传入域名
        download_speed = st.download()
        return download_speed
    except Exception as e:
        Print.print_war(f"Error measuring latency for {url}: {e}")
    return -1.0  # 返回-1表示测速失败


def get_free_port(start: int = 2000, end: int = 65535) -> int:
    """获取空闲端口号

    Args:
        start (int, optional): 起始端口号.
        end (int, optional): 结束端口号.

    Raises:
        Exception: 未找到空闲端口

    Returns:
        int: 空闲端口号
    """
    for port in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("localhost", port))
                return port
            except OSError:
                Print.print_war(f"端口 {port} 正被占用, 跳过")
    raise ValueError(f"未找到空闲端口({start}~{end})")


def check_update() -> None:
    """检查更新"""
    try:
        latest_version: str = requests.get(
            "https://api.github.com/repos/ToolDelta/ToolDelta/releases/latest", timeout=5).json()["tag_name"]
        current_version = ".".join(
            map(str, get_tool_delta_version()[:3]))

        if not latest_version.replace(".", "") <= current_version.replace(".", ""):
            # Print.print_suc(f"当前为最新版本 -> v{current_version}，无需更新")
            Print.print_load(
                f"检测到最新版本 {current_version} -> {latest_version}，请及时更新!"
            )
    except KeyError:
        Print.print_war("获取最新版本失败，请检查网络连接")

def if_token() -> None:
    """检查路径下是否有fbtoken，没有就提示输入

    Raises:
        SystemExit: 未输入fbtoken
    """
    if not os.path.isfile("fbtoken"):
        Print.print_inf(
            "请到对应的验证服务器官网下载FBToken，并放在本目录中，或者在下面输入fbtoken"
        )
        fbtoken = input(Print.fmt_info("请输入fbtoken: ", "§b 输入 "))
        if fbtoken:
            with open("fbtoken", "w", encoding="utf-8") as f:
                f.write(fbtoken)
        else:
            Print.print_err("未输入fbtoken, 无法继续")
            raise SystemExit


def fbtokenFix():
    """修复fbtoken里的换行符    """
    with open("fbtoken", "r", encoding="utf-8") as f:
        token = f.read()
        if "\n" in token:
            Print.print_war("fbtoken里有换行符，会造成fb登陆失败，已自动修复")
            with open("fbtoken", "w", encoding="utf-8") as f:
                f.write(token.replace("\n", ""))
