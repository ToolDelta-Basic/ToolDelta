from .basic_mods import os, requests, re, tarfile, gzip, json, importlib, threading, time
from .urlmethod import download_file_singlethreaded
from typing import Dict
from .color_print import Print
from glob import glob

class GameTextsLoader:
    def __init__(self) -> None:
        self.base_path = os.path.join(os.getcwd(), "插件数据文件", "game_texts")
        self.check_initial_run()
        self.start_auto_update_thread()
        self.game_texts_data: Dict[str, str] = self.load_data()

    def get_latest_version(self) -> str:
        return re.match(r"(\d+\.\d+\.\d+)", requests.get("https://api.github.com/repos/ToolDelta/ToolDelta-Game_Texts/releases/latest").json()["tag_name"]).group()

    def check_initial_run(self) -> None:
        version_file_path: str = os.path.join(self.base_path, "version")
        if not os.path.exists(version_file_path):
            latest_version: str = self.get_latest_version()
            open(version_file_path, "w").write(latest_version)
            self.download_and_extract(latest_version)

    def start_auto_update_thread(self) -> None:
        threading.Timer(24 * 60 * 60, self.auto_update).start()

    def auto_update(self) -> None:
        version_file_path: str = os.path.join(self.base_path, "version")
        version: str = open(version_file_path, "r").read()
        latest_version: str = self.get_latest_version()
        if version != latest_version:
            self.download_and_extract(latest_version)
        threading.Timer(24 * 60 * 60, self.auto_update).start()

    def download_and_extract(self, version):
        packets_url: str = f"https://hub.gitmirror.com/?q=https://github.com/ToolDelta/ToolDelta-Game_Texts/releases/download/{version}/ToolDelta_Game_Texts.tar.gz"
        archive_path = os.path.join(self.base_path, "ToolDelta_Game_Texts.tar.gz")
        download_file_singlethreaded(packets_url, archive_path)
        self.extract_data_archive(archive_path)

    def load_data(self) -> Dict[str, str]:
        try:
            all_values: Dict[str, str] = {}
            for file_path in glob(os.path.join(self.base_path, "src", "**", "*.py"), recursive=True):
                module_name: str = os.path.basename(file_path).replace(".py", "")
                spec: importlib.util.spec_from_file_location = importlib.util.spec_from_file_location(module_name, file_path)
                module: importlib.util.module_from_spec = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                for var_name in dir(module):
                    if not var_name.startswith("__"):
                        var_value = getattr(module, var_name)
                        if isinstance(var_value, dict):
                            all_values.update(var_value)
            return all_values
        except Exception as err:
            return {}

    def extract_data_archive(self, zip_path: str) -> bool:
        try:
            with gzip.open(zip_path, 'rb') as f_in:
                with tarfile.open(fileobj=f_in, mode='r') as tar:
                    tar.extractall(self.base_path)
                    open(os.path.join(self.base_path, "src_tree.json"), 'w').write(json.dumps(tar.getnames()))
                    return True
        except Exception as err:
            Print.print_war(f"Error extracting data archive: {err}")
            return False
