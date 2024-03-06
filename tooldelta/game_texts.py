from .basic_mods import os, requests, re
from .color_print import Print

class Game_Texts(object):
    def __init__(self) -> None:
        # 检测更新!
        if not os.path.exists("data/game_texts"):
            version_match = re.match(r"v(\d+\.\d+\.\d+)", requests.get("https://api.github.com/repos/ToolDelta/ToolDelta-Game_Texts/releases/latest").json()["tag_name"])
            open("data/game_texts/version","w").write(version_match)
            packets_url = f"https://github.com/ToolDelta/ToolDelta-Game_Texts/releases/download/{version_match}"