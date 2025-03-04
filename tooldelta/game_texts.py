"还原游戏常见字符串"

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
from .constants import TDSPECIFIC_MIRROR
from .version import get_tool_delta_version

# 关闭警告
urllib3.disable_warnings()
warnings.filterwarnings("ignore")


class GameTextsLoader:
    "还原游戏常见字符串"

    def __init__(self) -> None:
        "初始化"
        self.base_path = os.path.join(os.getcwd(), "插件数据文件", "game_texts")
        self.check_initial_run()
        if "no-download-libs" not in sys_args.sys_args_to_dict():
            # 暂时不用开自动更新线程
            self.auto_update()
        self.game_texts_data: dict[str, str] = self.load_data()

    @staticmethod
    def get_latest_version() -> str:
        """获取最新版本号

        Returns:
            str: 版本号
        """
        if (
            "no-download-libs" in sys_args.sys_args_to_dict()
            or "no-update-check" in sys_args.sys_args_to_dict()
        ):
            return ".".join(map(str, get_tool_delta_version()))
        try:
            result = re.match(
                r"(\d+\.\d+\.\d+)",
                requests.get(
                    f"{TDSPECIFIC_MIRROR}/https://api.github.com/repos/ToolDelta-Basic/GameText/releases/latest",
                    timeout=5,
                    verify=True,
                ).json()["tag_name"],
            )
        except Exception:
            raise ValueError("游戏文本翻译器: 无法获取最新版本号")
        if not isinstance(result, type(None)):
            return result.group()
        raise ValueError("游戏文本翻译器: 无法获取最新版本号")

    def check_initial_run(self) -> None:
        "检查初始运行"
        version_file_path = os.path.join(self.base_path, "version")
        if not os.path.exists(version_file_path):
            latest_version = self.get_latest_version()
            with open(version_file_path, "w", encoding="utf-8") as f:
                f.write(latest_version)
            self.download_and_extract(latest_version)

    @thread_func("自动更新游戏文本翻译器内容")
    def auto_update(self) -> None:
        "自动更新"
        version_file_path: str = os.path.join(self.base_path, "version")
        with open(version_file_path, encoding="utf-8") as f:
            version: str = f.read()
        try:
            latest_version = self.get_latest_version()
            if version != latest_version:
                self.download_and_extract(latest_version)
                with open(version_file_path, "w", encoding="utf-8") as f:
                    f.write(latest_version)
        except ValueError:
            return

    def download_and_extract(self, version) -> None:
        "下载并解压"
        packets_url: str = (
            f"{TDSPECIFIC_MIRROR}/https://github.com/ToolDelta-Basic/"
            f"GameText/releases/download/{version}/"
            "ToolDelta_Game_Texts.tar.gz"
        )
        archive_path = os.path.join(self.base_path, "ToolDelta_Game_Texts.tar.gz")
        urlmethod.download_file_singlethreaded(packets_url, archive_path)
        self.extract_data_archive(archive_path)

    def load_data(self) -> dict[str, str]:
        """加载数据

        Returns:
            dict[str, str]: 数据
        """
        try:
            all_values: dict[str, str] = {}
            for file_path in glob(
                pathname=os.path.join(self.base_path, "src", "**", "*.py"),
                recursive=True,
            ):
                module_name: str = os.path.basename(file_path).replace(".py", "")
                spec = util.spec_from_file_location(module_name, file_path)
                if isinstance(spec, type(None)) or isinstance(spec.loader, type(None)):
                    fmts.print_war(f"Failed to load module from {file_path}")
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
            with (
                gzip.open(zip_path, "rb") as f_in,
                tarfile.open(
                    fileobj=f_in,
                    mode="r:gz",  # type: ignore
                ) as tar,
            ):
                tar.extractall(self.base_path)
                with open(
                    os.path.join(self.base_path, "src_tree.json"), "w", encoding="utf-8"
                ) as f:
                    json.dump(tar.getnames(), f)
                return True
        except Exception as err:
            fmts.print_war(f"Error extracting data archive: {err}")
            return False


class GameTextsHandle:
    """处理游戏文本返回"""

    def __init__(self, Game_Texts: dict[str, str]) -> None:
        self.Game_Texts = Game_Texts

    def Handle_Text_Class1(
        self, packet: dict[str, Any] | list[dict[str, Any]]
    ) -> list[str]:
        """
        处理文本返回方法 1

        Args:
            packet (Union[Dict[str, Any], List[Dict[str, Any]]]): 数据包

        Returns:
            List[str]: 处理结果的 json 格式列表
        """

        def process_item(item: dict[str, Any]) -> str:
            message_key = item["Message"].replace("%", "")
            original_message = self.Game_Texts.get(message_key)

            if original_message:
                original_message = re.sub(
                    r'\$[^"\'\]/\]\)）}\s]{0,3}', "", original_message
                )
                param_list = list(item["Parameters"])

                if not re.findall(r"%[a-zA-Z]", original_message):
                    for n in range(1, len(param_list) + 1):
                        original_message = original_message.replace(
                            f"%{n}", f"{{{n - 1}}}"
                        )

                    filtered_param_list = [
                        re.sub(r"%", "", param) for param in param_list if "%" in param
                    ]
                    for filtered_param in filtered_param_list:
                        for i in range(len(param_list)):
                            if filtered_param in param_list[i]:
                                param_list[i] = param_list[i].replace(
                                    f"%{filtered_param}",
                                    self.Game_Texts.get(filtered_param, "???"),
                                )

                    filled_message = original_message.format(*param_list)
                else:
                    formatted_string = original_message
                    for i, arg in enumerate(param_list):
                        formatted_string = re.sub(
                            r"%[a-zA-Z]", str(arg), formatted_string, count=1
                        )

                    filtered_param_list = [
                        re.sub(r"%", "", param) for param in param_list if "%" in param
                    ]
                    for filtered_param in filtered_param_list:
                        for i in range(len(param_list)):
                            if filtered_param in param_list[i]:
                                param_list[i] = param_list[i].replace(
                                    f"%{filtered_param}",
                                    self.Game_Texts.get(filtered_param, "???"),
                                )

                    filled_message = formatted_string.format(*param_list)
            else:
                filled_message = item["Message"]

            return json.dumps(filled_message, indent=2, ensure_ascii=False)

        if isinstance(packet, list):
            return [process_item(item) for item in packet]
        elif isinstance(packet, dict):
            return [process_item(packet)]
