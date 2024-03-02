import os
import re
import shutil
import socket
import platform
from typing import Union
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import pyspeedtest
import requests

from .color_print import Print

def _pretty_kb(n: int) -> str:
    if n >= 1048576:
        return f"{round(n / 1048576, 2)}M"
    if n >= 1024:
        return f"{round(n / 1024, 2)}K"
    return f"{round(n, 1)}"

def _path_get_filename(path: str) -> Union[str, None]:
    if "/" not in path:
        return None
    return path.split("/")[-1]

def _is_common_text_file(url_path: str) -> bool:
    return any(url_path.endswith(i) for i in [".txt", ".yml", ".md", ".xml", ".py", ".h", ".c", ".pyi", ".json"])

def get_file_size(url: str) -> Union[int, None]:
    response = requests.head(url, timeout=10)
    if "Content-Length" in response.headers:
        file_size = int(response.headers["Content-Length"])
        return file_size
    return None


def download_file_chunk(url: str, start_byte: int, end_byte: int, save_dir: str) -> int:
    headers = {"Range": f"bytes={start_byte}-{end_byte}"}
    response = requests.get(url, headers=headers, stream=True, timeout=10)
    response.raise_for_status()
    with open(save_dir + ".tmp", "rb+") as dwnf:
        dwnf.seek(start_byte)
        total_bytes = end_byte - start_byte + 1
        downloaded_bytes = 0
        for chunk in response.iter_content(chunk_size=8192):
            dwnf.write(chunk)
            downloaded_bytes += len(chunk)
        return downloaded_bytes

def download_file(url: str, save_dir: str, num_threads: int = 8, ignore_warnings: bool = False) -> None:
    filesize = get_file_size(url)
    if filesize is None:
        raise ValueError("无法获取文件大小")
    if filesize < 256 and not ignore_warnings:
        Print.print_war(f"下载 {url} 的文件警告: 文件大小异常, 不到 0.25KB")
    chunk_size = filesize // num_threads  # 每个线程下载的块大小
    with open(save_dir + ".tmp", "wb") as dwnf:
        with tqdm(total=filesize, unit="B", unit_scale=True, desc=Print.fmt_info("", "§a 下载 §r"), ncols=80) as pbar:
            def update_progress(downloaded_bytes: int) -> None:
                pbar.update(downloaded_bytes)
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                futures = []
                for i in range(num_threads):
                    start_byte = i * chunk_size
                    end_byte = start_byte + chunk_size - 1
                    if i == num_threads - 1:
                        end_byte = filesize - 1
                    future = executor.submit(download_file_chunk, url, start_byte, end_byte, save_dir)
                    future.add_done_callback(lambda f: update_progress(f.result()))
                    futures.append(future)
                for future in futures:
                    future.result()
    shutil.move(save_dir + ".tmp", save_dir)

def download_unknown_file(url: str, save_dir: str) -> None:
    # 鉴于 Content-Length 不一定表示文件原始大小, 二进制文件与文本文件需要分开下载
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()

    with open(save_dir, "wb") as f:
        f.write(resp.content)

def test_site_latency(Da: dict) -> list:
    tmp_speed = {}
    urls = [Da["url"]] + Da["mirror_url"]
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(measure_latencyt, url) for url in urls]
        for future, url in zip(as_completed(futures), urls):
            latency = future.result()
            if latency != -1:
                tmp_speed[url] = latency

    sorted_speed = sorted(tmp_speed.items(), key=lambda x: x[1], reverse=True)
    return sorted_speed

def measure_latencyt(url: str) -> Union[float, int]:
    try:
        st = pyspeedtest.SpeedTest(
            re.search(r"(?<=http[s]://)[.\w-]*(:\d{,8})?((?=/)|(?!/))", url).group()
        )
        download_speed = st.download()  # / 1000000  # # 转换为兆字节/秒 （取消）
        return download_speed
    except Exception:
        return -1  # 返回-1表示测速失败

def get_free_port(start: int = 8080, end: int = 65535) -> int:
    for port in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("localhost", port))
                return port
            except OSError:
                Print.print_war(f"端口 {port} 正被占用, 跳过")
    raise Exception(f"未找到空闲端口({start}~{end})")
