from tooldelta import Frame, plugins, Plugin

import time


@plugins.add_plugin
class WorldEdit(Plugin):
    author = "SuperScript"
    version = (0, 0, 2)
    name = "简易建造"
    description = "以更方便的方法在租赁服进行创作, 输入.we help查看说明"

    def __init__(self, frame: Frame):
        self.frame = frame
        self.game_ctrl = frame.get_game_control()

    def on_def(self):
        self.getTarget = plugins.get_plugin_api("基本插件功能库").getTarget
        self.add_trigger = plugins.get_plugin_api("聊天栏菜单").add_trigger
        self.getX = None
        self.getY = None
        self.getZ = None

    def on_inject(self):
        self.add_trigger(["we help"], None, "查看 简易建造插件 的使用说明", self.description_show)

    def description_show(self, who: str, _):
        self.game_ctrl.say_to(
            who,
            "简易建造(需要创造模式)\n §7放置一个告示牌输入 §fWe start§7\n  即可设置起点\n 放置告示牌输入 §fWe fill <方块ID>§7\n  即可将此作为终止点填充方块\n告示牌输入 §fWe cn§7\n  将起始点的方块作为目标方块\n  并使用这个方块填充起始点到此的整个区域",
        )

    @plugins.add_packet_listener(56)
    def we_pkt56(self, jsonPkt: dict):
        if "NBTData" in jsonPkt and "id" in jsonPkt["NBTData"]:
            if (
                jsonPkt["NBTData"]["id"] == "Sign"
                and jsonPkt["NBTData"]["Text"] == "We start"
            ):
                placeX, placeY, placeZ, text = (
                    jsonPkt["NBTData"]["x"],
                    jsonPkt["NBTData"]["y"],
                    jsonPkt["NBTData"]["z"],
                    jsonPkt["NBTData"]["Text"],
                )
                try:
                    signPlayerName = self.getTarget(
                        f"@a[x={placeX}, y={placeY}, z={placeZ}, c=1, r=10]"
                    )[0]
                except Exception as err:
                    signPlayerName = ""
                    self.game_ctrl.say_to("@a", "§cCan't execute because " + str(err))
                self.getX = int(jsonPkt["NBTData"]["x"])
                self.getY = int(jsonPkt["NBTData"]["y"])
                self.getZ = int(jsonPkt["NBTData"]["z"])
                if signPlayerName in self.getTarget("@a[m=1]"):
                    self.game_ctrl.sendcmd(
                        f"/setblock {self.getX} {self.getY} {self.getZ} air 0 destroy"
                    )
                    self.game_ctrl.say_to(
                        signPlayerName,
                        f"§a设置第一点: {self.getX}, {self.getY}, {self.getZ}",
                    )

            elif (
                jsonPkt["NBTData"]["id"] == "Sign"
                and jsonPkt["NBTData"]["Text"].startswith("We fill ")
                and len(jsonPkt["NBTData"]["Text"]) > 8
            ):
                placeX, placeY, placeZ, text = (
                    jsonPkt["NBTData"]["x"],
                    jsonPkt["NBTData"]["y"],
                    jsonPkt["NBTData"]["z"],
                    jsonPkt["NBTData"]["Text"],
                )
                try:
                    signPlayerName = self.getTarget(
                        f"@a[x={placeX}, y={placeY}, z={placeZ}, c=1, r=10]"
                    )[0]
                    getXend = int(jsonPkt["NBTData"]["x"])
                    getYend = int(jsonPkt["NBTData"]["y"])
                    getZend = int(jsonPkt["NBTData"]["z"])
                except Exception as err:
                    signPlayerName = ""
                    self.game_ctrl.say_to("@a", "§4ERROR：目标选择器报错 §c " + int(err))
                blockData = text[8:].replace("陶瓦", "stained_hardened_clay")
                try:
                    if signPlayerName in self.getTarget("@a[m=1]"):
                        if not self.getX:
                            raise AssertionError
                        self.game_ctrl.sendcmd(
                            f"/fill {self.getX} {self.getY} {self.getZ} {getXend} {getYend} {getZend} {blockData}"
                        )
                        self.game_ctrl.say_to(
                            signPlayerName, "§c§lWorldEdit§r>> §a填充完成"
                        )
                    else:
                        self.game_ctrl.say_to(
                            signPlayerName, "§c§lWorldEdit§r>> §c没有权限"
                        )
                except AssertionError:
                    self.game_ctrl.say_to(
                        signPlayerName, "§c§lWorldEdit§r>> §c没有设置起点或终点"
                    )
            elif (
                jsonPkt["NBTData"]["id"] == "Sign"
                and jsonPkt["NBTData"]["Text"] == "We cn"
            ):
                try:
                    if not self.getX:
                        raise AssertionError
                    signPlayerName = self.getTarget(
                        f"@a[x={jsonPkt['NBTData']['x']}, y={jsonPkt['NBTData']['y']}, z={jsonPkt['NBTData']['z']}, c=1, r=10]"
                    )[0]
                    if signPlayerName in self.getTarget("@a[m=1]"):
                        self.frame.createThread(
                            self.fillwith,
                            (
                                self.getX,
                                self.getY,
                                self.getZ,
                                int(jsonPkt["NBTData"]["x"]),
                                int(jsonPkt["NBTData"]["y"]),
                                int(jsonPkt["NBTData"]["z"]),
                            ),
                        )
                except Exception as err:
                    self.game_ctrl.say_to("@a", "§cCan't execute because " + str(err))

    def fillwith(self, sx, sy, sz, dx, dy, dz):
        p2n = lambda n: 1 if n >= 0 else -1
        fx = p2n(dx - sx)
        fy = p2n(dy - sy)
        fz = p2n(dz - sz)
        for x in range(sx, dx + fx, fx):
            for y in range(sy, dy + fy, fy):
                for z in range(sz, dz + fz, fz):
                    self.game_ctrl.sendwocmd(
                        f"/clone {sx} {sy} {sz} {sx} {sy} {sz} {x} {y} {z}"
                    )
                    time.sleep(0.01)
