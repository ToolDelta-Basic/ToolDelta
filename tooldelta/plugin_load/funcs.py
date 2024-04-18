"简易函数"
import zipfile
from ..color_print import Print


def unzip_plugin(zip_dir: str, exp_dir: str) -> None:
    """解压插件

    Args:
        zip_dir (str): 压缩文件路径
        exp_dir (str): 解压目录
    """
    try:
        f = zipfile.ZipFile(zip_dir, "r")
        f.extractall(exp_dir)
    except Exception as err:
        Print.print_err(f"zipfile: 解压失败: {err}")
        raise EOFError("解压失败") from err
