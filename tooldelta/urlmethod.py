import requests, time, os, platform
from .color_print import Print
import shutil

def _pretty_kb(n):
    if n >= 1048576:
        return f"{round(n / 1048576, 2)}M"
    elif n >= 1024:
        return f"{round(n / 1024, 2)}K"
    else:
        return f"{round(n, 1)}"
    
def _path_get_filename(path: str):
    if "/" not in path:
        return None
    else:
        return path.split("/")[-1]
    
def _is_common_text_file(url_path: str):
    for i in [".txt", ".yml", ".md", ".xml", ".py", ".h", ".c", ".pyi", ".json"]:
        if url_path.endswith(i):
            return True
    return False

def get_file_size(url):
    response = requests.head(url)
    if "Content-Length" in response.headers:
        file_size = int(response.headers["Content-Length"])
        return file_size
    else:
        return None

def download_file(f_url: str, f_dir: str, ignore_warnings=False):
    with requests.get(f_url, stream=True, timeout=10) as res:
        res.raise_for_status()
        filesize = get_file_size(f_url)

        if filesize < 256 and not ignore_warnings:
            Print.print_war(f"下载 {f_url} 的文件警告: 文件大小异常, 不到 0.25KB")

        chunk_size = 8192
        nowsize = 0
        succ = False
        lastime = time.time()
        useSpeed = 0

        with open(f_dir + ".tmp", "wb") as dwnf:
            for chk in res.iter_content(chunk_size = 8192):
                nowtime = time.time()

                if nowtime != lastime:
                    useSpeed = chunk_size / (nowtime - lastime)
                    lastime = nowtime

                nowsize += len(chk)
                dwnf.write(chk)

                if nowsize % 81920 == 0:  # 每下载 10 个数据块更新一次进度
                    prgs = nowsize / filesize
                    _tmp = int(prgs * 20)
                    bar = Print.colormode_replace(
                        "§f" + " " * _tmp + "§b" + " " * (20 - _tmp) + "§r ", 7
                    )
                    Print.print_with_info(
                        f"{bar} {_pretty_kb(nowsize)}B / {_pretty_kb(filesize)}B ({_pretty_kb(useSpeed)}B/s)    ",
                        "§a 下载 §r",
                        end="\r",
                        need_log=False,
                    )
        succ = True

        if succ:
            shutil.move(f_dir + ".tmp", f_dir)
        else:
            os.remove(f_dir + ".tmp")

def download_unknown_file(url: str, save_dir: str):
    # 鉴于 Content-Length 不一定表示文件原始大小, 二进制文件与文本文件需要分开下载
    if (_is_common_text_file(url) or
        _path_get_filename(url) in ("LICENSE",)):
        resp = requests.get(url)
        resp.raise_for_status()
        with open(save_dir, "w", encoding = "utf-8") as f:
            f.write(resp.text)
    else:
        download_file(url, save_dir)


def get_free_port(start=8080, end=65535):
    if platform.uname()[0] == "Windows":
        for port in range(start, end):
            r = os.popen(f'netstat -aon|findstr ":{port}"', "r")
            if r.read() == "":
                return port
            else:
                Print.print_war(f"端口 {port} 正被占用, 跳过")
    else:
        for port in range(start, end):
            r = os.popen(f'netstat -aon|grep ":{port}"', "r")
            if r.read() == "":
                return port
            else:
                Print.print_war(f"端口 {port} 正被占用, 跳过")
    raise Exception(f"未找到空闲端口({start}~{end})")
