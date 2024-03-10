from tooldelta.plugin_load.injected_plugin import player_message, repeat
from tooldelta.plugin_load.injected_plugin.movent import (
    sendcmd,
    rawText,
    get_all_player,
    tellrawText,
)

__plugin_meta__ = {
    "name": "tpa传送",
    "version": "0.0.3",
    "author": "wling",
}

display = "§a§l传送系统 §7>>> §r"


tpaRequests = []


class tpa:
    def __init__(self, playersend, playerrecv, time):
        self.playersend = playersend
        self.playerrecv = playerrecv
        self.time = time
        self.start()

    def start(self):
        rawText(
            self.playersend,
            display
            + "已向玩家 §l%s§r 发起传送请求, 对方有 §l%d§r 秒的时间接受请求."
            % (self.playerrecv, self.time),
        )
        rawText(
            self.playerrecv,
            display
            + "收到 §l%s§r 发来的传送请求, 你有 §l%d§r 秒的时间接受请求."
            % (self.playersend, self.time),
        )
        tpaRequests.append(self)
        rawText(
            self.playerrecv,
            display
            + "输入§c.tpa acc §r接受对方请求, 将对方传来\n输入§c.tpa dec §r拒绝对方请求",
        )

    def accept(self):
        sendcmd(f"/tp {self.playersend} {self.playerrecv}")
        rawText(
            self.playersend,
            display + f"§l{self.playerrecv}§r 已接受你的传送请求.",
        )

        rawText(
            self.playerrecv,
            display + f"你已接受 §l{self.playersend}§r 的传送请求.",
        )

        tpaRequests.remove(self)

    def decline(self):
        rawText(
            self.playersend,
            display + f"§c§l{self.playerrecv}§r§c 已拒绝你的传送请求.",
        )

        rawText(
            self.playerrecv,
            display + f"§c你已拒绝 §l{self.playersend}§r§c 的传送请求.",
        )

        tpaRequests.remove(self)

    def outdate(self):
        rawText(
            self.playersend,
            display + f"§c你发给 §l{self.playerrecv}§r§c 的传送请求已过期.",
        )

        rawText(
            self.playerrecv,
            display + f"§c§l{self.playersend}§r§c 发来的传送请求已过期.",
        )

        tpaRequests.remove(self)


@player_message()
async def tpaCommand(playername, msg):
    if msg.startswith(".tpa"):
        if msg == ".tpa":
            rawText(
                playername,
                display
                + "\n玩家互传(选人版)  帮助菜单\n输入§c.tpa list §r查询目前的玩家传送请求\n输入§c.tpa <玩家名称> §r向对方发起传送请求\n输入§c.tpa acc §r接受对方请求, 将对方传来\n输入§c.tpa dec §r拒绝对方请求",
            )
            return
        arg = msg.split(" ")[1]
        if arg == "list":
            if len(tpaRequests) == 0:
                rawText(playername, display + "暂无请求.")
            else:
                tpaIndex = 1
                for i in tpaRequests:
                    rawText(
                        playername,
                        display
                        + "请求§l§c%d§r: §l%s§r 发送给 §l%s§r, 剩余时间: §l%d§r s"
                        % (tpaIndex, i.playersend, i.playerrecv, i.time),
                    )
                    tpaIndex += 1
        elif arg == "acc":
            tpaBeRequested = False
            for i in tpaRequests:
                if playername == i.playerrecv:
                    tpaBeRequested = True
                    i.accept()
                    break
            if not (tpaBeRequested):
                tellrawText(playername, "§l§4ERROR§r", "§c你没有待处理的请求.")
        elif arg == "dec":
            tpaBeRequested = False
            for i in tpaRequests:
                if playername == i.playerrecv:
                    tpaBeRequested = True
                    i.decline()
                    break
            if not (tpaBeRequested):
                tellrawText(playername, "§l§4ERROR§r", "§c你没有待处理的请求.")
        else:
            playerTpaFound = []
            playerTpaToSearch = arg
            for i in get_all_player():
                if playerTpaToSearch == i:
                    playerTpaFound = [i]
                    break
                elif playerTpaToSearch in i:
                    playerTpaFound.append(i)
            print(playerTpaFound)
            if len(playerTpaFound) == 0:
                tellrawText(
                    playername,
                    "§l§4ERROR§r",
                    "§c未找到名称包含 §l%s§r§c 的玩家, 无法发起请求."
                    % playerTpaToSearch,
                )
            elif len(playerTpaFound) >= 2:
                tellrawText(
                    playername,
                    "§l§4ERROR§r",
                    "§c有多名玩家名称包含 §l%s§r§c, 无法发起请求:" % playerTpaToSearch,
                )
                playerTpaFoundIndex = 1
                for i in playerTpaFound:
                    tellrawText(
                        playername,
                        "§l§4ERROR§r",
                        "§l§c%d§r§c. §l%s§r§c" % (playerTpaFoundIndex, i),
                    )
                    playerTpaFoundIndex += 1
            else:
                tpaSentRequest = False
                tpaRecvedRequest = False
                for i in tpaRequests:
                    if playername == i.playersend:
                        tpaSentRequest = True
                    if playerTpaFound[0] == i.playerrecv:
                        tpaRecvedRequest = True
                if tpaSentRequest:
                    tellrawText(
                        playername,
                        "§l§4ERROR§r",
                        "§c你已发过请求, 请等对方处理后或等请求过期后再试.",
                    )
                elif tpaRecvedRequest:
                    tellrawText(
                        playername,
                        "§l§4ERROR§r",
                        "§c对方有未处理的请求, 请等对方处理后或等请求过期后再试.",
                    )
                else:
                    tpa(playername, playerTpaFound[0], 60)


@repeat(1)
async def tpaTimeCount():
    for i in tpaRequests:
        i.time -= 1
        if i.time <= 0:
            i.outdate()
