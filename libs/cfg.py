import json, os

class Cfg:

    default_server_login = {
        "服务器号": 0,
        "密码": 0
    }
    std_server_login = {
        "服务器号": int,
        "密码": int
    }

    def get_cfg(path: str, std: dict):
        obj: dict = json.load(open(path, "r", encoding="utf-8"))
        for i in std.keys():
            if not isinstance(obj[i], std[i]):
                raise ValueError
        return obj

    def default_cfg(path: str, default: dict, force: bool = False):
        if not os.path.isfile(path) or force:
            json.dump(default, open(path, "w", encoding='utf-8'), indent=4, ensure_ascii=False)
