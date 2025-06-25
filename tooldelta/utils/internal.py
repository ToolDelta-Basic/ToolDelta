import os
import sys
from tooldelta import constants

def init_dirs():
        """初始化系统文件夹"""
        os.makedirs(
            os.path.join("插件文件", constants.TOOLDELTA_CLASSIC_PLUGIN), exist_ok=True
        )
        os.makedirs("插件配置文件", exist_ok=True)
        os.makedirs(os.path.join("tooldelta", "bin"), exist_ok=True)
        os.makedirs(os.path.join("插件数据文件", "game_texts"), exist_ok=True)
        if sys.platform == "win32":
            win_create_batch_file()


def win_create_batch_file():
    if not os.path.isfile("点我启动.bat"):
        argv = sys.argv.copy()
        if argv[0].endswith(".py"):
            argv.insert(0, "python")
        exec_cmd = " ".join(argv)
        with open("点我启动.bat", "w") as f:
            f.write(f"@echo off\n{exec_cmd}\npause")
