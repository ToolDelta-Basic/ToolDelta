import os
import json
import threading
import ctypes
import traceback

def get_dotcs_env(__F, print_ins):
    # 为旧版 DotCS 插件提供原生环境
    sendcmd = lambda cmd, waitForResp=False, timeout=30: (
        __F.link_game_ctrl.sendcmd(cmd, waitForResp, timeout).as_dict
        if waitForResp
        else __F.link_game_ctrl.sendcmd(cmd)
    )
    sendwocmd = __F.link_game_ctrl.sendwocmd
    sendwscmd = lambda cmd, waitForResp=False, timeout=30: (
        __F.link_game_ctrl.sendwscmd(cmd, waitForResp, timeout).as_dict
        if waitForResp
        else __F.link_game_ctrl.sendwscmd(cmd)
    )
    sendfbcmd = __F.link_game_ctrl.sendfbcmd
    allplayers = __F.link_game_ctrl.allplayers
    robotname = __F.link_game_ctrl.bot_name
    XUID2playerName = __F.link_game_ctrl.players_uuid
    threadList = __F.old_dotcs_threadinglist
    admin = adminhigh = [robotname]
    tellrawText = lambda target, dispname=None, text="": __F.link_game_ctrl.say_to(
        target, dispname + " " + text if dispname else text
    )
    exiting = False
    server = hash(__F.serverNumber)

    def color(
        text: str,
        output: bool = True,
        end: str = "\n",
        replace: bool = False,
        replaceByNext: bool = False,
        info=" 信息 ",
    ):
        if not output:
            return print_ins.fmt_info(text, info)
        if not replace:
            print_ins.print_with_info(text, info, end=end)
        else:
            print_ins.print_with_info(text, info, end="\r")

    class createThread(threading.Thread):
        def __init__(self, name, data=None, func="", output=True):
            if data is None:
                data = {}
            threading.Thread.__init__(self)
            self.name = name
            self.data = data
            self.func = func
            self.stopping = False
            self.daemon = True
            self.output = output
            threadList.append(self)
            self.start()

        def run(self):
            try:
                if self.func.__class__.__name__ != "str":
                    self.func(self)
                else:
                    exec(f"{self.func}(self)")
            except Exception as err:
                traceback.print_exc()
            except SystemExit as err:
                pass
            finally:
                threadList.remove(self)

        def get_id(self):
            if hasattr(self, "_thread_id"):
                return self._thread_id
            for thread_id, thread in enumerate(threading.enumerate()):
                if thread is self:
                    return thread_id

        def stop(self):
            self.stopping = True
            thread_id = self.get_id()
            res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
                thread_id, ctypes.py_object(SystemExit)
            )
            if res > 1:
                ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)

    def getTarget(sth: str, timeout: bool | int = 1) -> list:
        if not sth.startswith("@"):
            raise Exception("Minecraft Target Selector is not correct.")
        result = sendcmd(f"/tell @s get{sth}", True, timeout)["OutputMessages"][0][
            "Parameters"
        ][1][3:]
        if ", " not in result:
            if not result:
                return []
            return [result]
        return result.split(", ")

    def getScore(scoreboardNameToGet: str, targetNameToGet: str) -> int:
        resultList = sendcmd(f"/scoreboard players list {targetNameToGet}", True)["OutputMessages"]
        result = {}
        result2 = {}
        for i in resultList:
            Message = i["Message"]
            if Message == r"commands.scoreboard.players.list.player.empty":
                continue
            if Message == r"§a%commands.scoreboard.players.list.player.count":
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
            raise Exception(f"Failed to get score: {str(err)}")

    def getPos(targetNameToGet: str, timeout: float | int = 1) -> dict:
        if (
            (targetNameToGet not in allplayers)
            and (targetNameToGet != robotname)
            and (not targetNameToGet.startswith("@a"))
        ):
            raise Exception("Player not found.")
        result = sendcmd(f"/querytarget {targetNameToGet}", True, timeout)["OutputMessages"][0]
        if result["Success"] is False:
            raise Exception("Failed to get the position.")
        resultList = json.loads(result["Parameters"][0])
        result = {}
        for i in resultList:
            targetName = XUID2playerName[i["uniqueId"][-8:]]
            x = i["position"]["x"]
            y = i["position"]["y"] - 1.6200103759765
            z = i["position"]["z"]
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

    def getItem(targetName: str, itemName: str, itemSpecialID: int = -1) -> int:
        if (
            (targetName not in allplayers)
            and (targetName != robotname)
            and (not targetName.startswith("@a"))
        ):
            raise Exception("Player not found.")
        result = sendcmd(f"/clear {targetName} {itemName} {itemSpecialID} 0", True)
        if result["OutputMessages"][0]["Message"] == "commands.generic.syntax":
            raise Exception("Item name error.")
        if result["OutputMessages"][0]["Message"] == "commands.clear.failure.no.items":
            return 0
        return int(result["OutputMessages"][0]["Parameters"][1])

    def getStatus(statusName: str):
        if not os.path.isfile(f"插件数据文件/{statusName}.txt"):
            return None
        with open(f"插件数据文件/{statusName}.txt", "r", encoding="utf-8") as file:
            status = file.read()
        return status

    def setStatus(statusName: str, status):
        with open(f"插件数据文件/{statusName}.txt", "w", encoding="utf-8") as file:
            file.write(str(status))

    def getPlayerData(dataName: str, playerName: str, writeNew):
        try:
            with open(
                f"插件数据文件/players/{playerName}.json", "r", encoding="utf-8"
            ) as f:  # skipcq: PTC-W6004
                j = json.load(f)[dataName]
            return j
        except KeyError:
            with open(f"插件数据文件/players/{playerName}.json", "r", encoding="utf-8") as f:
                j = json.load(f)
            j[dataName] = writeNew
            with open(f"插件数据文件/players/{playerName}.json", "w", encoding="utf-8") as f:
                json.dump(j, f)
        except FileNotFoundError:
            with open(f"插件数据文件/players/{playerName}.json", "w", encoding="utf-8") as f:
                json.dump({dataName: writeNew}, f)
        return None

    def setPlayerData(dataName: str, playerName: str, dataValue, writeNew: str = ""):
        if os.path.isfile(f"插件数据文件/players/{playerName}.json"):
            with open(f"插件数据文件/players/{playerName}.json", "r", encoding="utf-8") as f:
                j = json.load(f)
            j[dataName] = dataValue
            with open(f"插件数据文件/players/{playerName}.json", "w", encoding="utf-8") as f:
                json.dump(j, f)
        else:
            with open(f"插件数据文件/players/{playerName}.json", "w", encoding="utf-8") as f:
                json.dump({dataName: dataValue}, f)

    return locals()
