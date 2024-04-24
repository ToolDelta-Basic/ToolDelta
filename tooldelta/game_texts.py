"还原游戏常见字符串"
import os
import re
import tarfile
import gzip
from importlib import util
import threading
from glob import glob
from typing import Dict
import requests
import ujson as json
from .urlmethod import download_file_singlethreaded
from .color_print import Print

class GameTextsLoader:
    "还原游戏常见字符串"

    def __init__(self) -> None:
        "初始化"
        self.base_path = os.path.join(os.getcwd(), "插件数据文件", "game_texts")
        self.check_initial_run()
        self.start_auto_update_thread()
        self.auto_update()
        self.game_texts_data: Dict[str, str] = self.load_data()

    @staticmethod
    def get_latest_version() -> str:
        """获取最新版本号

        Returns:
            str: 版本号
        """
        result = re.match(
            r"(\d+\.\d+\.\d+)",
            requests.get(
                "https://api.github.com/repos/ToolDelta/GameText/releases/latest", timeout=5
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
            f"https://hub.gitmirror.com/?q=https://github.com/ToolDelta/GameText/releases/download/{version}/ToolDelta_Game_Texts.tar.gz"
        )
        archive_path = os.path.join(
            self.base_path, "ToolDelta_Game_Texts.tar.gz")
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
                os.path.join(self.base_path, "src", "**", "*.py"), recursive=True
            ):
                module_name: str = os.path.basename(
                    file_path).replace(".py", "")
                spec = (
                    util.spec_from_file_location(
                        module_name, file_path)
                )
                if isinstance(spec, type(None)) or isinstance(spec.loader, type(None)):
                    Print.print_war(
                        f"Failed to load module from {file_path}")
                    continue
                module = (
                    util.module_from_spec(spec)
                )
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
                fileobj=f_in, mode="r:gz" # type: ignore
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

class GameTextsHandle(object):
    def __init__(self, Game_Texts: dict) -> None:
        self.Game_Texts = Game_Texts

    def Handle_Text_Class1(self, Pkt: dict) -> str:
        "处理文本返回方法1"
        mjon: list = []
        if type(Pkt) == list:
            for i in Pkt:
                death_message = re.sub(r'\$[^"\'\]/\]\)）}\s]{0,3}', '', self.Game_Texts.get(i["Message"].replace("%", "")))
                if not len(re.findall(r'%[a-zA-Z]', death_message)) >=1:
                    if death_message:
                        pkg_list = list(i["Parameters"])
                        for n, value in enumerate(pkg_list, start=1):
                            death_message = death_message.replace("%{}".format(n), "{" + str(n-1) + "}")
                        if len([str(item) for item in pkg_list if "%" in str(item)]) >= 1:
                            filtered_pkg_list = [re.sub(r'%', '', item) for item in pkg_list if "%" in item]
                            for filtered_item in filtered_pkg_list:
                                for i in range(len(pkg_list)):
                                    if filtered_item in pkg_list[i]:
                                        pkg_list[i] = pkg_list[i].replace(f"%{filtered_item}", self.Game_Texts.get(filtered_item))
                        filled_message = death_message.format(*pkg_list) 
                else:   
                    if death_message:
                        death_message = self.Game_Texts.get(i["Message"].replace("%", ""))
                        pkg_list = list(i["Parameters"])
                        format_specifiers = re.findall(r'%[a-zA-Z]', death_message)
                        formatted_string = death_message
                        for i, arg in enumerate(pkg_list, start=0):
                            formatted_string = re.sub(r'%[a-zA-Z]', str(arg), formatted_string, count=1)
                        if len([str(item) for item in pkg_list if "%" in str(item)]) >= 1:
                            filtered_pkg_list = [re.sub(r'%', '', item) for item in pkg_list if "%" in item]
                            for filtered_item in filtered_pkg_list:
                                for i in range(len(pkg_list)):
                                    if filtered_item in pkg_list[i]:
                                        pkg_list[i] = pkg_list[i].replace(f"%{filtered_item}", self.Game_Texts.get(filtered_item))
                        filled_message = formatted_string.format(*pkg_list) 

                jso = json.dumps(
                    filled_message, indent=2, ensure_ascii=False
                )
                mjon.append(jso)
        else:
            death_message = re.sub(r'\$[^"\'\]/\]\)）}\s]{0,3}', '', self.Game_Texts.get(Pkt["Message"].replace("%", "")))
            if not len(re.findall(r'%[a-zA-Z]', death_message)) >=1:
                if death_message:
                    pkg_list = list(Pkt["Parameters"])
                    for n, value in enumerate(pkg_list, start=1):
                        death_message = death_message.replace("%{}".format(n), "{" + str(n-1) + "}")
                    if len([str(item) for item in pkg_list if "%" in str(item)]) >= 1:
                        filtered_pkg_list = [re.sub(r'%', '', item) for item in pkg_list if "%" in item]
                        for filtered_item in filtered_pkg_list:
                            for i in range(len(pkg_list)):
                                if filtered_item in pkg_list[i]:
                                    pkg_list[i] = pkg_list[i].replace(f"%{filtered_item}", self.Game_Texts.get(filtered_item))
                    filled_message = formatted_string.format(*pkg_list)  
            else:   
                if death_message:
                    death_message = self.Game_Texts.get(Pkt["Message"].replace("%", ""))
                    pkg_list = list(Pkt["Parameters"])
                    format_specifiers = re.findall(r'%[a-zA-Z]', death_message)
                    formatted_string = death_message
                    for i, arg in enumerate(pkg_list, start=1):
                        formatted_string = re.sub(r'%[a-zA-Z]', str(arg), formatted_string, count=1)
                    if len([str(item) for item in pkg_list if "%" in str(item)]) >= 1:
                        filtered_pkg_list = [re.sub(r'%', '', item) for item in pkg_list if "%" in item]
                        for filtered_item in filtered_pkg_list:
                            for i in range(len(pkg_list)):
                                if filtered_item in pkg_list[i]:
                                    pkg_list[i] = pkg_list[i].replace(f"%{filtered_item}", self.Game_Texts.get(filtered_item))
                    filled_message =  formatted_string

            jso = json.dumps(
                filled_message, indent=2, ensure_ascii=False
            )
            mjon.append(jso)
        return mjon
    

    
    def Handle_Text_Class2(self, Pkt: dict) -> str:
        "处理文本返回方法2"
        MSG = json.loads(Pkt["Message"])
        print(MSG)
        # msg = json.loads(Pkt["Message"])
        # rawtext = msg["rawtext"]
        # for item in rawtext:
        #     if "translate" in item and "with" in item:
        #         game_text_key = item["translate"]
        #         game_text_with = item["with"]
        #     elif "translate" in item:translate = item["translate"]
        # if game_text_with == None:
        #     death_message = self.Game_Texts.get(game_text_key)
        # else:
        #     death_message = self.Game_Texts.get(game_text_key)
        #     if type(game_text_with["rawtext"]) == list:
        #         pkg_list = []
        #         for rt in game_text_with:pkg_list.append(rt["rawtext"]["text"])
        #         self.Handle_Text_Class1({"Message": game_text_key, "Parameters": pkg_list})
        #         print(c)
        #     else:
        #         c = self.Handle_Text_Class1({"Message": game_text_key, "Parameters": game_text_with["rawtext"]["text"]})
        #         print(c)

# {"rawtext":[{"text":"["},{"translate":"xingchentty"},{"text":""},{"text":": "},{"translate":"commands.time.set","with":{"rawtext":[{"text":"45342000"}]}},{"text":"]"}]}