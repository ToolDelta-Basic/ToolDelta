"""自定义常用 URL 方法"""

import asyncio
import os
import re
import shutil
import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import aiohttp
import anyio
import pyspeedtest
import requests
from colorama import Fore, Style, init
from tqdm.asyncio import tqdm

from ..constants.tooldelta_cli import TDREPO_URL, TDDEPENDENCY_REPO_RAW
from ..version import get_tool_delta_version
from . import fmts

GGithubSrcURL = ""
GPluginMarketURL = ""

# Initialize colorama
init(autoreset=True)

# def get_avali_github_url(self):
#     """自动选择最佳镜像地址"""
#     url_list = ["https://ghp.ci", "https://github.tooldelta.top"]
#     try:
#         if not Config.get_cfg(
#                 "ToolDelta基本配置.json", {"是否使用github镜像": bool}
#             )["是否使用github镜像"]:
#             self.url = "https://raw.githubusercontent.com"
#             return self.url
#         if url := Config.get_cfg(
#                 "ToolDelta基本配置.json", {"插件市场源": str}
#             )["插件市场源"]:
#             self.url = f"{url}/https://raw.githubusercontent.com"
#             return self.url
#     except Exception:
#         fmts.clean_print("§c未发现配置文件，将选择内置镜像地址")
#     for url in url_list:
#         try:
#             response = requests.get(url)
#             if response.status_code == 200:
#                 self.url = f"{url}/https://raw.githubusercontent.com"
#                 return self.url
#         except requests.RequestException:
#             continue
#     self.url = "https://github.tooldelta.top/https://raw.githubusercontent.com"
#     return self.url


def set_global_github_src_url(url: str):
    global GGithubSrcURL
    GGithubSrcURL = url


def get_global_github_src_url():
    return GGithubSrcURL or "https://mirror.ghproxy.com"


def get_fastest_github_mirror():
    # fmts.print_inf("正在对各 GitHub 镜像进行测速 (这需要 5s) ...")
    # res = test_site_latency([
    #     "https://gh-proxy.com/",
    #     "https://github.tooldelta.top",
    # ])
    # fmts.print_suc(f"检测完成: 将使用 {(site := res[0][0])}")
    # return site
    return "https://github.tooldelta.top"


async def download_file_urls(download_url2dst: list[tuple[str, str]]) -> None:
    """
    从给定的URL并发下载文件到指定的目标路径。

    Args:
        download_url2dst (List[Tuple[str, str]]): 包含多个元组的列表，每个元组包含：
            - url (str): 要下载的文件的URL。
            - dst (str): 下载的文件将保存的目标路径。

    Returns:
        None
    """
    Http_Ok = 200

    async def download_file(
        session: aiohttp.ClientSession,
        url: str,
        i: int,
        file_path: str,
    ) -> tqdm:
        """
        从给定的URL下载单个文件到指定的目标路径。

        Args:
            session (aiohttp.ClientSession): 用于发送HTTP请求的aiohttp客户端会话。
            url (str): 要下载的文件的URL。
            i (int): 下载任务的索引，用于进度条定位。
            sem (asyncio.Semaphore): 用于限制同时进行的下载任务数量的信号量。
            sem2 (asyncio.Semaphore): 用于限制显示的进度条数量的信号量。
            file_path (str): 下载的文件将保存的目标路径。

        Returns:
            tqdm: 下载任务的进度条。
        """
        async with sem2:
            progress_bar = tqdm(
                desc=f"• Downloading {Fore.CYAN}{url.split('/')[-1]}{Style.RESET_ALL}: {Fore.YELLOW}Pending...{Style.RESET_ALL}",
                total=0,
                unit="MB",
                unit_scale=True,
                bar_format="{desc} {n:.2f}MB/{total:.2f}MB",
                position=i,
            )
            async with sem:
                async with session.get(url) as response:
                    if response.status == Http_Ok:
                        filename = url.split("/")[-1]
                        total_size = int(response.headers.get("content-length", 0))
                        total_size_mb = total_size / (1024 * 1024)  # 转换为 MB
                        progress_bar.reset(total=total_size_mb)

                        progress_bar.set_description_str(
                            f"• Downloading {Fore.CYAN}{filename}{Style.RESET_ALL}: {Fore.YELLOW}In Progress...{Style.RESET_ALL}"
                        )
                        downloaded = 0

                        async with await anyio.open_file(file_path, "wb") as f:
                            async for chunk in response.content.iter_chunked(1024):
                                await f.write(chunk)
                                downloaded += len(chunk)
                                progress_bar.update(
                                    len(chunk) / (1024 * 1024)
                                )  # 更新进度为 MB

                        progress_bar.set_description_str(
                            f"• Downloading {Fore.CYAN}{filename}{Style.RESET_ALL}: {Fore.GREEN}Succeed{Style.RESET_ALL}"
                        )
                        progress_bar.bar_format = "{desc}"  # 只显示描述
                        progress_bar.refresh()
                    else:
                        progress_bar.set_description_str(
                            f"• Downloading {Fore.CYAN}{url.split('/')[-1]}{Style.RESET_ALL}: {Fore.RED}Failed (HTTP {response.status}){Style.RESET_ALL}"
                        )
                        progress_bar.bar_format = "{desc}"  # 只显示描述
                        progress_bar.refresh()
            return progress_bar

    sem = asyncio.Semaphore(6)  # 限制同时进行的下载任务数量为4
    sem2 = asyncio.Semaphore(10)  # 只显示 10 个下载任务

    async with aiohttp.ClientSession() as session:
        tasks: list[asyncio.Task] = []
        progress_bars: list[tqdm] = []

        for i, (url, dst) in enumerate(download_url2dst):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            task: asyncio.Task = asyncio.create_task(
                download_file(session, url, i, dst)
            )
            tasks.append(task)

        progress_bars = await asyncio.gather(*tasks)
        for progress_bar in progress_bars:
            progress_bar.close()


def githubdownloadurl_to_rawurl(url: str) -> str:
    """将 GitHub 下载链接转换为原始链接

    Args:
        url (str): 原始链接

    Returns:
        str: 原始链接
    """
    try:
        if url.startswith("https://github.com/"):
            return requests.head(url, allow_redirects=True).url
        return url
    except Exception:
        return url


def progress_bar(
    current: float,
    total: float,
    length: float = 20,
    color1: str = "§f",
    color2: str = "§b",
) -> str:
    """执行进度条

    Args:
        current (float | int): 当前进度值
        total (float | int): 总进度值
        length (int): 进度条长度.
        color1 (str): 进度条颜色 1.
        color2 (str): 进度条颜色 2.

    Returns:
        str: 格式化后的进度条字符串
    """
    pc = round(min(1, current / total) * length)
    return fmts.colormode_replace(
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
    fmts.print_with_info(b, "§a 下载 ", need_log=False, end="\r")


KB = 1024
MB = 1024 * KB


def pretty_kb(n: float) -> str:
    """将字节数转换为可读性更好的字符串表示形式

    Args:
        n (float): 字节数

    Returns:
        str: 可读性更好的字符串表示形式
    """
    if n >= MB:
        return f"{round(n / MB, 2)}M"
    if n >= KB:
        return f"{round(n / KB, 2)}K"
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
        for i in [
            ".txt",
            ".yml",
            ".md",
            ".xml",
            ".html",
            ".py",
            ".h",
            ".c",
            ".pyi",
            ".js",
            ".json",
        ]
    )


def get_file_size(url: str) -> int | None:
    """
    获取文件大小 (不安全的, 有可能无法获取到正确大小)

    Args:
        url (str): 网址

    Returns:
        Union[int, None]: 文件大小（单位：字节）
    """
    response = requests.head(url, timeout=10)
    if "content-length" in response.headers:
        file_size = int(response.headers["content-length"])
        return file_size
    return None


def download_file_chunk(url: str, start_byte: int, end_byte: int, save_dir: str) -> int:
    """下载文件的代码块

    Args:
        url (str): 文件的 URL 地址
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


def download_file_singlethreaded(url: str, save_dir: str) -> None:
    """下载单个文件

    Args:
        url (str): 文件的 URL 地址
        save_dir (str): 文件保存的目录
        ignore_warnings (bool, optional): 是否忽略警告
    """
    with requests.get(url, stream=True, timeout=10) as res:
        res.raise_for_status()
        filesize = get_file_size(url)
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
        url (str): 文件的 URL 地址
        save_dir (str): 文件保存的目录
    """
    # 鉴于 Content-Length 不一定表示文件原始大小，二进制文件与文本文件需要分开下载
    # 否则显示的下载条会异常
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    if is_common_text_file(save_dir):
        # 文本文件，体积可能不大
        with open(save_dir, "wb") as f:
            f.write(resp.content)
    download_file_singlethreaded(url, save_dir)


def test_site_latency(urls: list[str]) -> list[tuple[str, float]]:
    """测试网站延迟

    Args:
        Da (dict): 包含 URL 和镜像 URL 的字典: {"url": ..., "m}

    Returns:
        list: 按延迟排序的 URL 和延迟时间的元组列表
    """
    tmp_speed: dict[str, float] = {}

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(measure_latencyt, url) for url in urls]

        for future, url in zip(as_completed(futures), urls):
            try:
                latency = future.result(timeout=5)
                if latency != -1:
                    tmp_speed[url] = latency
            except Exception as e:
                fmts.print_war(f"Error measuring latency for {url}: {e}")

    return sorted(tmp_speed.items(), key=lambda x: x[1])


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
        domain = re.search(r"(?<=http[s]://)[.\w-]*(:\d{1,8})?((?=/)|(?!/))", url)
        if isinstance(domain, type(None)):  # 如果没有匹配到域名
            raise ValueError("Invalid URL")
        st = pyspeedtest.SpeedTest(domain.group())  # 传入域名
        download_speed = st.download()
        return download_speed
    except Exception as e:
        fmts.print_war(f"Error measuring latency for {url}: {e}")
    return -1.0  # 返回 -1 表示测速失败


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
                fmts.print_war(f"端口 {port} 正被占用，跳过")
    raise ValueError(f"未找到空闲端口 ({start}~{end})")


def check_update() -> None:
    """检查更新"""
    try:
        resp = requests.get(
            f"{TDREPO_URL}/releases/latest",
            timeout=5,
        )
        resp.raise_for_status()
        latest_version = resp.json()["tag_name"]
        current_version = ".".join(map(str, get_tool_delta_version()[:3]))

        if not latest_version.replace(".", "") <= current_version.replace(".", ""):
            fmts.print_load(
                f"检测到最新版本 {current_version} -> {latest_version}，请及时更新！"
            )
    except KeyError:
        fmts.print_war("获取最新版本失败，请检查网络连接")
    except Exception as err:
        fmts.print_war(f"无法获取最新版本: {err}, 已忽略")


def get_newest_dependency_commit(mirror_src: str) -> str:
    """
    获取最新的 commit

    Args:
        mirror_src (str): like "https://ghproxy.com"
    """
    return requests.get(
        mirror_src
        + f"/https://raw.githubusercontent.com/{TDDEPENDENCY_REPO_RAW}/main/commit"
    ).text
