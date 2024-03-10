import json
import time
from tooldelta import Plugin, plugins, Frame


def find_key_from_value(dic, val):
    # A bad method!
    for k, v in dic.items():
        if v == val:
            return k


plugins.checkSystemVersion((0, 1, 9))


@plugins.add_plugin_as_api("基本插件功能库")
class BasicFunctionLib(Plugin):
    version = (0, 0, 6)
    name = "基本插件功能库"
    author = "SuperScript"
    description = "提供额外的方法用于获取游戏数据"

    def __init__(self, frame: Frame):
        self.frame = frame
        self.game_ctrl = frame.get_game_control()
        self.waitmsg_req = []
        self.waitmsg_result = {}

    def on_player_message(self, player: str, msg: str):
        if player in self.waitmsg_req:
            self.waitmsg_result[player] = msg
            self.waitmsg_req.remove(player)

    def on_player_leave(self, player: str):
        if player in self.waitmsg_req:
            self.waitmsg_result[player] = EXC_PLAYER_LEAVE
            self.waitmsg_req.remove(player)

    # -------------- API ---------------
    def getScore(self, scoreboardNameToGet: str, targetNameToGet: str) -> int:
        "获取玩家计分板分数 (计分板名, 玩家/计分板项名) 获取失败引发异常"
        resultList = self.game_ctrl.sendwscmd(
            f"/scoreboard players list {targetNameToGet}", True
        ).OutputMessages
        result = {}
        result2 = {}
        for i in resultList:
            Message = i.Message
            if Message == r"commands.scoreboard.players.list.player.empty":
                continue
            if Message == r"§a%commands.scoreboard.players.list.player.count":
                targetName = i.Parameters[1][1:]
            elif Message == "commands.scoreboard.players.list.player.entry":
                if targetName == "commands.scoreboard.players.offlinePlayerName":
                    continue
                scoreboardName = i.Parameters[2]
                targetScore = int(i.Parameters[0])
                if targetName not in result:
                    result[targetName] = {}
                result[targetName][scoreboardName] = targetScore
                if scoreboardName not in result2:
                    result2[scoreboardName] = {}
                result2[scoreboardName][targetName] = targetScore
        if not (result or result2):
            raise Exception("Failed to get the score.")
        try:
            if targetNameToGet == "*" or targetNameToGet.startswith("@"):
                if scoreboardNameToGet == "*":
                    return [result, result2]
                return result2[scoreboardNameToGet]
            if scoreboardNameToGet == "*":
                return result[targetNameToGet]
            return result[targetNameToGet][scoreboardNameToGet]
        except KeyError as err:
            raise Exception(f"Failed to get score: {err}")

    def getPos(self, targetNameToGet: str, timeout: float | int = 1) -> dict:
        """
        获取租赁服内玩家坐标的函数
        参数:
            targetNameToGet: str -> 玩家名称
        返回: dict -> 获取结果
        包含了["x"], ["y"], ["z"]: float, ["dimension"](维度): int 和["yRot"]: float
        """
        if (
            (targetNameToGet not in self.game_ctrl.allplayers)
            and (targetNameToGet != self.game_ctrl.bot_name)
            and (not targetNameToGet.startswith("@a"))
        ):
            raise Exception("Player not found.")
        result = self.game_ctrl.sendwscmd(
            "/querytarget " + targetNameToGet, True, timeout
        )
        if result.OutputMessages[0].Success is False:
            raise Exception(
                f"Failed to get the position: {result.OutputMessages[0].Parameters[0]}"
            )
        parameter = result.OutputMessages[0].Parameters[0]
        if isinstance(parameter, str):
            resultList = json.loads(parameter)
        else:
            resultList = parameter
        result = {}
        for i in resultList:
            targetName = find_key_from_value(self.game_ctrl.players_uuid, i["uniqueId"])
            x = (
                i["position"]["x"]
                if i["position"]["x"] >= 0
                else i["position"]["x"] - 1
            )
            y = i["position"]["y"] - 1.6200103759765
            z = (
                i["position"]["z"]
                if i["position"]["z"] >= 0
                else i["position"]["z"] - 1
            )
            position = {
                "x": float(f"{x:.2f}"),
                "y": float(f"{y:.2f}"),
                "z": float(f"{z:.2f}"),
            }
            dimension = i["dimension"]
            yRot = i["yRot"]
            result[targetName] = {
                "dimension": dimension,
                "position": position,
                "yRot": yRot,
            }
        if targetNameToGet == "@a":
            return result
        if len(result) != 1:
            raise Exception("Failed to get the position.")
        if targetNameToGet.startswith("@a"):
            return list(result.values())[0]
        return result[targetNameToGet]

    def getItem(self, targetName: str, itemName: str, itemSpecialID: int = -1) -> int:
        "获取玩家背包内物品数量: 目标选择器, 物品ID, 特殊值 = 所有"
        if (
            (targetName not in self.game_ctrl.allplayers)
            and (targetName != self.game_ctrl.bot_name)
            and (not targetName.startswith("@a"))
        ):
            raise Exception("Player not found.")
        result = self.game_ctrl.sendwscmd(
            f"/clear {targetName} {itemName} {itemSpecialID} 0", True
        )
        if result.OutputMessages[0].Message == "commands.generic.syntax":
            raise Exception("Item name error.")
        if result.OutputMessages[0].Message == "commands.clear.failure.no.items":
            return 0
        return int(result.OutputMessages[0].Parameters[1])

    def getTarget(self, sth: str, timeout: bool | int = 5) -> list:
        "获取符合目标选择器实体的列表"
        if not sth.startswith("@"):
            raise Exception("Minecraft Target Selector is not correct.")
        result = (
            self.game_ctrl.sendwscmd(f"/testfor {sth}", True, timeout)
            .OutputMessages[0]
            .Parameters
        )

        if result:
            result = result[0]
            return result.split(", ")
        return []

    def getBlockTile(self, x: int, y: int, z: int):
        "获取指定坐标的方块的ID"
        res = self.game_ctrl.sendwscmd(f"/testforblock {x} {y} {z} air", True)
        if res.SuccessCount:
            return "air"
        return res.OutputMessages[0].Parameters[4].strip("%tile.").strip(".name")

    def waitMsg(self, who: str, timeout: int = 30, exc=None):
        """
        使用其来等待一个玩家的聊天栏回复, 超时则引发exc给定的异常, 没有给定时超时返回None
        当过程中玩家退出了游戏, 则引发异常(为IOError)
        """
        time.sleep(0.5)
        if who not in self.waitmsg_req:
            self.waitmsg_req.append(who)
        timer = time.time()
        while 1:
            time.sleep(0.2)
            if who in self.waitmsg_result.keys():
                r = self.waitmsg_result[who]
                del self.waitmsg_result[who]
                if r == EXC_PLAYER_LEAVE:
                    raise EXC_PLAYER_LEAVE
                return r
            if time.time() - timer >= timeout:
                try:
                    self.waitmsg_req.remove(who)
                except:
                    pass
                if exc is not None:
                    raise exc
                return None

    def getPosXYZ(self, player, timeout=30) -> tuple[float, float, float]:
        "获取玩家坐标的X, Y, Z值"
        res = self.getPos(player, timeout=timeout)["position"]
        return res["x"], res["y"], res["z"]

    def sendresultcmd(self, cmd, timeout=30):
        "返回命令执行是否成功"
        res = self.game_ctrl.sendwscmd(cmd, True, timeout).SuccessCount
        return bool(res)


EXC_PLAYER_LEAVE = IOError("Player left when waiting msg.")
