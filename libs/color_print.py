import datetime
from .logger import publicLogger

class _Print:
    INFO_NORMAL = "§f 信息 "
    INFO_WARN = "§6 警告 "
    INFO_ERROR = "§4 报错 "
    INFO_FAIL = "§c 失败 "
    INFO_SUCC = "§a 成功 "
    INFO_LOAD = "§d 加载 "
    STD_COLOR_LIST = [
            ["0", "#000000"],
            ["1", "#0000AA"],
            ["2", "#00AA00"],
            ["3", "#00AAAA"],
            ["4", "#AA0000"],
            ["5", "#AA00AA"],
            ["6", "#FFAA00"],
            ["7", "#AAAAAA"],
            ["8", "#555555"],
            ["9", "#5555FF"],
            ["a", "#55FF55"],
            ["b", "#55FFFF"],
            ["c", "#FF5555"],
            ["d", "#FF55FF"],
            ["e", "#FFFF55"],
            ["f", "#FFFFFF"],
            ["g", "#DDD605"],
            ["r", "/"]
        ]
    def _mccolor_console_common(self, text: str):
        return text.replace("§1", "\033[0;37;34m").replace("§2", "\033[0;37;32m").replace("§3", "\033[0;37;36m").replace("§4", "\033[0;37;31m").replace("§5", "\033[0;37;35m").replace("§6", "\033[0;37;33m").replace("§7", "\033[0;37;90m").replace("§8", "\033[0;37;2m").replace("§9", "\033[0;37;94m").replace("§a", "\033[0;37;92m").replace("§b", "\033[0;37;96m").replace("§c", "\033[0;37;91m").replace("§d", "\033[0;37;95m").replace("§e", "\033[0;37;93m").replace("§f", "\033[0;37;1m").replace("§r", "\033[0m")+"\033[0m"
    
    def _mccolor_console_st1(self, text: str):
        return text.replace("§1", "\033[7;37;34m").replace("§2", "\033[7;37;32m").replace("§3", "\033[7;37;36m").replace("§4", "\033[7;37;31m").replace("§5", "\033[7;37;35m").replace("§6", "\033[7;37;33m").replace("§7", "\033[7;37;90m").replace("§8", "\033[7;37;2m").replace("§9", "\033[7;37;94m").replace("§a", "\033[7;37;92m").replace("§b", "\033[7;37;96m").replace("§c", "\033[7;37;91m").replace("§d", "\033[7;37;95m").replace("§e", "\033[7;37;93m").replace("§f", "\033[7;37;1m").replace("§r", "\033[0m")+"\033[0m"

    def print_with_info(self, text: str, info: str = INFO_NORMAL, **print_kwargs):
        self.c_log(info, text)
        setNextCol = "§r"
        if "\n" in text:
            output_txts = []
            for text_line in str(text).split("\n"):
                if "§" in text_line:
                    try:
                        n = text_line.rfind("§")
                        _setNextCol = text_line[n:n+2]
                        assert setNextCol != -1
                        setNextCol = _setNextCol
                    except:
                        pass
                output_txts.append(datetime.datetime.now().strftime("[%H:%M] ") + self._mccolor_console_st1(info) + " " + self._mccolor_console_common(setNextCol + text_line))
            print("\n".join(output_txts), **print_kwargs)
        else:
            print(datetime.datetime.now().strftime("[%H:%M] ") + self._mccolor_console_st1(info) + " " + self._mccolor_console_common(text), **print_kwargs)

    def print_err(self, text: str, **print_kwargs):
        self.print_with_info(f"§c{text}", self.INFO_ERROR, **print_kwargs)

    def print_inf(self, text: str, **print_kwargs):
        self.print_with_info(f"{text}", self.INFO_NORMAL, **print_kwargs)

    def print_suc(self, text: str, **print_kwargs):
        self.print_with_info(f"§a{text}", self.INFO_SUCC, **print_kwargs)

    def print_war(self, text: str, **print_kwargs):
        self.print_with_info(f"§6{text}", self.INFO_WARN, **print_kwargs)

    def fmt_info(self, text: str, info: str):
        output_txts = []
        for text_line in str(text).split("\n"):
            output_txts.append(datetime.datetime.now().strftime("[%H:%M] ") + self._mccolor_console_st1(info) + " " + self._mccolor_console_common(text_line))
        return "\n".join(output_txts)
    
    def c_log(self, inf, msg):
        for _g, _s in [("§6 警告 ", "WARN"), ("§a 成功 ", "INFO"), ("§f 信息 ", "INFO"), ("§c 失败 ", "FAIL"), ("§4 报错 ", "ERROR")]:
            if inf == _g:
                inf = _s
                break
        for col, _ in self.STD_COLOR_LIST:
            col = "§" + col
            msg = msg.replace(col, "")
        for col, _ in self.STD_COLOR_LIST:
            col = "§" + col
            inf = inf.replace(col, "")
        inf = inf.replace(" ", "")
        publicLogger.log_in(msg, inf)
    
Print = _Print()
