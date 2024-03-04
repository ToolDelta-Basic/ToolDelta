from email.mime import base
from tooldelta import Plugin, plugins, Print
from tooldelta.frame import Frame

from PIL import Image
import time


@plugins.add_plugin
class MapArtImporter(Plugin):
    name = "地图画导入"
    version = (0, 0, 3)
    author = "SuperScript"
    description = "导入图片到租赁服"

    def __init__(self, frame: Frame):
        self.color_cache = {}
        self.color_mapping = {}
        self.default_block = "concrete"
        self.frame = frame
        self.game_ctrl = frame.get_game_control()

    def on_inject(self):
        self.menu = plugins.get_plugin_api("聊天栏菜单", (0, 0, 1))
        self.menu.add_trigger(
            ["像素画"],
            "导入像素画",
            "<文件名> <x坐标> <y坐标> <z坐标>, <尺寸(默认为1x1, 格式: ?x?)>",
            lambda player, args: self.frame.ClassicThread(
                self.menu_imp, (player, args)
            ),
        )

    def get_nearest_color_block(self, rvalue, gvalue, bvalue):
        if self.color_cache.get((rvalue, gvalue, bvalue)):
            return self.color_cache.get((rvalue, gvalue, bvalue))
        max_weight_reversed = 10000000
        max_matches = (0, 0, 0)
        for i, item in enumerate(color_map):
            _, (r, g, b) = item
            weight = (r - rvalue) ** 2 + (g - gvalue) ** 2 + (b - bvalue) ** 2
            if weight < max_weight_reversed:
                max_matches = item[0]
                max_weight_reversed = weight
        self.color_cache[(rvalue, gvalue, bvalue)] = max_matches
        return max_matches

    def imp_map(
        self,
        bmap_path: str,
        size: tuple[int, int],
        baseXP: int,
        baseYP: int,
        baseZP: int,
        owner: str,
    ):
        self.game_ctrl.say_to(owner, "§7读取并分析图片...")
        img = Image.open(bmap_path).convert("RGB").resize(size)
        xsize, ysize = size
        scmd = self.game_ctrl.sendwocmd
        self.game_ctrl.say_to(owner, "§7开始导入像素画...")
        TOTAL = xsize * ysize
        BPS = 800
        progress = 0
        sname = self.game_ctrl.bot_name
        if not sname:
            raise ValueError("未找到机器人名")
        # /w @s .像素画 a1.png 10048 154 10048 3x2
        # /w @s .像素画 a1.jpg 10048 154 10048 2x2
        zchunk = 0
        for xchunk in range(xsize // 16):
            cmdd = f"/tp {sname} {baseXP + xchunk * 16 + 8} {baseYP + 10} {baseZP + 8}"
            scmd(cmdd)
            time.sleep(0.5)
            for zchunk in range(ysize // 16):
                re_xpos = baseXP + xchunk * 16
                re_zpos = baseZP + zchunk * 16
                progress += 256
                nowprogresspcent = int(progress / TOTAL * 100)
                _prgs = int(progress / TOTAL * 20)
                nowprogresstext = Print.colormode_replace(
                    "§e" + " " * _prgs + "§c" + " " * (20 - _prgs) + "§r", 7
                )
                Print.print_with_info(
                    f"§b像素画导入进度:  {nowprogresstext}   §a{nowprogresspcent}% {progress}/{TOTAL}",
                    end="\r",
                )
                cmdd = f"/tp {sname} {re_xpos + 8} {baseYP + 10} {re_zpos + 8}"
                scmd(cmdd)
                for limx in range(16):
                    time.sleep(16 / BPS)
                    for limz in range(16):
                        image_pixel_x = re_xpos + limx - baseXP
                        image_pixel_y = re_zpos + limz - baseZP
                        rget, gget, bget = img.getpixel((image_pixel_x, image_pixel_y))
                        neBlock, neBlock_spec = self.get_nearest_color_block(
                            rget, gget, bget
                        )
                        if (
                            neBlock == "light_weighted_pressure_plate"
                            and neBlock_spec == 7
                        ):
                            scmd(
                                f"/setblock {re_xpos + limx} {baseYP} {re_zpos + limz} sponge 0"
                            )
                            baseYP += 1
                            scmd(
                                f"/setblock {re_xpos + limx} {baseYP} {re_zpos + limz} {neBlock} {neBlock_spec}"
                            )
                            baseYP -= 1
                            continue
                        scmd(
                            f"/setblock {re_xpos + limx} {baseYP} {re_zpos + limz} {neBlock} {neBlock_spec}"
                        )
        Print.print_suc("像素画导入成功")
        self.color_cache.clear()

    def menu_imp(self, player, args):
        if len(args) not in (4, 5):
            self.game_ctrl.say_to(player, "§c参数数量错误")
            return
        if len(args) == 4:
            (file, xp, yp, zp), size = args, (128, 128)
        elif len(args) == 5:
            file, xp, yp, zp, size = args
            try:
                size = size.split("x")
                sizex, sizey = int(size[0]) * 128, int(size[1]) * 128
                if not (sizex > 0 and sizey > 0):
                    raise AssertionError
                size = (sizex, sizey)
            except:
                self.game_ctrl.say_to(player, "§c地图画尺寸格式应该像这样: 1x2")
                return
        try:
            self.imp_map(file, size, int(xp), int(yp), int(zp), player)
        except Exception as err:
            self.game_ctrl.say_to(player, f"§c出现问题: {err}")


color_map = [
    [["stone", 0], [89, 89, 89]],
    [["stone", 1], [135, 102, 76]],
    [["stone", 3], [237, 235, 229]],
    [["stone", 5], [104, 104, 104]],
    [["grass", 0], [144, 174, 94]],
    [["planks", 0], [129, 112, 73]],
    [["planks", 1], [114, 81, 51]],
    [["planks", 2], [228, 217, 159]],
    [["planks", 4], [71, 71, 71]],
    [["planks", 5], [91, 72, 50]],
    [["leaves", 0], [64, 85, 32]],
    [["leaves", 1], [54, 75, 50]],
    [["leaves", 2], [68, 83, 47]],
    [["leaves", 14], [58, 71, 40]],
    [["leaves", 15], [55, 73, 28]],
    [["sponge", 0], [183, 183, 70]],
    [["lapis_block", 0], [69, 101, 198]],
    [["noteblock", 0], [111, 95, 63]],
    [["web", 0], [159, 159, 159]],
    [["wool", 0], [205, 205, 205]],
    [["wool", 1], [163, 104, 54]],
    [["wool", 2], [132, 65, 167]],
    [["wool", 3], [91, 122, 169]],
    [["wool", 5], [115, 162, 53]],
    [["wool", 6], [182, 106, 131]],
    [["wool", 7], [60, 60, 60]],
    [["wool", 8], [123, 123, 123]],
    [["wool", 9], [69, 100, 121]],
    [["wool", 10], [94, 52, 137]],
    [["wool", 11], [45, 59, 137]],
    [["wool", 12], [78, 61, 43]],
    [["wool", 13], [85, 100, 49]],
    [["wool", 14], [113, 46, 44]],
    [["wool", 15], [20, 20, 20]],
    [["gold_block", 0], [198, 191, 84]],
    [["iron_block", 0], [134, 134, 134]],
    [["double_stone_slab", 1], [196, 187, 136]],
    [["double_stone_slab", 6], [204, 202, 196]],
    [["double_stone_slab", 7], [81, 11, 5]],
    [["tnt", 0], [188, 39, 26]],
    [["mossy_cobblestone", 0], [131, 134, 146]],
    [["diamond_block", 0], [102, 173, 169]],
    [["farmland", 0], [116, 88, 65]],
    [["ice", 0], [149, 149, 231]],
    [["pumpkin", 1], [189, 122, 62]],
    [["monster_egg", 1], [153, 156, 169]],
    [["red_mushroom_block", 0], [131, 53, 50]],
    [["vine", 1], [68, 89, 34]],
    [["brewing_stand", 6], [155, 155, 155]],
    [["double_wooden_slab", 1], [98, 70, 44]],
    [["emerald_block", 0], [77, 171, 67]],
    [["light_weighted_pressure_plate", 7], [231, 221, 99]],
    [["stained_hardened_clay", 0], [237, 237, 237]],
    [["stained_hardened_clay", 2], [154, 76, 194]],
    [["stained_hardened_clay", 4], [213, 213, 82]],
    [["stained_hardened_clay", 6], [211, 123, 153]],
    [["stained_hardened_clay", 8], [142, 142, 142]],
    [["stained_hardened_clay", 10], [110, 62, 160]],
    [["slime", 0], [109, 141, 60]],
    [["packed_ice", 0], [128, 128, 199]],
    [["repeating_command_block", 1], [77, 43, 112]],
    [["chain_command_block", 1], [70, 82, 40]],
    [["nether_wart_block", 0], [93, 38, 36]],
    [["bone_block", 0], [160, 153, 112]],
]
