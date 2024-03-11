from .basic_mods import os, requests, re, tarfile, gzip, json, importlib, threading, time
from .urlmethod import download_file_singlethreaded
from typing import Dict
from .color_print import Print

class GameTextsLoader:
    def __init__(self) -> None:
        self.check_initial_run()
        self.start_auto_update_thread()
        self.game_texts_data: Dict[str, str] = self.load_data()

    def check_initial_run(self) -> None:
        version_file_path: str = os.path.join(os.getcwd(), "插件数据文件", "game_texts", "version")
        if not os.path.exists(version_file_path):
            latest_version: str = re.match(r"(\d+\.\d+\.\d+)", requests.get("https://api.github.com/repos/ToolDelta/ToolDelta-Game_Texts/releases/latest").json()["tag_name"]).group()
            open(version_file_path, "w").write(latest_version)
            packets_url: str = f"https://hub.gitmirror.com/?q=https://github.com/ToolDelta/ToolDelta-Game_Texts/releases/download/{latest_version}/ToolDelta_Game_Texts.tar.gz"
            download_file_singlethreaded(packets_url, os.path.join(os.getcwd(), "插件数据文件", "game_texts", "ToolDelta_Game_Texts.tar.gz"))
            unzipped_success: bool = self.extract_data_archive(os.path.join(os.getcwd(), "插件数据文件", "game_texts", "ToolDelta_Game_Texts.tar.gz"))

    def start_auto_update_thread(self) -> None:
        update_thread: threading.Thread = threading.Thread(target=self.auto_update_thread, daemon=True)
        update_thread.start()

    def auto_update_thread(self) -> None:
        while True:
            self.auto_update()
            time.sleep(24 * 60 * 60)

    def auto_update(self) -> None:
        version_file_path: str = os.path.join(os.getcwd(), "插件数据文件", "game_texts", "version")
        version: str = open(version_file_path, "r").read()
        latest_version: str = re.match(r"(\d+\.\d+\.\d+)", requests.get("https://api.github.com/repos/ToolDelta/ToolDelta-Game_Texts/releases/latest").json()["tag_name"]).group()
        if version != latest_version:
            packets_url: str = f"https://hub.gitmirror.com/?q=https://github.com/ToolDelta/ToolDelta-Game_Texts/releases/download/{latest_version}/ToolDelta_Game_Texts.tar.gz"
            download_file_singlethreaded(packets_url, os.path.join(os.getcwd(), "插件数据文件", "game_texts", "ToolDelta_Game_Texts.tar.gz"))
            unzipped_success: bool = self.extract_data_archive(os.path.join(os.getcwd(), "插件数据文件", "game_texts", "ToolDelta_Game_Texts.tar.gz"))

    def load_data(self) -> Dict[str, str]:
        try:
            all_values: Dict[str, str] = {}
            for root, dirs, files in os.walk(os.path.join(os.getcwd(), "插件数据文件", "game_texts", "src")):
                for file_name in files:
                    if file_name.endswith(".py"):
                        file_path: str = os.path.join(root, file_name)
                        module_name: str = file_name.replace(".py", "")
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
                    tar.extractall(os.path.join(os.getcwd(), "插件数据文件", "game_texts"))
                    open(os.path.join(os.getcwd(), "插件数据文件", "game_texts", "src_tree.json"), 'w').write(json.dumps(tar.getnames()))
                    return True
        except Exception as err:
            Print.print_war(f"Error extracting data archive: {err}")
            return False