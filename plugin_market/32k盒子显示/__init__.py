from tooldelta import plugins, Frame, Plugin, Print
import time


@plugins.add_plugin
class Display32KShulkerBox(Plugin):
    name = "32k盒子显示"
    description = "检测32k盒子并反制"
    author = "SuperScript"
    version = (0, 0, 2)

    def __init__(self, f: Frame):
        self.game_ctrl = f.get_game_control()

    def on_def(self):
        self.bas_api = plugins.get_plugin_api("基本插件功能库")
        self.chatbar = plugins.get_plugin_api("聊天栏菜单")
        self.ban_sys = plugins.get_plugin_api("封禁系统")

    def on_inject(self):
        self.chatbar.add_trigger(
            [".32kboxes", ".32k盒"],
            None,
            "查看最近产生的32k潜影盒",
            self.on_menu,
            lambda _: True,
            True,
        )

    @plugins.add_packet_listener(56)
    def box_get(self, jsonPkt):
        if "Items" in jsonPkt["NBTData"]:
            shulkerBoxPos = f"{jsonPkt['Position'][0]} {jsonPkt['Position'][1]} {jsonPkt['Position'][2]}"
            shulkerx, shulkery, shulkerz = jsonPkt["Position"][0:3]
            shulkerBoxItemList = jsonPkt["NBTData"]["Items"]
            ench32kName = []
            for i in shulkerBoxItemList:
                enchItemName = i["Name"]
                if "tag" in i:
                    if "ench" in i["tag"]:
                        for j in i["tag"]["ench"]:
                            if j["lvl"] > 10:
                                ench32kName.append(enchItemName)
            if ench32kName:
                structID = "b" + hex(round(time.time())).replace("0x", "")
                try:
                    playerNearest = self.bas_api.getTarget(
                        f"@a[x={shulkerx},y={shulkery},z={shulkerz},name=!{self.game_ctrl.bot_name},c=1]"
                    )[0]
                except:
                    playerNearest = "未找到"
                self.game_ctrl.sendcmd(
                    f"/structure save {structID} {shulkerBoxPos} {shulkerBoxPos} disk"
                )
                self.game_ctrl.sendcmd(f"/setblock {shulkerBoxPos} bedrock")
                self.game_ctrl.say_to(
                    "@a",
                    text=f"§4警报 §c发现坐标§e({shulkerBoxPos.replace(' ', ',')})§c的32k潜影盒，已自动保存并清除，最近玩家：{playerNearest}，结构方块结构名：",
                )
                self.game_ctrl.sendcmd(f"/tag {playerNearest} add ban")
                self.game_ctrl.say_to(
                    "@a[m=1]", text="§6" + structID + "§6，给予玩家的标签是ban"
                )
                self.ban_sys.ban(playerNearest, time.time() + 1000000000, "使用 32k 潜影盒")
                Print.print_war(
                    f"!!! 发现含32k的潜影盒, 坐标: {shulkerBoxPos}, 结构id: {structID}"
                )
                self.write32kBox(structID)

    def on_menu(self, player: str, _):
        boxes = self.getAll32kBoxes()
        if boxes.strip():
            for i in boxes:
                self.game_ctrl.sendcmd(
                    f"/execute {player} ~~~ structure load {i} ~~~"
                )
                self.game_ctrl.sendcmd(
                    f"/execute {player} ~~~ setblock ~~~ air 0 destroy"
                )
                self.game_ctrl.sendcmd("/structure delete " + i)
                time.sleep(0.05)
            self.game_ctrl.say_to(player, "§6检查完成.")
        else:
            self.game_ctrl.say_to(player, "§c没有检测到最近产生的32k潜影盒.")

    @staticmethod
    def getAll32kBoxes() -> str:
        try:
            with open("data/32kBoxes.txt", "r", encoding="utf-8") as f:
                boxes = f.read().split("\n")
                f.close()
            return boxes
        except FileNotFoundError:
            return ""

    @staticmethod
    def write32kBox(structID):
        with open("data/32kBoxes.txt", "a", encoding="utf-8") as f:
            f.write("\n" + structID)
            f.close()
