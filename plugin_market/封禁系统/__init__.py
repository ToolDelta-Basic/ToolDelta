import time
from tooldelta import plugins, Plugin, Frame, Builtins, Print, Config


@plugins.add_plugin_as_api("封禁系统")
class BanSystem(Plugin):
    name = "封禁系统"
    author = "SuperScript"
    version = (0, 0, 1)
    description = "便捷美观地封禁玩家, 同时也是一个前置插件"
    BAN_DATA_DEFAULT = {"BanTo": 0, "Reason": ""}

    def __init__(self, frame: Frame):
        self.frame = frame
        self.game_ctrl = frame.get_game_control()
        self.tmpjson = Builtins.TMPJson
        STD_BAN_CFG = {"踢出玩家提示格式": str, "玩家被封禁的广播提示": str}
        DEFAULT_BAN_CFG = {
            "踢出玩家提示格式": "§c你因为 [ban原因]\n被系统封禁至 §6[日期] [时间]",
            "玩家被封禁的广播提示": "§6WARNING: §c[玩家名] 因为[ban原因] 被系统封禁至 §6[日期] [时间]",
        }
        self.cfg, _ = Config.getPluginConfigAndVersion(
            self.name, STD_BAN_CFG, DEFAULT_BAN_CFG, self.version
        )

    def on_def(self):
        self.chatbar = plugins.get_plugin_api("聊天栏菜单", (0, 0, 1))

    @Builtins.run_as_new_thread
    def on_inject(self):
        self.chatbar.add_trigger(
            ["ban", "封禁"],
            "[玩家名] [年]/[月]/[日] [时]:[分] [原因, 不填为未知原因]",
            "封禁玩家",
            self.ban_who,
            lambda x: x in (3, 4),
            True,
        )
        for i in self.game_ctrl.allplayers:
            self.test_ban(i)

    # -------------- API --------------
    def ban(self, player: str, ban_to_time_ticks: int, reason: str = ""):
        # player: 需要ban的玩家
        # ban_to_time_ticks: 将其封禁直到(时间戳, 和time.time()一样)
        # reason: 原因
        ban_datas = self.BAN_DATA_DEFAULT.copy()
        ban_datas["BanTo"] = ban_to_time_ticks
        ban_datas["Reason"] = reason
        self.rec_ban_data(player, ban_datas)
        if player in self.game_ctrl.allplayers:
            self.test_ban(player)

    # ----------------------------------

    @Builtins.run_as_new_thread
    def on_player_join(self, player: str):
        self.test_ban(player)

    def ban_who(self, caller: str, args: list[str]):
        if not self.frame.launcher.is_op(caller):
            self.game_ctrl.say_to(caller, "§c封禁系统: 你不是管理员")
            return
        if len(args) == 3:
            target, ymd, hms = args
            reason = ""
        else:
            target, ymd, hms, reason = args
        all_matches = Builtins.fuzzy_match(self.game_ctrl.allplayers, target)
        if all_matches == []:
            self.game_ctrl.say_to(caller, f"§c封禁系统: 无匹配名字关键词的玩家: {target}")
        elif len(all_matches) > 1:
            self.game_ctrl.say_to(
                caller, f"§c封禁系统: 匹配到多个玩家符合要求: {', '.join(all_matches)}"
            )
        else:
            try:
                struct_time = time.strptime(
                    ymd.strip() + " " + hms.strip(), "%Y年%m月%d日 %H:%M"
                )
            except ValueError:
                self.game_ctrl.say_to(caller, "§c封禁玩家: 封禁时间格式不正确")
                return
            self.ban(all_matches[0], time.mktime(struct_time), reason)
            self.game_ctrl.say_to(caller, "§c封禁系统: §f设置封禁成功.")

    def test_ban(self, player):
        ban_data = self.get_ban_data(player)
        ban_to, reason = ban_data["BanTo"], ban_data["Reason"]
        if ban_to > time.time():
            self.game_ctrl.sendwocmd(
                f"/kick {player} {self.format_msg(player, ban_to, reason, '踢出玩家提示格式')}"
            )
            self.game_ctrl.say_to(
                "@a", self.format_msg(player, ban_to, reason, "玩家被封禁的广播提示")
            )
            # 防止出现无法执行的指令
            self.game_ctrl.sendwocmd(f"/kick {player}")

    def format_msg(self, player: str, ban_to_sec: int, ban_reason: str, cfg_key: str):
        struct_time = time.gmtime(ban_to_sec)
        date_show = time.strftime("%Y年 %m月 %d日", struct_time)
        time_show = time.strftime("%H : %M : %S", struct_time)
        Print.print_inf(
            f"封禁系统使用的 当前时间: §6{time.strftime('%Y年%m月%d日 %H:%M:%S', time.gmtime(time.time()))}"
        )
        return Builtins.SimpleFmt(
            {
                "[日期]": date_show,
                "[时间]": time_show,
                "[玩家名]": player,
                "[ban原因]": ban_reason or "未知",
            },
            self.cfg[cfg_key],
        )

    @staticmethod
    def rec_ban_data(player: str, data):
        Builtins.SimpleJsonDataReader.writeFileTo("封禁系统", player, data)

    def get_ban_data(self, player: str):
        return Builtins.SimpleJsonDataReader.readFileFrom(
            "封禁系统", player, self.BAN_DATA_DEFAULT
        )
