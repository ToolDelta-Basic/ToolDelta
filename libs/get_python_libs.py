from subprocess import Popen, PIPE
from libs.color_print import Print
from os import sep
from sys import argv

neccessary_libs = [
    "requests",
    "psutil",
    "nbt",
    "flask",
    "rich",
    "pymysql",
    "websocket-client",
    "qrcode",
    "tqdm"
]

def try_install_libs():
    if argv[-1].split(sep)[-1] == "ToolDelta.py":
        install_libs(neccessary_libs)

def check_pip():
    try:
        p = Popen("pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple", shell=True, stdout=PIPE, stderr=PIPE)
        p.wait()
    except Exception as err:
        Print.print_err(err)
        return False
    return not p.returncode

def get_single_lib(lib_name, lib_show_name = ""):
    lib_show_name = lib_show_name or lib_name
    cmd = f"pip install {lib_name}"
    Print.print_inf(f"正在安装库: {lib_show_name}", end = "\r")
    pipe = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    pipe.wait()
    if pipe.returncode:
        Print.print_err(f"未成功安装库: {lib_show_name}")
        raise SystemExit
    else:
        Print.print_suc(f"成功安装库: {lib_show_name}")

def install_libs(libs):
    if not check_pip():
        Print.print_err("pip 环境未就绪!")
        raise SystemExit
    for lib in libs:
        get_single_lib(lib)
