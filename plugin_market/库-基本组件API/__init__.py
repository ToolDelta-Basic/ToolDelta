import json
import time
from tooldelta import Plugin, PluginAPI, plugins, Frame


def find_key_from_value(dic, val):
    # A bad method!
    for k, v in dic.items():
        if v == val:
            return k


plugins.checkSystemVersion((0, 1, 8))


@plugins.add_plugin_api("基本插件功能库")
class BasicFunctionLib(PluginAPI):
    version = (0, 0, 3)

    def __init__(self, frame: Frame):
        self.frame = frame
        self.game_ctrl = frame.get_game_control()
        frame

    # -------------- API ---------------
    def getScore(self, scoreboardNameToGet: str, targetNameToGet: str) -> int:
        "获取玩家计分板分数 (计分板名, 玩家/计分板项名) 获取失败引发异常"
        resultList = self.game_ctrl.sendwscmd(
            "/scoreboard players list %s" % targetNameToGet, True
        ).OutputMessages
        result = {}
        result2 = {}
        for i in resultList:
            Message = i.Message
            if Message == r"commands.scoreboard.players.list.player.empty":
                continue
            elif Message == r"§a%commands.scoreboard.players.list.player.count":
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
                else:
                    return result2[scoreboardNameToGet]
            else:
                if scoreboardNameToGet == "*":
                    return result[targetNameToGet]
                else:
                    return result[targetNameToGet][scoreboardNameToGet]
        except KeyError as err:
            raise Exception("Failed to get score: %s" % str(err))

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
        if result.OutputMessages[0].Success == False:
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
                "x": float("%.2f" % x),
                "y": float("%.2f" % y),
                "z": float("%.2f" % z),
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
        else:
            if len(result) != 1:
                raise Exception("Failed to get the position.")
            if targetNameToGet.startswith("@a"):
                return list(result.values())[0]
            else:
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
            "/clear %s %s %d 0" % (targetName, itemName, itemSpecialID), True
        )
        if result.OutputMessages[0].Message == "commands.generic.syntax":
            raise Exception("Item name error.")
        if result.OutputMessages[0].Message == "commands.clear.failure.no.items":
            return 0
        else:
            return int(result.OutputMessages[0].Parameters[1])

    def getTarget(self, sth: str, timeout: bool | int = 5) -> list:
        "获取符合目标选择器实体的列表"
        if not sth.startswith("@"):
            raise Exception("Minecraft Target Selector is not correct.")
        result = (
            self.game_ctrl.sendwscmd("/testfor %s" % sth, True, timeout)
            .OutputMessages[0]
            .Parameters
        )
        if result:
            result = result[0]
            return result.split(", ")
        else:
            return []

    def getBlockTile(self, x: int, y: int, z: int):
        "获取指定坐标的方块的ID"
        res = self.game_ctrl.sendwscmd(f"/testforblock {x} {y} {z} air", True)
        if res.SuccessCount:
            return "air"
        else:
            return res.OutputMessages[0].Parameters[4].strip("%tile.").strip(".name")

    @staticmethod
    def waitMsg(who: str, timeout: int = 30, exc=None):
        active_basic_api: ActivatePluginAPI = active_basic_apis[0]
        """
        使用其来等待一个玩家的聊天栏回复, 超时则引发exc给定的异常, 没有给定时超时返回None
        当过程中玩家退出了游戏, 则引发异常(为IOError)
        """
        time.sleep(0.5)
        if who not in active_basic_api.waitmsg_req:
            active_basic_api.waitmsg_req.append(who)
        timer = time.time()
        while 1:
            time.sleep(0.2)
            if who in active_basic_api.waitmsg_result.keys():
                r = active_basic_api.waitmsg_result[who]
                del active_basic_api.waitmsg_result[who]
                if r == EXC_PLAYER_LEAVE:
                    raise EXC_PLAYER_LEAVE
                return r
            elif time.time() - timer >= timeout:
                try:
                    active_basic_api.waitmsg_req.remove(who)
                except:
                    pass
                if exc is not None:
                    raise exc
                else:
                    return None

    def getPosXYZ(self, player, timeout=30) -> tuple[float, float, float]:
        "获取玩家坐标的X, Y, Z值"
        res = self.getPos(player, timeout=timeout)["position"]
        return res["x"], res["y"], res["z"]

    def sendresultcmd(self, cmd, timeout=30):
        "返回命令执行是否成功"
        res = self.game_ctrl.sendwscmd(cmd, True, timeout).SuccessCount
        return bool(res)


active_basic_apis: list = []

EXC_PLAYER_LEAVE = IOError("Player left when waiting msg.")


@plugins.add_plugin
class ActivatePluginAPI(Plugin):
    name = "基本组件API"
    author = "System"
    version = (0, 0, 1)

    def __init__(self, frame: Frame):
        self.game_ctrl = frame.get_game_control()
        self.waitmsg_req = []
        self.waitmsg_result = {}
        active_basic_apis.append(self)

    def on_player_message(self, player: str, msg: str):
        if player in self.waitmsg_req:
            self.waitmsg_result[player] = msg
            self.waitmsg_req.remove(player)

    def on_player_leave(self, player: str):
        if player in self.waitmsg_req:
            self.waitmsg_result[player] = EXC_PLAYER_LEAVE
            self.waitmsg_req.remove(player)
