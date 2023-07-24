import datetime
import sys
import time

from rich import print as rprint


class _Print:
    std_color_list = [
        ["0", "[#000000]"],
        ["1", "[#0000AA]"],
        ["2", "[#00AA00]"],
        ["3", "[#00AAAA]"],
        ["4", "[#AA0000]"],
        ["5", "[#AA00AA]"],
        ["6", "[#FFAA00]"],
        ["7", "[#AAAAAA]"],
        ["8", "[#555555]"],
        ["9", "[#5555FF]"],
        ["a", "[#55FF55]"],
        ["b", "[#55FFFF]"],
        ["c", "[#FF5555]"],
        ["d", "[#FF55FF]"],
        ["e", "[#FFFF55]"],
        ["f", "[#FFFFFF]"],
        ["g", "[#DDD605]"],
        ["r", "/"]
    ]
    modes = ["[black on white] 信息 [/black on white] ", "[black on yellow] 警告 [/black on yellow] [yellow]",
             "[red on yellow] 错误 [/red on yellow] [red]", "[black on white] 输入 [/black on white] ",
             "[white on green] 成功 [/white on green] ", "[black on white] 加载 [/black on white] ",
             "[yellow on white]  FB  [/yellow on white] "]

    def _mccolor_console_common(this, text: str):
        return text.replace("§1", "\033[0;37;34m").replace("§2", "\033[0;37;32m").replace("§3",
                                                                                          "\033[0;37;36m").replace("§4",
                                                                                                                   "\033[0;37;31m").replace(
            "§5", "\033[0;37;35m").replace("§6", "\033[0;37;33m").replace("§7", "\033[0;37;90m").replace("§8",
                                                                                                         "\033[0;37;2m").replace(
            "§9", "\033[0;37;94m").replace("§a", "\033[0;37;92m").replace("§b", "\033[0;37;96m").replace("§c",
                                                                                                         "\033[0;37;91m").replace(
            "§d", "\033[0;37;95m").replace("§e", "\033[0;37;93m").replace("§f", "\033[0;37;1m").replace("§r",
                                                                                                        "\033[0m") + "\033[0m"

    def _mccolor_console_st1(this, text: str):
        return text.replace("§1", "\033[7;37;34m").replace("§2", "\033[7;37;32m").replace("§3",
                                                                                          "\033[7;37;36m").replace("§4",
                                                                                                                   "\033[7;37;31m").replace(
            "§5", "\033[7;37;35m").replace("§6", "\033[7;37;33m").replace("§7", "\033[7;37;90m").replace("§8",
                                                                                                         "\033[7;37;2m").replace(
            "§9", "\033[7;37;94m").replace("§a", "\033[7;37;92m").replace("§b", "\033[7;37;96m").replace("§c",
                                                                                                         "\033[7;37;91m").replace(
            "§d", "\033[7;37;95m").replace("§e", "\033[7;37;93m").replace("§f", "\033[7;37;1m").replace("§r",
                                                                                                        "\033[0m") + "\033[0m"

    def print_with_info(this, *args, mode=0, rmlast: bool = False, countdown=None, endmsg="倒计时结束", sep=" ",
                        end="\n",
                        file=None, flush=False):
        """
        1:[black on white] 信息 [/black on white]
        2:[black on yellow] 警告 [/black on yellow] [yellow]
        3:[red on yellow] 错误 [/red on yellow] [red]
        4:[black on white] 输入 [/black on white]
        5:[white on green] 成功 [/white on green]
        6:[black on white] 加载 [/black on white]
        7:[yellow on white]  FB  [/yellow on white]


        """
        modified_args = []
        if len(args):
            for arg in args:
                if isinstance(arg, str):
                    arg = arg.replace("§1", "[#0000AA]").replace("§2", "[#00AA00]").replace("§3",
                                                                                            "[#00AAAA]").replace("§4",
                                                                                                                 "[#AA0000]").replace(
                        "§5", "[#AA00AA]").replace("§6", "[#FFAA00]").replace("§7", "[#AAAAAA]").replace("§8",
                                                                                                         "[#555555]").replace(
                        "§9", "[#5555FF]").replace("§a", "[#55FF55]").replace("§b", "[#55FFFF]").replace("§c",
                                                                                                         "[#FF5555]").replace(
                        "§d", "[#FF55FF]").replace("§e", "[#FFFF55]").replace("§f", "[#FFFFFF]").replace("§d",
                                                                                                         "[#DDD605]").replace(
                        "§l", "[italic]")
                    modified_args.append(arg)
                else:
                    modified_args.append(arg)

        if countdown:
            for i in range(countdown, -1, -1):
                time.sleep(1)
                print(f"\r\x1b[K[{datetime.datetime.now().strftime('%H:%M:%S')}] ", end="")
                rprint(this.modes[mode], end="")
                rprint(*modified_args, f"{i}s", end="")
                sys.stdout.flush()
            print(f"\r\x1b[K[{datetime.datetime.now().strftime('%H:%M:%S')}] ", end="")
            rprint(this.modes[mode], end="")
            rprint(endmsg.replace("§1", "[#0000AA]").replace("§2", "[#00AA00]").replace("§3",
                                                                                        "[#00AAAA]").replace("§4",
                                                                                                             "[#AA0000]").replace(
                "§5", "[#AA00AA]").replace("§6", "[#FFAA00]").replace("§7", "[#AAAAAA]").replace("§8",
                                                                                                 "[#555555]").replace(
                "§9", "[#5555FF]").replace("§a", "[#55FF55]").replace("§b", "[#55FFFF]").replace("§c",
                                                                                                 "[#FF5555]").replace(
                "§d", "[#FF55FF]").replace("§e", "[#FFFF55]").replace("§f", "[#FFFFFF]").replace("§d",
                                                                                                 "[#DDD605]").replace(
                "§l", "[italic]"))
        else:
            other_mode=None
            modified_args1=modified_args
            for i in modified_args1:
                if isinstance(i, str):
                    for txt in i.split("\n"):
                        if rmlast:
                            print(f"\r\x1b[K[{datetime.datetime.now().strftime('%H:%M:%S')}] ", end="")
                        else:
                            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] ", end="")
                        if "[#FF55FF] 加载 " in modified_args:
                            modified_args.remove("[#FF55FF] 加载 ")
                            rprint(this.modes[5], end="")
                        elif "[#55FFFF] 输入 " in modified_args:
                            modified_args.remove("[#55FFFF] 输入 ")
                            rprint(this.modes[3], end="")
                        elif "[#55FFFF]  FB  " in modified_args or "[#55FFFF]  FB  §r" in modified_args:
                            try:
                                modified_args.remove("[#55FFFF]  FB  ")
                            except ValueError:
                                modified_args.remove("[#55FFFF]  FB  §r")
                            pass
                        else:
                            rprint(this.modes[mode], end="")
                        if mode == 6 or "§b  FB  " in modified_args or "§b  FB  §r" in modified_args or "[#55FFFF]  FB  " in modified_args or "[#55FFFF]  FB  §r" in modified_args:
                            print(txt, sep=sep, end=end, file=file, flush=flush)
                        else:
                            rprint(txt, sep=sep, end=end, file=file, flush=flush)
                else:
                    rprint(i, sep=sep, end="", file=file, flush=flush)
                    if len(modified_args) != 0:
                        if modified_args[len(modified_args) - 1] == i:
                            print(end="\n")

    def input(self, text: str = "") -> str:
        self.print_with_info(text, end="", mode=3)
        return input()

    def print_err(this, text: str, **print_kwargs):
        this.print_with_info(f"§c{text}", mode=2, **print_kwargs)

    def print_inf(this, text: str, **print_kwargs):
        this.print_with_info(f"{text}", mode=0, **print_kwargs)

    def print_suc(this, text: str, **print_kwargs):
        this.print_with_info(text, mode=4, **print_kwargs)

    def print_war(this, text: str, **print_kwargs):
        this.print_with_info(f"§6{text}", mode=1, **print_kwargs)

    def fmt_info(this, text: str, info: str):
        output_txts = []
        for text_line in str(text).split("\n"):
            output_txts.append(datetime.datetime.now().strftime("[%H:%M:%S] ") + this._mccolor_console_st1(
                info) + " " + this._mccolor_console_common(text_line))
        return "\n".join(output_txts)


Print = _Print()
