addPluginAPI: type
PluginAPI: type

import json

@addPluginAPI("dotcs_basic", (0, 0, 1))
class DotCSLib(PluginAPI):
    def __init__(this, frame):
        this.frame = frame
        this.game_ctrl = frame.get_game_control()

    def getScore(this, scoreboardNameToGet: str, targetNameToGet: str) -> int:
        """
        获取租赁服内对应计分板数值的函数
        参数:
            scoreboardName: str -> 计分板名称
            targetName: str -> 计分板对象名称
        返回: int -> 获取结果
        """
        resultList = this.game_ctrl.sendcmd("/scoreboard players list %s" % targetNameToGet, True).OutputMessages
        result = {}
        result2 = {}
        for i in resultList:
            Message = i.Message
            if Message == r"commands.scoreboard.players.list.player.empty":
                continue
            elif Message == r"§a%commands.scoreboard.players.list.player.count":
                targetName = i["Parameters"][1][1:]
            elif Message == "commands.scoreboard.players.list.player.entry":
                if targetName == "commands.scoreboard.players.offlinePlayerName":
                    continue
                scoreboardName = i["Parameters"][2]
                targetScore = int(i["Parameters"][0])
                if targetName not in result:
                    result[targetName] = {}
                result[targetName][scoreboardName] = targetScore
                if scoreboardName not in result2:
                    result2[scoreboardName] = {}
                result2[scoreboardName][targetName] = targetScore
        if not(result or result2):
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
        
    def getPos(this, targetNameToGet: str, timeout: float | int = 1) -> dict:
        """
        获取租赁服内玩家坐标的函数
        参数:
            targetNameToGet: str -> 玩家名称
        返回: dict -> 获取结果
        """
        if (targetNameToGet not in this.game_ctrl.allplayers) and (targetNameToGet != this.game_ctrl.bot_name) and (not targetNameToGet.startswith("@a")):
            raise Exception("Player not found.")
        result = this.game_ctrl.sendcmd("/querytarget %s" % targetNameToGet, True, timeout).OutputMessages[0]
        if result.Success == False:
            raise Exception("Failed to get the position.")
        resultList = json.loads(result.Parameters[0])
        result = {}
        for i in resultList:
            targetName = this.game_ctrl.players_uuid[i["uniqueId"][-8:]]
            x = i["position"]["x"]
            y = i["position"]["y"] - 1.6200103759765
            z = i["position"]["z"]
            position = {"x": float("%.2f" % x), "y": float("%.2f" % y), "z": float("%.2f" % z)}
            dimension = i["dimension"]
            yRot = i["yRot"]
            result[targetName] = {"dimension": dimension, "position": position, "yRot": yRot}
        if targetNameToGet == "@a":
            return result
        else:
            if len(result) != 1:
                raise Exception("Failed to get the position.")
            if targetNameToGet.startswith("@a"):
                return list(result.values())[0]
            else:
                return result[targetNameToGet]
            
    def getTarget(this, sth: str, timeout: bool | int = 5) -> list:
        if not sth.startswith("@"):
            raise Exception("Minecraft Target Selector is not correct.")
        result = this.game_ctrl.sendcmd("/testfor %s" % sth, True, timeout).OutputMessages[0].Parameters[0]
        return result.split(", ")