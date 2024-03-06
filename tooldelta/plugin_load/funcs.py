import os
import zipfile
import traceback
from tooldelta.color_print import Print


def unzip_plugin(zip_dir, exp_dir):
    try:
        f = zipfile.ZipFile(zip_dir, "r")
        f.extractall(exp_dir)
    except Exception as err:
        Print.print_err(f"zipfile: 解压失败: {err}")
        print(traceback.format_exc())
        os._exit(0)
