"还原游戏常见字符串"

import gzip
import os
import re
import tarfile
import threading
import warnings
from glob import glob
from importlib import util
from typing import Dict

import requests
import ujson as json
import urllib3

from .color_print import Print
from .constants import TDSPECIFIC_MIRROR
from .get_tool_delta_version import get_tool_delta_version
from .sys_args import sys_args_to_dict
from .urlmethod import download_file_singlethreaded

# 关闭警告
urllib3.disable_warnings()
warnings.filterwarnings("ignore")


class GameTextsLoader:
    "还原游戏常见字符串"

    def __init__(self) -> None:
        "初始化"
        self.base_path = os.path.join(os.getcwd(), "插件数据文件", "game_texts")
        self.check_initial_run()
        if "no-download-libs" not in sys_args_to_dict():
            self.start_auto_update_thread()
            self.auto_update()
        self.game_texts_data: Dict[str, str] = self.load_data()

    @staticmethod
    def get_latest_version() -> str:
        """获取最新版本号

        Returns:
            str: 版本号
        """
        if (
            "no-download-libs" in sys_args_to_dict()
            or "no-update-check" in sys_args_to_dict()
        ):
            return ".".join(map(str, get_tool_delta_version()))
        result = re.match(
            r"(\d+\.\d+\.\d+)",
            requests.get(
                "https://tdload.tblstudio.cn/https://api.github.com/repos/ToolDelta/GameText/releases/latest",
                timeout=5,
                verify=True,
            ).json()["tag_name"],
        )
        if not isinstance(result, type(None)):
            return result.group()
        raise ValueError("无法获取最新版本号")

    def check_initial_run(self) -> None:
        "检查初始运行"
        version_file_path: str = os.path.join(self.base_path, "version")
        if not os.path.exists(version_file_path):
            latest_version: str = self.get_latest_version()
            with open(version_file_path, "w", encoding="utf-8") as f:
                f.write(latest_version)
            self.download_and_extract(latest_version)

    def start_auto_update_thread(self) -> None:
        "启用自动更新线程"
        threading.Timer(24 * 60 * 60, self.auto_update).start()

    def auto_update(self) -> None:
        "自动更新"
        version_file_path: str = os.path.join(self.base_path, "version")
        with open(version_file_path, "r", encoding="utf-8") as f:
            version: str = f.read()
        latest_version: str = self.get_latest_version()
        if version != latest_version:
            self.download_and_extract(latest_version)
            with open(version_file_path, "w", encoding="utf-8") as f:
                f.write(latest_version)

    def download_and_extract(self, version) -> None:
        "下载并解压"
        packets_url: str = (
            f"{TDSPECIFIC_MIRROR}/https://github.com/ToolDelta/"
            f"GameText/releases/download/{version}/"
            "ToolDelta_Game_Texts.tar.gz"
        )
        archive_path = os.path.join(self.base_path, "ToolDelta_Game_Texts.tar.gz")
        download_file_singlethreaded(packets_url, archive_path)
        self.extract_data_archive(archive_path)

    def load_data(self) -> Dict[str, str]:
        """加载数据

        Returns:
            Dict[str, str]: 数据
        """
        try:
            all_values: Dict[str, str] = {}
            for file_path in glob(
                pathname=os.path.join(self.base_path, "src", "**", "*.py"),
                recursive=True,
            ):
                module_name: str = os.path.basename(file_path).replace(".py", "")
                spec = util.spec_from_file_location(module_name, file_path)
                if isinstance(spec, type(None)) or isinstance(spec.loader, type(None)):
                    Print.print_war(f"Failed to load module from {file_path}")
                    continue
                module = util.module_from_spec(spec)
                spec.loader.exec_module(module)
                for var_name in dir(module):
                    if not var_name.startswith("__"):
                        var_value = getattr(module, var_name)
                        if isinstance(var_value, dict):
                            all_values.update(var_value)
            return all_values
        except Exception as err:
            print(f"Error loading game texts data: {err}")
            return {}

    def extract_data_archive(self, zip_path: str) -> bool:
        """解压数据归档

        Args:
            zip_path (str): 压缩包路径

        Returns:
            bool: 是否成功
        """
        try:
            with gzip.open(zip_path, "rb") as f_in, tarfile.open(
                fileobj=f_in,  # type: ignore
                mode="r:gz",
            ) as tar:
                tar.extractall(self.base_path)
                with open(
                    os.path.join(self.base_path, "src_tree.json"), "w", encoding="utf-8"
                ) as f:
                    json.dump(tar.getnames(), f)
                return True
        except Exception as err:
            Print.print_war(f"Error extracting data archive: {err}")
            return False


class GameTextsHandle:
    """处理游戏文本返回"""

    def __init__(self, Game_Texts: dict) -> None:
        self.Game_Texts = Game_Texts

    def Handle_Text_Class1(self, packet: dict | list) -> list:
        """处理文本返回方法 1

        Args:
            packet (dict | list): 数据包

        Returns:
            list: 处理结果的 json 格式列表
        """
        json_result: list = []  # 使用 list 保存处理后的结果
        if isinstance(packet, list):  # 如果 packet 是 list 类型
            for item in packet:  # 遍历 packet 中的每个 item
                # 从 self.Game_Texts 中获取原始消息文本
                if not isinstance(
                    (
                        original_message := self.Game_Texts.get(
                            item["Message"].replace("%", "")
                        )
                    ),
                    type(None),
                ):
                    # 检查原始消息中是否包含格式化参数%
                    if not len(re.findall(r"%[a-zA-Z]", original_message)) >= 1:
                        if original_message:  # 如果原始消息不为空
                            original_message = re.sub(
                                r'\$[^"\'\]/\]\)）}\s]{0,3}', "", original_message
                            )  # 删除$后的内容
                            param_list = list(item["Parameters"])  # 获取参数列表
                            for n, _ in enumerate(param_list, start=1):
                                original_message = original_message.replace(
                                    f"{n}", f"{{{n - 1}}}"
                                )
                            # 检查参数中是否包含%
                            if (
                                len(
                                    [
                                        str(param)
                                        for param in param_list
                                        if "%" in str(param)
                                    ]
                                )
                                >= 1
                            ):
                                # 提取参数中的%后的字符并替换为实际的值
                                filtered_param_list = [
                                    re.sub(r"%", "", param)
                                    for param in param_list
                                    if "%" in param
                                ]
                                for filtered_param in filtered_param_list:
                                    for i in range(len(param_list)):
                                        if filtered_param in param_list[i]:
                                            param_list[i] = param_list[i].replace(
                                                f"%{filtered_param}",
                                                self.Game_Texts.get(
                                                    filtered_param, "???"
                                                ),
                                            )
                            # 格式化消息文本
                            filled_message = original_message.format(*param_list)
                    else:
                        if original_message:  # 如果原始消息不为空
                            original_message = re.sub(
                                r'\$[^"\'\]/\]\)）}\s]{0,3}', "", original_message
                            )  # 删除$后的内容
                            param_list = list(item["Parameters"])  # 获取参数列表
                            re.findall(r"%[a-zA-Z]", original_message)  # 查找格式化参数
                            formatted_string = original_message
                            for i, arg in enumerate(param_list, start=0):
                                formatted_string = re.sub(
                                    r"%[a-zA-Z]", str(arg), formatted_string, count=1
                                )
                            if (
                                len(
                                    [
                                        str(param)
                                        for param in param_list
                                        if "%" in str(param)
                                    ]
                                )
                                >= 1
                            ):
                                # 提取参数中的%后的字符并替换为实际的值
                                filtered_param_list = [
                                    re.sub(r"%", "", param)
                                    for param in param_list
                                    if "%" in param
                                ]
                                for filtered_param in filtered_param_list:
                                    for i in range(len(param_list)):
                                        if filtered_param in param_list[i]:
                                            param_list[i] = param_list[i].replace(
                                                f"%{filtered_param}",
                                                self.Game_Texts.get(filtered_param),
                                            )
                            # 格式化消息文本
                            filled_message = formatted_string.format(*param_list)
                else:
                    filled_message = item["Message"]
                # 将填充后的消息文本转换为 json 格式，并添加到结果列表中
                json_output = json.dumps(filled_message, indent=2, ensure_ascii=False)
                json_result.append(json_output)
        elif isinstance(packet, dict):  # 如果 packet 不是 list 类型
            # 从 self.Game_Texts 中获取原始消息文本
            if not isinstance(
                (
                    original_message := self.Game_Texts.get(
                        packet["Message"].replace("%", "")
                    )
                ),
                type(None),
            ):
                if not len(re.findall(r"%[a-zA-Z]", original_message)) >= 1:
                    if original_message:  # 如果原始消息不为空
                        original_message = re.sub(
                            r'\$[^"\'\]/\]\)）}\s]{0,3}', "", original_message
                        )  # 删除$后的内容
                        param_list = list(packet["Parameters"])  # 获取参数列表
                        for n, _ in enumerate(param_list, start=1):
                            original_message = original_message.replace(
                                f"%{n}", "{" + str(n - 1) + "}"
                            )
                        if (
                            len(
                                [
                                    str(param)
                                    for param in param_list
                                    if "%" in str(param)
                                ]
                            )
                            >= 1
                        ):
                            # 提取参数中的%后的字符并替换为实际的值
                            filtered_param_list = [
                                re.sub(r"%", "", param)
                                for param in param_list
                                if "%" in param
                            ]
                            for filtered_param in filtered_param_list:
                                for i in range(len(param_list)):
                                    if filtered_param in param_list[i]:
                                        param_list[i] = param_list[i].replace(
                                            f"%{filtered_param}",
                                            self.Game_Texts.get(filtered_param),
                                        )
                        # 格式化消息文本
                        filled_message = original_message.format(*param_list)
                else:
                    if original_message := self.Game_Texts.get(
                        packet["Message"].replace("%", "")
                    ):  # 如果原始消息不为空
                        param_list = list(packet["Parameters"])  # 获取参数列表
                        original_message = re.sub(
                            r'\$[^"\'\]/\]\)）}\s]{0,3}', "", original_message
                        )  # 删除$后的内容
                        formatted_string = original_message
                        for i, arg in enumerate(param_list, start=1):
                            formatted_string = re.sub(
                                r"%[a-zA-Z]", str(arg), formatted_string, count=1
                            )
                        if (
                            len(
                                [
                                    str(param)
                                    for param in param_list
                                    if "%" in str(param)
                                ]
                            )
                            >= 1
                        ):
                            # 提取参数中的%后的字符并替换为实际的值
                            filtered_param_list = [
                                re.sub(r"%", "", param)
                                for param in param_list
                                if "%" in param
                            ]
                            for filtered_param in filtered_param_list:
                                for i in range(len(param_list)):
                                    if filtered_param in param_list[i]:
                                        param_list[i] = param_list[i].replace(
                                            f"%{filtered_param}",
                                            self.Game_Texts.get(filtered_param),
                                        )

                        filled_message = formatted_string
            else:
                filled_message = packet["Message"]
            # 将填充后的消息文本转换为 json 格式，并添加到结果列表中
            json_output = json.dumps(filled_message, indent=2, ensure_ascii=False)
            json_result.append(json_output)
        return json_result  # 返回处理结果的 json 格式列表
