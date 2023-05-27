import datetime
class _Print:
    std_color_list = [
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
    def _mccolor_console_common(this, text: str):
        return text.replace("§1", "\033[0;37;34m").replace("§2", "\033[0;37;32m").replace("§3", "\033[0;37;36m").replace("§4", "\033[0;37;31m").replace("§5", "\033[0;37;35m").replace("§6", "\033[0;37;33m").replace("§7", "\033[0;37;90m").replace("§8", "\033[0;37;2m").replace("§9", "\033[0;37;94m").replace("§a", "\033[0;37;92m").replace("§b", "\033[0;37;96m").replace("§c", "\033[0;37;91m").replace("§d", "\033[0;37;95m").replace("§e", "\033[0;37;93m").replace("§f", "\033[0;37;1m").replace("§r", "\033[0m")+"\033[0m"
    
    def _mccolor_console_st1(this, text: str):
        return text.replace("§1", "\033[7;37;34m").replace("§2", "\033[7;37;32m").replace("§3", "\033[7;37;36m").replace("§4", "\033[7;37;31m").replace("§5", "\033[7;37;35m").replace("§6", "\033[7;37;33m").replace("§7", "\033[7;37;90m").replace("§8", "\033[7;37;2m").replace("§9", "\033[7;37;94m").replace("§a", "\033[7;37;92m").replace("§b", "\033[7;37;96m").replace("§c", "\033[7;37;91m").replace("§d", "\033[7;37;95m").replace("§e", "\033[7;37;93m").replace("§f", "\033[7;37;1m").replace("§r", "\033[0m")+"\033[0m"

    def print_with_info(this, text: str, info: str, **print_kwargs):
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
                output_txts.append(datetime.datetime.now().strftime("[%H:%M] ") + this._mccolor_console_st1(info) + " " + this._mccolor_console_common(setNextCol + text_line))
            print("\n".join(output_txts), **print_kwargs)
        else:
            print(datetime.datetime.now().strftime("[%H:%M:%S] ") + this._mccolor_console_st1(info) + " " + this._mccolor_console_common(text), **print_kwargs)

    def print_err(this, text: str, **print_kwargs):
        this.print_with_info(f"§c{text}", "§c 报错 ", **print_kwargs)

    def print_inf(this, text: str, **print_kwargs):
        this.print_with_info(f"{text}", "§f 信息 ", **print_kwargs)

    def print_suc(this, text: str, **print_kwargs):
        this.print_with_info(f"§a{text}", "§a 成功 ", **print_kwargs)

    def print_war(this, text: str, **print_kwargs):
        this.print_with_info(f"§6{text}", "§6 警告 ", **print_kwargs)

    def fmt_info(this, text: str, info: str):
        output_txts = []
        for text_line in str(text).split("\n"):
            output_txts.append(datetime.datetime.now().strftime("[%H:%M:%S] ") + this._mccolor_console_st1(info) + " " + this._mccolor_console_common(text_line))
        return "\n".join(output_txts)
    
Print = _Print()