"""
游戏文本翻译器模块
功能：从指定仓库下载游戏文本翻译数据，并提供文本处理功能
用于将游戏中的原始消息（如%开头的标识符）替换为本地化文本
"""

import gzip
import os
import re
import tarfile
import warnings
from glob import glob
from importlib import util
from typing import Any

import requests
import json
import urllib3

from .utils import thread_func, sys_args, urlmethod
from .utils import fmts
from .constants import TDSPECIFIC_MIRROR  # 镜像地址常量
from .version import get_tool_delta_version  # 获取当前版本

# 关闭不必要的警告
urllib3.disable_warnings()
warnings.filterwarnings("ignore")

# 预编译正则表达式，用于高效文本处理
DOLLAR_PATTERN = re.compile(r'\$[^"\'\]/\]\)）}\s]{0,3}')  # 匹配$开头的特殊字符
ALPHA_PERCENT_PATTERN = re.compile(r"%[a-zA-Z]")  # 匹配%后跟字母（如%a, %b）
DIGIT_PERCENT_PATTERN = re.compile(r"%(\d+)")  # 匹配%后跟数字（如%1, %2）
PARAM_PERCENT_PATTERN = re.compile(r"%([^\s%]+)")  # 匹配%后跟非空白字符


class GameTextsLoader:
    """游戏文本加载器
    负责从远程仓库下载、更新和加载游戏文本翻译数据
    """

    def __init__(self) -> None:
        """初始化加载器"""
        # 设置数据存储基础路径
        self.base_path = os.path.join(os.getcwd(), "插件数据文件", "game_texts")
        # 检查并执行首次运行设置
        self.check_initial_run()

        # 检查是否跳过库下载
        if "no-download-libs" not in sys_args.sys_args_to_dict():
            # 自动更新数据（暂时不在独立线程中运行）
            fmts.print_inf("游戏文本翻译器: 正在检查更新..")
            self.auto_update()
            fmts.print_suc("游戏文本翻译器: 更新检查完成")

        # 加载游戏文本数据到内存
        self.game_texts_data: dict[str, str] = self.load_data()

    @staticmethod
    def get_latest_version() -> str:
        """获取最新版本号
        从GitHub仓库获取最新发布的版本标签

        Returns:
            str: 版本号字符串 (如'1.2.3')
        """
        # 如果设置了跳过下载或跳过更新检查，则返回当前版本
        if (
            "no-download-libs" in sys_args.sys_args_to_dict()
            or "no-update-check" in sys_args.sys_args_to_dict()
        ):
            return ".".join(map(str, get_tool_delta_version()))

        try:
            # 通过镜像访问GitHub API
            response = requests.get(
                f"{TDSPECIFIC_MIRROR}/https://api.github.com/repos/ToolDelta-Basic/GameText/releases/latest",
                timeout=5,
                verify=True,
            )
            # 从标签名中提取版本号
            result = re.match(r"(\d+\.\d+\.\d+)", response.json()["tag_name"])
            if result:
                return result.group()
        except Exception as err:
            # 错误处理
            fmts.print_war(f"获取最新版本失败: {err}")
        raise ValueError("游戏文本翻译器: 无法获取最新版本号")

    def check_initial_run(self) -> None:
        """检查初始运行状态
        如果是首次运行，创建目录并下载初始数据
        """
        version_file_path = os.path.join(self.base_path, "version")
        # 如果版本文件不存在，说明是首次运行
        if not os.path.exists(version_file_path):
            # 创建目录结构
            os.makedirs(self.base_path, exist_ok=True)
            # 获取最新版本
            latest_version = self.get_latest_version()
            # 写入版本文件
            with open(version_file_path, "w", encoding="utf-8") as f:
                f.write(latest_version)
            # 下载并解压数据
            self.download_and_extract(latest_version)

    @thread_func("自动更新游戏文本翻译器内容")
    def auto_update(self) -> None:
        """自动更新数据
        在后台线程中检查并更新游戏文本数据
        """
        version_file_path: str = os.path.join(self.base_path, "version")
        if not os.path.exists(version_file_path):
            return

        # 读取当前版本
        with open(version_file_path, encoding="utf-8") as f:
            version: str = f.read()

        try:
            # 获取最新版本
            latest_version = self.get_latest_version()
            # 如果版本不同则更新
            if version != latest_version:
                fmts.print_inf(
                    f"发现新版本: {version} -> {latest_version}, 正在更新..."
                )
                self.download_and_extract(latest_version)
                # 更新版本文件
                with open(version_file_path, "w", encoding="utf-8") as f:
                    f.write(latest_version)
                fmts.print_suc("游戏文本数据更新完成")
        except ValueError as err:
            fmts.print_war(f"自动更新失败: {err}")

    def download_and_extract(self, version) -> None:
        """下载并解压数据包

        Args:
            version: 要下载的版本号
        """
        # 构建下载URL
        packets_url: str = (
            f"{TDSPECIFIC_MIRROR}/https://github.com/ToolDelta-Basic/"
            f"GameText/releases/download/{version}/"
            "ToolDelta_Game_Texts.tar.gz"
        )
        # 本地保存路径
        archive_path = os.path.join(self.base_path, "ToolDelta_Game_Texts.tar.gz")
        fmts.print_inf(f"下载游戏文本数据: {packets_url}")
        # 下载文件
        urlmethod.download_file_singlethreaded(packets_url, archive_path)
        # 解压文件
        self.extract_data_archive(archive_path)

    def load_data(self) -> dict[str, str]:
        """加载游戏文本数据
        从解压后的文件中加载所有翻译映射

        Returns:
            dict[str, str]: 游戏文本映射字典
        """
        all_values: dict[str, str] = {}
        src_dir = os.path.join(self.base_path, "src")

        # 检查源目录是否存在
        if not os.path.exists(src_dir):
            fmts.print_war(f"源目录不存在: {src_dir}")
            return {}

        # 递归查找所有Python文件
        fmts.print_inf("加载游戏文本数据...")
        for file_path in glob(
            pathname=os.path.join(src_dir, "**", "*.py"),
            recursive=True,
        ):
            # 提取模块名（不含扩展名）
            module_name: str = os.path.splitext(os.path.basename(file_path))[0]
            # 动态创建模块规范
            spec = util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                fmts.print_war(f"无法从 {file_path} 加载模块规范")
                continue

            try:
                # 创建并执行模块
                module = util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # 遍历模块属性
                for var_name in dir(module):
                    # 跳过特殊属性
                    if var_name.startswith("__"):
                        continue
                    var_value = getattr(module, var_name)
                    # 如果是字典则合并到总字典
                    if isinstance(var_value, dict):
                        all_values.update(var_value)
            except Exception as err:
                fmts.print_war(f"加载模块 {file_path} 错误: {err}")

        fmts.print_suc(f"成功加载 {len(all_values)} 条游戏文本")
        return all_values

    def extract_data_archive(self, zip_path: str) -> bool:
        """解压数据压缩包

        Args:
            zip_path (str): 压缩文件路径

        Returns:
            bool: 解压是否成功
        """
        try:
            fmts.print_inf(f"解压游戏文本数据: {zip_path}")
            # 使用gzip和tarfile解压.tar.gz文件
            with gzip.open(zip_path, "rb") as f_in:
                with tarfile.open(fileobj=f_in, mode="r:gz") as tar:
                    # 解压到目标目录
                    tar.extractall(self.base_path)
                    # 获取解压文件列表
                    names = tar.getnames()
                    if names:
                        # 保存文件树结构
                        with open(
                            os.path.join(self.base_path, "src_tree.json"),
                            "w",
                            encoding="utf-8",
                        ) as f:
                            json.dump(names, f)
            fmts.print_suc("解压完成")
            return True
        except Exception as err:
            fmts.print_war(f"解压数据包错误: {err}")
            return False


class GameTextsHandle:
    """游戏文本处理器
    使用加载的文本数据来处理游戏中的原始消息
    """

    def __init__(self, Game_Texts: dict[str, str]) -> None:
        """初始化处理器
        Args:
            Game_Texts (dict[str, str]): 游戏文本映射字典
        """
        self.Game_Texts = Game_Texts

    def Handle_Text_Class1(
        self, packet: dict[str, Any] | list[dict[str, Any]]
    ) -> list[str]:
        """
        处理文本方法1 - 主要文本处理逻辑
        将包含%占位符的游戏原始消息转换为本地化文本

        Args:
            packet: 游戏原始数据包，可以是单个字典或字典列表
               格式要求:
               - "Message": 包含%标识的消息键
               - "Parameters": 用于填充的参数列表

        Returns:
            list[str]: 处理后的消息列表(JSON格式)
        """

        def replace_params(s: str, params: list[str]) -> str:
            """递归替换参数中的%标记
            处理参数本身可能包含的%占位符

            Args:
                s: 原始字符串
                params: 参数列表

            Returns:
                str: 处理后的字符串
            """
            # 遍历参数列表
            for i, param in enumerate(params):
                # 只处理包含%的参数
                if "%" not in param:
                    continue

                # 替换参数中的%标记
                new_param = PARAM_PERCENT_PATTERN.sub(
                    # 从游戏文本字典中查找替换，找不到则保留原值
                    lambda m: self.Game_Texts.get(m.group(1), param) or param,
                    param,
                )
                # 如果参数被修改，更新参数列表
                if new_param != param:
                    params[i] = new_param
            return s

        def process_item(item: dict[str, Any]) -> str:
            """处理单个数据项

            Args:
                item: 包含Message和Parameters的字典

            Returns:
                str: 处理后的消息(JSON格式)
            """
            # 提取消息键(去掉%)
            message_key = item["Message"].replace("%", "")
            # 从字典中获取原始消息
            original_message = self.Game_Texts.get(message_key)

            # 如果找不到翻译，返回原始消息
            if not original_message:
                return json.dumps(item["Message"], indent=2, ensure_ascii=False)

            # 清理原始消息(移除$开头的特殊字符)
            original_message = DOLLAR_PATTERN.sub("", original_message)
            # 获取参数列表(复制避免修改原始数据)
            param_list = list(item["Parameters"])

            # 检查消息中是否包含字母占位符(如%a, %b)
            has_alpha = ALPHA_PERCENT_PATTERN.search(original_message) is not None

            if not has_alpha:
                # ====== 处理数字占位符(如%1, %2) ======

                # 将%1, %2转换为{0}, {1}格式
                def replace_num(match):
                    """数字占位符转换函数"""
                    # 将数字减1转换为0-based索引
                    return "{" + str(int(match.group(1)) - 1) + "}"

                # 替换所有数字占位符
                original_message = DIGIT_PERCENT_PATTERN.sub(
                    replace_num, original_message
                )

                # 替换参数中的%标记(递归处理)
                original_message = replace_params(original_message, param_list)

                try:
                    # 使用format方法填充参数
                    filled_message = original_message.format(*param_list)
                except (IndexError, KeyError):
                    # 参数不匹配时使用原始消息
                    filled_message = original_message
            else:
                # ====== 处理字母占位符 ======
                formatted_string = original_message

                # 逐个替换字母占位符
                for arg in param_list:
                    # 如果没有字母占位符了，提前退出
                    if not ALPHA_PERCENT_PATTERN.search(formatted_string):
                        break
                    # 替换第一个匹配的字母占位符
                    formatted_string = ALPHA_PERCENT_PATTERN.sub(
                        str(arg), formatted_string, count=1
                    )

                # 替换参数中的%标记(递归处理)
                formatted_string = replace_params(formatted_string, param_list)
                filled_message = formatted_string

            # 返回处理后的消息(JSON格式)
            return json.dumps(filled_message, indent=2, ensure_ascii=False)

        # 处理单个或多个数据项
        if isinstance(packet, list):
            return [process_item(item) for item in packet]
        return [process_item(packet)]
