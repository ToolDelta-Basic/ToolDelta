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

        if filesize < 256 and "404" in res.text:
            raise requests.RequestException("下载失败: 返回 404")
        elif filesize < 256 and not ignore_warnings:
            Print.print_war(f"下载 {f_url} 的文件警告: 文件大小异常, 不到 0.25KB")

        nowsize = 0
        succ = False
        lastime = time.time()
        useSpeed = 0

        with open(f_dir + ".tmp", "wb") as dwnf:
            for chk in res.iter_content(chunk_size = 8192):
                nowtime = time.time()

                if nowtime != lastime:
                    useSpeed = 1024 / (nowtime - lastime)
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

                if nowsize / filesize > 1:
                    Print.print_war(f"下载: 实际大小已超出文件大小 {round(nowsize / filesize, 2)} 倍")

        succ = True

        if succ:
            shutil.move(f_dir + ".tmp", f_dir)
        else:
            os.remove(f_dir + ".tmp")


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
