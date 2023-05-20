# DotCS Lite

import os, time, traceback, socket, datetime, json, random, sys, urllib, urllib.parse, platform, sqlite3, threading, struct, hashlib, shutil, base64, ctypes, collections, types, itertools, _thread as thread
from typing import Union, List, Dict, Tuple, Set, TypeVar
# pip 可下载到的库.
# pip freeze>modules.txt
# pip uninstall -r modules.txt -y
# pip install psutil requests pymysql qrcode websocket-client brotli pillow rich numpy pyinstaller==4.9 mido pycryptodome
import psutil, requests, pymysql, qrcode, websocket, brotli, PIL, rich.console, Crypto.Cipher.DES3
# 加载开发者们的自制库.
import bdx_work_shop.canvas
import bdx_work_shop.artists.cmd_midi_music
from proxy import conn
from PyPI import TDES
from PyPI import getVarSize
from PyPI.SpaceRectangularCoordinateSystem import Point, Cube
from PyPI.LiteColor import Color
from PyPI.itemNetworkList import itemNetworkList


threadList = []
exiting = False
exitDelay = 3
exitReason = None
connected = False

class _root_Set():
    DefColor = True
    _Console = rich.console.Console()
    fbname = "phoenixbuilder.exe"
    debug = False
    _root_debug = False
    _needOmega = False
    defaultPosX, defaultPosY, defaultPosZ = (100000, 100000, 100000)
            
_root = _root_Set()

try:

    """""""""
    DEF PART
    """""""""
    
    _use_zh = True
    lastReplace = False
    lastReplaceByNext = False
    
    
            
    color = Color.colorSet    
    print = color

    def err_and_exit(msg, wait = 20):
        color("§c" + msg)
        time.sleep(wait)
        exitChatbarMenu()

    def countdown(delay: int | float, msg: str = None) -> None:
        """
        控制台显示倒计时的函数
        参数:
            delay: int | float -> 倒计时时间(秒)
            msg: str -> 倒计时运行时显示的说明
        返回: 无返回值
        """
        if msg is None:
            msg = "Countdown"
        delayStart = time.time()
        delayStop = delayStart+delay
        while delay >= 0.01:
            delay = delayStop-time.time()
            color("%s: %.2fs" % (msg, delay), replace = True, replaceByNext = True, info = "§e 等待 ")
            time.sleep(0.01)

    def exitChatbarMenu(killFB: bool = True, delay: int | float = 3, reason: str = None, force = False) -> None:
        """
        退出命令系统的函数
        参数:
            killFB: bool -> 是否同时关闭FastBuilder
            delay: int | float -> 倒计时时间(秒)
            reason: str -> 退出时显示的说明
        返回: 无返回值
        """
        global exiting, exitDelay, exitReason
        if force:
            try:
                FBkill()
            except:
                pass
            finally:
                color("§e正在清空globals变量.", info = "§e 加载 ")
                globals().clear()
        exitDelay = delay
        exitReason = reason
        exiting = True
        raise SystemExit(0)


    try:
        pid = os.getpid()
        os.system("echo DotCS 正在运行, 其进程 pid 为 %d." % pid)
        color("§aColorTest")
        _loadPackagesStartedTime = time.time()
        # Python 自带库.
       
        # 第三方库.
        PyPIthird = [
            {"name": "bdx_work_shop", "author": "2401PT, SuperScript", "link": "https://github.com/CMA2401PT/BDXWorkShop"},
            {"name": "FastBuilder connector", "author": "2401PT", "link": "https://github.com/CMA2401PT/FastBuilder"},
            {"name": "TDES encrypt", "author": "7912", "link": "None"},
            {"name": "Space Rectangular Coordinate System", "author": "7912", "link": "None"}
        ]
        for i in PyPIthird:
            color("DotCS 使用了 §e%s§r 库, 其作者是 §e%s§r, 链接: %s" % (i["name"], i["author"], i["link"]), info = " 信息 ")
        
        _veryNeedDirs = [
            "plugin",
            "status", 
            "player",
            "serverMsg",
            "_Plugin_Data"
        ]
        
        for _dir in _veryNeedDirs:
            if not os.path.isdir(_dir):
                os.mkdir(_dir)
                
        if not os.path.isfile("start.bat"):
            with open("start.bat", "w", encoding="utf-8") as batfile:
                batfile.write("@echo off\nDotCSLite.py\nchoice /t 0.5 /d y /n 1>nul\n%0")
                batfile.close()
                del batfile
                
        if not os.path.isfile("status/itemNetworkID.txt"):
            with open("status/itemNetworkID.txt", "w", encoding='utf-8') as file:
                file.write(itemNetworkList)
                file.close()
                del file, itemNetworkList
            
        _loadPackagesUsedTime = time.time() - _loadPackagesStartedTime
        
        arg_arr = sys.argv
        # 启动参数
        for argvs in arg_arr:
            try:
                getdata=arg_arr[arg_arr.index(argvs)+1]
            except:
                getdata=None
                
            match argvs:
                case "--debug":
                    try:
                        _root.debug = eval(getdata)
                        color("§fDebug mode: §aon")
                    except:
                        color("§c启动参数[debug]不正确的值:%s, 只能为bool类型"%getdata, info = "§c 错误 ")
                        while 1: pass
                        
                case "--fb-name":
                    _root.fbname = getdata
                        
                case "--default-pos":
                    try:
                        _root.defaultPosX, _root.defaultPosY, _root.defaultPosZ = eval(getdata)
                    except:
                        color("§c启动参数[default-pos]不正确的值:%s, 只能为元组或列表类型, 如(100000, 100000, 100000)"%getdata, info = "§c 错误 ")
                        while 1: pass
                        
                case "--Omega" | "--O":
                    _root._needOmega = True
                    
                case "--def-no-color":
                    _root.DefColor = False
                        
        platformVer = str(platform.platform())
        
        if "Windows" in platformVer:
            platformVer = "Windows"
            outputTime = "long"
        else:
            platformVer = "Linux"
            outputTime = "short"

    except Exception as err:
        color("§c启动初始化失败, 信息:\n"+str(err), info = "§c 错误 ")
        color("§c"+traceback.format_exc(), info = "§c 错误 ")
        exitChatbarMenu(False, 5)


    def is_port_used(port: int) -> bool:
        """
        检测端口是否被占用的函数
        参数:
            port: int -> 要检测的端口
        返回:
            端口未占用: bool -> False
            端口被占用: bool -> True
        """
        portUsed = False
        for proc in psutil.process_iter():
            try:
                if _root.fbname in proc.name():
                    if strInList(str(port), proc.cmdline()):
                        portUsed = True
            except:
                pass
        return portUsed


    def FBkill() -> None:
        """
        关闭FastBuilder的函数
        """
        for proc in psutil.process_iter():
            try:
                if _root.fbname in proc.name():
                    if strInList(server, proc.cmdline()):
                        proc.kill()
                        color("§6已终止 FastBuilder ,其 pid 为 %d" % proc.pid, info = "§6  FB  ")
            except:
                pass


    def runFB(killFB: bool = True) -> None:
        """
        启动FastBuilder的函数
        参数:
            killFB: bool -> 启动前是否关闭FastBuilder
        返回: 无返回值
        """
        global platformVer, FBport
        if FBip == "localhost" or FBip == "127.0.0.1":
            color("§e正在启动 FastBuilder.", info = "§e 加载 ")
            if killFB:
                FBkill()
            if os.path.isfile("nohup.out"):
                try:
                    os.remove("nohup.out")
                    open("nohup.out", "w").write("")
                except:
                    pass
            while is_port_used(FBport):
                color("§e端口 %d 被占用, 正在切换." % FBport, info = "§e 加载 ")
                FBport += 10
            if platformVer == "Windows":
                os.system('mshta vbscript:createobject("wscript.shell").run("""cmd.exe""/C %s -t fbtoken --code %s --password %s --listen-external 0.0.0.0:%d --no-readline --no-update-check>nohup.out",0)(window.close)' % (_root.fbname, server, serverPassword, FBport))
            else:
                os.system("nohup ./fbname -t fbtoken --code %s --password %s --listen-external 0.0.0.0:%d --no-readline --no-update-check &" % (_root.fbname, server, serverPassword, FBport))


    def Byte2KB(byteSize: int) -> str:
        """
        将字节单位转换为最大能转换的单位的函数
        参数:
            byteSize: int -> 字节单位大小
        返回: str: -> 转换后的格式
        """
        for i in ["B", "KB", "MB", "GB", "TB", "PB", "EB"]:
            if byteSize > 1024:
                byteSize /= 1024
            else:
                return "%.2f%s" % (byteSize, i)


    def setGlobalVar(key, value):
        if value is None:
            globals().__delitem__(value)
        else:
            globals().update({key: value})


    def fileDownload(url: str, path: str, timeout: float | int = 20, freshSize: int = 10240) -> dict:
        """
        下载文件并显示进度的函数
        参数:
            url: str -> 文件链接
            path: str -> 文件存储位置
            timeout: float | int -> 下载超时处理, 单位: 秒
            freshSize: int -> 每次下载的文件大小, 单位: 字节, 说明: 此数值越大, 对CPU的使用越低, 控制台更新下载进度状态的频率也越慢
        返回:
            dict: -> 下载是否成功
                成功: status -> success
                失败: status -> fail
                    无法找到目标服务器: reason -> file not found
                    目标服务器拒绝下载: reason -> server rejected
                    下载时连接中断或超时: reason -> timed out
        """
        try:
            response = requests.get(url, stream = True, timeout = timeout)
        except Exception as err:
            color("§c下载失败, 原因: 文件未找到.", info = "§c 错误 ")
            return {"status": "fail", "reason": "file not found"}
        fileDownloadedSize = 0
        fileSize = int(response.headers['content-length'])
        if response.status_code == 200:
            color("§e开始下载, 文件大小: %s" % Byte2KB(fileSize), info = "§e 下载 ")
            timeDownloadStart = time.time()
            fileDownloadedLastSize = 0
            speedDownloadCurrent = 0
            timeRem = "--:--:--"
            with open(path, 'wb') as file:
                try:
                    for data in response.iter_content(chunk_size = freshSize):
                        if exiting:
                            color("§c下载失败, 原因: 命令系统退出", info = "§c 错误 ")
                            return {"status": "fail", "reason": "exit"}
                        file.write(data)
                        fileDownloadedSize += len(data)
                        if time.time()-timeDownloadStart >= 0.5:
                            speedDownloadCurrent = (fileDownloadedSize-fileDownloadedLastSize)/(time.time()-timeDownloadStart)
                            timeDownloadStart = time.time()
                            fileDownloadedLastSize = fileDownloadedSize
                            if speedDownloadCurrent != 0:
                                timeRem = second2minsec((fileSize-fileDownloadedSize)/speedDownloadCurrent)
                        color("§e正在下载: %.2f%%, %s / %s, %s/s, 预计还需 %s" % (fileDownloadedSize/fileSize*100, Byte2KB(fileDownloadedSize), Byte2KB(fileSize), Byte2KB(speedDownloadCurrent), timeRem), replace = True, info = "§e 下载 ")
                except Exception as err:
                    color("§c下载失败, 原因: 连接超时", info = "§c 错误 ")
                    return {"status": "fail", "reason": "timed out"}
            color("§a下载完成", info = "§a 成功 ")
            return {"status": "success"}
        else:
            color("§c下载失败, 原因: 状态码 %s" % response.status_code, info = "§c 错误 ")
            return {"status": "fail", "reason": "server rejected", "status_code": response.status_code}


    def updateCheck() -> None:
        pass


    sendtogroup = ""
    QQgroup = ""
    def NekoMaidMsg(msg, msgIndex, connToSend, isLastFormat = False): pass
    def log(text: str, filename: str = None, mode: str = "a", encoding: str = "utf-8", errors: str = "ignore", output: bool = True, sendtogamewithRitBlk: bool = False, sendtogamewithERROR: bool = False, sendtogrp: bool = False, info = " 信息 ") -> None:
        """
        记录日志的函数
        参数:
            text: str -> 要记录的信息
            filename: str -> 写入文件位置, 默认写入在 serverMsg\%Y-%m-%d.txt
            mode: str -> 记录方法, 同open()
            encoding: str -> 记录编码, 同open()
            errors: str -> 错误处理方式, 同open()
            output: bool -> 是否同时在控制台输出
        返回: 无返回值
        """
        if filename is None:
            filename = "serverMsg/"+datetime.datetime.now().strftime("%Y-%m-%d.txt")
        if text[-1:] == "\n":
            text = text[:-1]
        if output:
            color(text+"\033[0m", info = info)
        try:
            with open(filename, mode, encoding = encoding, errors = errors) as file:
                file.write("["+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"] "+text+"\n")
        except Exception as err:
            color("写入日志错误, 信息:\n"+str(err), info = "§c 错误 ")
        if sendtogamewithRitBlk and connected:
            tellrawText("@a", "§l§6Ritle§aBlock§r", text = text)
        if sendtogamewithERROR and connected:
            tellrawText("@a", "§l§4ERROR§r", text = "§c" + text)
        if sendtogrp:
            try:
                sendtogroup("group", QQgroup, text)
            except Exception as err:
                errmsg = "log()函数中sendtogroup()报错, 信息:\n"+str(err)
                log("§c" + errmsg, info = "§c 错误 ")
        for i in threadList[:]:
            try:
                if i.name == "与NekoMaid网站通信":
                    for j in text.split("\n"):
                        NekoMaidMsg(["NekoMaid:console:log", {"level": "INFO", "logger": "net.minecraft.server.v1_16_R3.DedicatedServer", "msg": "%s§r" % "["+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"] "+j.replace("'", 'unchanged'), "time": time.time()*1000}], "42", i.data["conn"], True)
            except:
                pass


    def tellrawText(who: str, dispname: None | str = None, text: str = None) -> None:
        """
        便捷执行tellraw的函数
        参数:
            who: str.MinecraftTargetSelector -> 给谁显示
            dispname: None | str -> 模拟玩家说话格式, 不传则直接tellraw
            text: str -> 要显示的信息
        返回: 无返回值
        """
        if dispname is None:
            sendcmd(r"""/tellraw %s {"rawtext":[{"text":"%s"}]}""" % (who, text.replace('"', '’’').replace("'", '’')))
        else:
            sendcmd(r"""/tellraw %s {"rawtext":[{"text":"<%s> %s"}]}""" % (who, dispname.replace('"', '’’').replace("'", '’'), text.replace('"', '’’').replace("'", '’')))


    def tellrawScore(scoreboardName: str, targetName: str) -> str:
        """
        返回tellraw计分板格式的函数
        参数:
            scoreboardName: str -> 计分板名称
            targetName: str -> 计分板对象
        返回: str -> tellraw计分板格式
        """
        return '{"score":{"name":"%s","objective":"%s"}}' % (targetName, scoreboardName)


    FBlog_old = []
    def FBlogRead() -> str:
        """
        读取FastBuilder日志的函数
        你不应该使用此函数, 命令系统会每秒运行1次此函数
        """
        if FBip == "localhost" or FBip == "127.0.0.1":
            global FBlog_old
            try:
                with open("nohup.out", "r", encoding = "utf-8") as file:
                    FBlog = file.readlines()
                    FBlogNew = []
                    for i in range(len(FBlog)):
                        try:
                            FBlog[i] = FBlog[i].replace("\n", "").replace("\r", "")
                        except:
                            pass
                    if FBlog != FBlog_old:
                        for i in FBlog:
                            if i not in FBlog_old:
                                FBlogNew.append(i)
                    if FBlogNew != []:
                        for i in FBlogNew:
                            color(i, info = "§6  FB  ")
                        if strInList("ERROR", FBlogNew) and not strInList("触发词冲突", FBlogNew):
                            if connected:
                                FBkill()
                            else:
                                exitChatbarMenu(reason = "FastBuilder ERROR", delay = 60)
                    FBlog_old = FBlog
                    return FBlog
            except:
                pass
        return False


    gameTime = "00:00:00"
    tps = {"1s": 0, "5s": 0, "20s": 0, "1m": 0, "5m": 0, "10m": 0}
    def getGameTimeRepeat(self) -> None:
        global gameTime
        gameTimeTickLast = 0
        timeLastGet = 0
        tpsList = [20] * 1200
        while True:
            try:
                if exiting:
                    return
                timeStart = time.time()
                timeGet = time.time()
                gameTimeTick = (int(sendcmd("/time query daytime", True, timeout = 20)["OutputMessages"][0]["Parameters"][0])+6000)%24000
                gameTime = second2minsec(round(gameTimeTick / 24000*86400))
                tps_1s = float("%.2f" % ((gameTimeTick-gameTimeTickLast)/(timeGet-timeLastGet)))
                if tps_1s > 0 and tps_1s < 50:
                    tpsList.append(tps_1s)
                if len(tpsList) > 1200:
                    tpsList = tpsList[-1200:]
                if len(tpsList) >= 2:
                    tps["1s"] = float("%.2f" % (sum(tpsList[-2:])/2))
                if len(tpsList) >= 10:
                    tps["5s"] = float("%.2f" % (sum(tpsList[-10:])/10))
                if len(tpsList) >= 40:
                    tps["20s"] = float("%.2f" % (sum(tpsList[-40:])/40))
                if len(tpsList) >= 120:
                    tps["1m"] = float("%.2f" % (sum(tpsList[-120:])/120))
                if len(tpsList) >= 600:
                    tps["5m"] = float("%.2f" % (sum(tpsList[-600:])/600))
                if len(tpsList) >= 1200:
                    tps["10m"] = float("%.2f" % (sum(tpsList[-1200:])/1200))
            except Exception as err:
                errmsg = "getGameTimeRepeat()函数报错, 信息:\n"+str(err)
                color("§c"+traceback.format_exc(), info = "§c 错误 ")
                log("§c" + errmsg, sendtogamewithERROR = True, info = "§c 错误 ")
            finally:
                while time.time() - timeStart < 0.5:
                    constChangeLock.acquire()
                    try:
                        for i in [const, const2]:
                            for j in [const, const2]:
                                for k in ["__dict_hidden__", "__dict_hidden2__"]:
                                    for l in ["__dict_hidden__", "__dict_hidden2__"]:
                                        if object.__getattribute__(i, k) != object.__getattribute__(j, l):
                                            exitChatbarMenu(reason = "§cCONST被篡改了？？？！！你不应该修改CONST！！！！", info = "§4 警告 ")
                    except:
                        exitChatbarMenu(reason = "§cCONST被篡改了？？？！！你不应该修改CONST！！！！", info = "§4 警告 ")
                    constChangeLock.release()
                    time.sleep(0.001)
                gameTimeTickLast = gameTimeTick
                timeLastGet = timeGet

    def playerXUIDThread(self) -> None:
            """
            设置了新线程处理.
            SuperScript
            """
            global allplayers, XUID2playerName
            color("§e正在检测在线玩家的游戏名中是否包含违禁词.", info = "§e 加载 ")
            for i in allplayers[:]:
                color("§e正在检测: %s" % i, replace = True, replaceByNext = True, info = "§e 加载 ")
                hasPWord = False
                if getPlayerData("prohibitedWord", i, "False") == "False":
                    if prohibitedWordTest(i):
                        hasPWord = True
                        setPlayerData("prohibitedWord", i, "True")
                else:
                    hasPWord = True
                if hasPWord:
                    color("§c玩家 %s 的游戏名中包含违禁词, 正在踢出." % i, info = "§c 警告 ")
                    sendwocmd('/kick "%s" §c您的名称内有违禁词, 无法进服.' % i)
                    allplayers.remove(i)

            color("§e正在获取在线玩家的XUID.", info = "§e 加载 ")
            for i in allplayers:
                color("§e正在获取: %s" % i, replace = True, replaceByNext = True, info = "§e 加载 ")
                result = sendcmd('/querytarget @a[name="%s"]' % i, True, timeout = 20)["OutputMessages"][0]
                if result["Success"] == False:
                    err_and_exit("获取玩家XUID失败")
                XUID2playerName[json.loads(result["Parameters"][0])[0]["uniqueId"][-8:]] = i
            for i in allplayers:
                color("§e正在验证: %s" % i, replace = True, replaceByNext = True, info = "§e 加载 ")
                if i not in list(XUID2playerName.values()):
                    err_and_exit(f"获取玩家 {i} 的XUID失败")
            try:
                allplayers.remove(robotname)
            except:
                pass

    def pluginRepeat(self) -> None:
        """
        命令系统启动后处理repeat类插件的函数
        你不应该使用此函数, 命令系统会自动以新线程运行它
        """
        global msgList
        timeDict = {"1s": {"time": 1, "timeNow": 0}, "10s": {"time": 10, "timeNow": 0}, "1m": {"time": 60, "timeNow": 0}}
        while True:
            if exiting:
                return
            for i in timeDict:
                if timeDict[i]["timeNow"] == 0:
                    timeDict[i]["timeNow"] = timeDict[i]["time"]
                    msgList.append([-100, {"pluginRunType": "repeat %s" % i}, -1])
                timeDict[i]["timeNow"] -= 1
            time.sleep(1)


    def othersRepeat(self) -> None:
        """
        命令系统启动后每60秒运行1次的函数
        你不应该使用此函数, 命令系统会自动以新线程运行它
        """
        global allplayers, FBlog
        while True:
            timeStart = time.time()
            try:
                if connected:
                    updateCheck()
                    allplayers = getTarget("@a[rm=0.001]", timeout = 60)
            except Exception as err:
                pass
            finally:
                while time.time() - timeStart < 60:
                    if exiting:
                        return
                    if not connected:
                        FBlog = FBlogRead()
                    time.sleep(1)


    def _delayExec(self):
        timeDelay = self.data["delay"]
        func = self.data["func"]
        time.sleep(timeDelay)
        try:
            if type(func).__name__ == "str":
                exec(func)
            else:
                func()
        except Exception as err:
            errmsg = "延迟执行报错, 信息:\n"+str(err)
            color("§c"+traceback.format_exc(), info = "§c 错误 ")
            log("§c" + errmsg, info = "§c 错误 ", sendtogamewithERROR = True)


    def delayExec(func, delay):
        createThread("延迟执行", data = {"delay": delay, "func": func}, func = _delayExec, output = False)


    def getPlayerData(dataName: str, playerName: str, writeNew: str = "") -> (str | int | float):
        """
        获取玩家本地数据的函数
        读取文件: player\playerName\dataName.txt
        参数:
            dataName: str -> 数据名称
            playerName: str -> 玩家名称
            writeNew: str -> 若数据不存在, 写入的数据
        返回: str | int | float -> 文件读取结果
        """
        dataName = dataName.replace("\\", "/")
        fileDir = "player/%s/%s.txt" % (playerName, dataName)
        pathDir = ""
        pathAll = ("player/%s/%s" % (playerName, dataName)).split("/")
        pathAll.pop(-1)
        for i in pathAll:
            pathDir += "%s/" % i
        if not os.path.isdir(pathDir):
            pathToCreate = ""
            for i in pathDir.split("/"):
                try:
                    pathToCreate += "%s/" % i
                    os.mkdir(pathToCreate)
                except:
                    pass
        if not os.path.isfile(fileDir):
            with open(fileDir, "w", encoding = "utf-8", errors = "ignore") as file:
                file.write(writeNew)
        with open(fileDir, "r", encoding = "utf-8", errors = "ignore") as file:
            data = file.read()
        if "." not in data:
            try:
                data = int(data)
            except:
                pass
        else:
            try:
                data = float(data)
            except:
                pass
        return data

    def setPlayerData(dataName: str, playerName: str, dataValue, writeNew: str = ""):
        """
        设置玩家本地数据的函数
        写入文件: player\playerName\dataName.txt
        参数:
            dataName: str -> 数据名称
            playerName: str -> 玩家名称
            dataValue: Any -> 要设置的数据, 写入前会自动转化为str
            writeNew: str -> 若数据不存在, 写入的数据
        返回: dataValue: Any -> 设置结果
        """
        dataName = dataName.replace("\\", "/")
        fileDir = "player/%s/%s.txt" % (playerName, dataName)
        pathDir = ""
        pathAll = ("player/%s/%s" % (playerName, dataName)).split("/")
        pathAll.pop(-1)
        for i in pathAll:
            pathDir += "%s/" % i
        if not os.path.isdir(pathDir):
            pathToCreate = ""
            for i in pathDir.split("/"):
                try:
                    pathToCreate += "%s/" % i
                    os.mkdir(pathToCreate)
                except:
                    pass
        if not os.path.isfile(fileDir):
            with open(fileDir, "w", encoding = "utf-8", errors = "ignore") as file:
                file.write(writeNew)
        with open(fileDir, "w", encoding = "utf-8", errors = "ignore") as file:
            file.write(str(dataValue))
        return dataValue

    def addPlayerData(dataName: str, playerName: str, dataValue, dataType: str = "int", writeNew: str = ""):
        """
        增加/追加玩家本地数据的函数
        写入文件: player\playerName\dataName.txt
        参数:
            dataName: str -> 数据名称
            playerName: str -> 玩家名称
            dataValue: Any -> 要设置的数据, 写入前会自动转化为str
            dataType: "int" | "add" -> 设置类型
                add: 在文件末尾追加
                int: 数学计算, 加上新值
            writeNew: str -> 若数据不存在, 写入的数据
        返回: dataValue: Any -> 设置结果
        """
        if dataType == "int":
            return setPlayerData(dataName, playerName, getPlayerData(dataName, playerName, writeNew)+dataValue, writeNew)
        elif dataType == "add":
            dataName = dataName.replace("\\", "/")
            fileDir = "player/%s/%s.txt" % (playerName, dataName)
            pathDir = ""
            pathAll = ("player/%s/%s" % (playerName, dataName)).split("/")
            pathAll.pop(-1)
            for i in pathAll:
                pathDir += "%s/" % i
            if not os.path.isdir(pathDir):
                pathToCreate = ""
                for i in pathDir.split("/"):
                    try:
                        pathToCreate += "%s/" % i
                        os.mkdir(pathToCreate)
                    except:
                        pass
            with open(fileDir, "a", encoding = "utf-8", errors = "ignore") as file:
                file.write("%s\n" % str(dataValue))
            return dataValue
        else:
            raise Exception("dataType error")


    def getType(sth):
        return sth.__class__.__name__


    def float2int(number: float, way: int = 1) -> int:
        """
        小数转整数的函数
        参数:
            number: float -> 要转换的小数
            way: 1 | 2 | 3 -> 转换方式
                1: 四舍五入
                2: 舍去小数部分
                3: 若有小数部分, 则入
        返回: int -> 转换结果
        """
        if way == 1:
            return round(number)
        elif way == 2:
            return int(number)
        elif way == 3:
            if int(number) == number:
                return int(number)
            else:
                return int(number)+1


    def floatPos2intPos(number: float | str) -> int:
        if type(number) == str:
            number = float(number)
        if type(number) == int:
            return number
        if int(number) == number:
            return int(number)
        if number > 0:
            return int(number)
        if number < 0:
            return int(number)-1
        raise ValueError("居然能运行到这里, 我也不知道出什么bug了...")
        # 7912: 不行就抛错误


    def second2minsec(sec: int) -> str:
        """
        秒数转正常时间显示的函数
        比如将 79 转换为 00:01:19
        参数:
            sec: int -> 要转换的秒数
        返回: str -> 转换结果
        """
        min, sec = divmod(sec, 60)
        hour, min = divmod(min, 60)
        hour, min, sec = str(int(hour)), str(int(min)), str(int(sec))
        if len(hour) == 1:
            hour = "0" + hour
        if len(min) == 1:
            min = "0" + min
        if len(sec) == 1:
            sec = "0" + sec
        return "%s:%s:%s" % (hour, min, sec)


    def getTarget(sth: str, timeout: bool | int = 1) -> list:
        """
        获取租赁服内对应目标选择器实体的函数
        参数:
            sth: str.MinecraftTargetSelector -> 要获取的目标选择器
        返回: list -> 获取结果
        例子:
        >>> a = getTarget("@a")
        >>> print(a)
        ["player1", "player2", ...]
        """
        if not sth.startswith("@"):
            raise Exception("Minecraft Target Selector is not correct.")
        result = sendcmd("/tell @s get%s" % sth, True, timeout)
        result = result["OutputMessages"][0]["Parameters"][1][3:]
        if ", " not in result:
            if not result:
                return []
            return [result]
        else:
            return result.split(", ")


    def getScore(scoreboardNameToGet: str, targetNameToGet: str) -> int:
        """
        获取租赁服内对应计分板数值的函数
        参数:
            scoreboardName: str -> 计分板名称
            targetName: str -> 计分板对象名称
        返回: int -> 获取结果
        """
        resultList = sendcmd("/scoreboard players list %s" % targetNameToGet, True)["OutputMessages"]
        result = {}
        result2 = {}
        for i in resultList:
            Message = i["Message"]
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


    def getPos(targetNameToGet: str, timeout: float | int = 1) -> dict:
        """
        获取租赁服内玩家坐标的函数
        参数:
            targetNameToGet: str -> 玩家名称
        返回: dict -> 获取结果
        """
        if (targetNameToGet not in allplayers) and (targetNameToGet != robotname) and (not targetNameToGet.startswith("@a")):
            raise Exception("Player not found.")
        result = sendcmd("/querytarget %s" % targetNameToGet, True, timeout)["OutputMessages"][0]
        if result["Success"] == False:
            raise Exception("Failed to get the position.")
        resultList = json.loads(result["Parameters"][0])
        result = {}
        for i in resultList:
            targetName = XUID2playerName[i["uniqueId"][-8:]]
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


    def getItem(targetName: str, itemName: str, itemSpecialID: int = -1) -> int:
        """
        获取租赁服内玩家某物品个数的函数
        参数:
            targetName: str -> 玩家名称
            itemName: str -> 物品英文名称
            itemSpecialID: int -> 物品特殊值
        返回: int -> 获取结果
        """
        if (targetName not in allplayers) and (targetName != robotname) and (not targetName.startswith("@a")):
            raise Exception("Player not found.")
        result = sendcmd("/clear %s %s %d 0" % (targetName, itemName, itemSpecialID), True)
        if result["OutputMessages"][0]["Message"] == "commands.generic.syntax":
            raise Exception("Item name error.")
        if result["OutputMessages"][0]["Message"] == "commands.clear.failure.no.items":
            return 0
        else:
            return int(result["OutputMessages"][0]["Parameters"][1])


    def getStatus(statusName: str) -> str:
        """
        获取状态数据的函数
        读取文件: status\statusName.txt
        参数:
            statusName: str -> 数据名称
        返回: str -> 文件读取结果
        """
        if not os.path.isfile("status/%s.txt" % statusName):
            return None
        with open("status/%s.txt" % statusName, "r", encoding = "utf-8") as file:
            status = file.read()
        return status


    def setStatus(statusName: str, status):
        """
        设置状态数据的函数
        设置文件: status\statusName.txt
        参数:
            statusName: str -> 数据名称
            status: Any -> 要写入的信息, 写入前会转化为str
        返回: Any -> 设置结果
        """
        with open("status/%s.txt" % statusName, "w", encoding = "utf-8") as file:
            file.write(str(status))



    def QRcode(text: str, where: str = "console", who: str | None = None) -> None:
        """
        在控制台或租赁服输出二维码的函数
        参数:
            text: str -> 要转换的信息
            where: "console" | "server" -> 输出地点
                console: 控制台
                server: 租赁服
            who: str.MinecraftTargetSelector -> 如果发到租赁服, 发送的对象
        返回: None
        """
        if where != "console" and where != "chatbar" and where != "actionbar":
            raise Exception("invalid argument")
        if where != "console" and (who is None):
            raise Exception("invalid argument")
        qr = qrcode.QRCode()
        qr.add_data(text)
        qrline = ""
        qrall = ""
        for i in qr.get_matrix():
            for j in i:
                if j == False:
                    qrline += "\033[0;37;7m  " if (where == "console") else "§f▓"
                else:
                    qrline += "\033[0m  " if (where == "console") else "§0▓"
            if where == "console":
                color("%s\033[0m" % qrline)
            elif where == "chatbar":
                tellrawText(who, text = "§l"+qrline)
            qrall += qrline
            qrline = ""
        if where == "actionbar":
            sendcmd("/title %s actionbar %s" % (who, qrall))


    sendcmdResponse = {}
    def sendcmd(cmd: str, waitForResponse: bool = False, timeout: float | int = 1) -> None:
        """
        以 WebSocket 身份发送指令到租赁服的函数
        ---
        参数:
            cmd: str (Minecraft command) -> 要在租赁服执行的指令.
            waitForResponse: bool -> 是否等到收到命令执行结果再返回结果.
                False: 不等结果, 直接返回命令执行的uuid. `(一瞬间)`
                True : 等到收到结果了再返回结果. `(需要1~2游戏刻)`
            timeout: number -> 等待返回结果的最长时间
        返回:
            `waitForResponse = False`:
                str : 命令执行的uuid.
            `waitForResponse = True `:
                Dict: 命令执行的返回结果.
        报错:
            TimeoutError: 等待命令执行结果超时.
        """
        global sendcmdResponse
        if cmd[0] == "/":
            cmd = cmd[1:]
        uuid = conn.SendMCCommand(connID, cmd).decode("utf-8")
        if not waitForResponse:
            return uuid
        else:
            sendcmdResponse[uuid] = None
            startTime = time.time()
            while not sendcmdResponse[uuid]:
                if int(time.time() - startTime) > timeout:
                    del sendcmdResponse[uuid]
                    raise TimeoutError("timed out")
                time.sleep(0.001)
            result = sendcmdResponse[uuid]
            del sendcmdResponse[uuid]
            return result

    def sendplayercmd(cmd: str, waitForResponse: bool = False) -> None:
        """
        以 玩家(FastBuilder机器人) 身份发送指令到租赁服的函数
        ---
        参数:
            cmd: str (Minecraft command) -> 要在租赁服执行的指令.
            waitForResponse: bool -> 是否等到收到命令执行结果再返回结果.
                False: 不等结果, 直接返回命令执行的uuid. `(一瞬间)`
                True : 等到收到结果了再返回结果. `(需要1~2游戏刻)`
            timeout: number -> 等待返回结果的最长时间
        返回:
            `waitForResponse = False`:
                str : 命令执行的uuid.
            `waitForResponse = True `:
                Dict: 命令执行的返回结果.
        报错:
            TimeoutError: 等待命令执行结果超时.
        """
        global sendcmdResponse
        if cmd[0] == "/":
            cmd = cmd[1:]
        uuid = conn.SendWSCommand(connID, cmd).decode("utf-8")
        if not waitForResponse:
            return uuid
        else:
            sendcmdResponse[uuid] = None
            startTime = time.time()
            while not sendcmdResponse[uuid]:
                if int(time.time() - startTime) > 1:
                    del sendcmdResponse[uuid]
                    raise TimeoutError("timed out")
                time.sleep(0.001)
            result = sendcmdResponse[uuid]
            del sendcmdResponse[uuid]
            return result

    def sendwocmd(cmd: str) -> None:
        """
        以最高权限(租赁服控制台)身份发送指令到租赁服的函数
        ---
        你可以执行 /stop, 这会导致租赁服关闭, 然后重启
        参数:
            cmd: str (Minecraft command) -> 要在租赁服执行的指令.
        """
        if cmd[0] == "/" or cmd[0] == "!":
            cmd = cmd[1:]
        # if cmd.startswith("stop"):
        #     exitChatbarMenu(reason = "You can not use the command 'stop'.")
        conn.SendNoResponseCommand(connID, cmd)

    def sendfbcmd(cmd: str) -> None:
        """
        发送命令到FastBuilder的函数
        参数:
            cmd: str (FastBuilder command) -> FastBuilder执行指令
        返回: 无返回值
        """
        if cmd[0] == "?":
            cmd = cmd[1:]
        conn.SendFBCommand(connID, cmd)


    def strInList(string: str, list: list) -> bool:
        """
        检测字符串是否在列表里的函数
        参数:
            str: str -> 要检测的字符串
            list: list -> 要检测的列表
        返回:
            若str在list里: bool -> True
            若str不在list里: bool -> False
        """
        string = str(string)
        for i in list:
            if string in i:
                return True
        return False


    PWordResponse = {}
    def prohibitedWordTest(word):
        uuid = sendcmd("%s 测试 %d" % (word, random.randint(0, 100)))
        PWordResponse[uuid] = False
        sendcmd("Finished test.", True, 5)
        if not PWordResponse[uuid]:
            del PWordResponse[uuid]
            return True
        else:
            del PWordResponse[uuid]
            return False


    msgList = []
    rev = ""
    playername = ""
    allplayers = []
    robotname = ""
    XUID2playerName = {}
    msgLastRecvTime = time.time()
    itemNetworkID2NameDict = {}
    itemNetworkID2NameEngDict = {}
    adminhigh = []
    def processPacket(self) -> None:
        """
        处理FastBuilder发送来的包的函数
        你不应该使用此函数, 命令系统会在运行FastBuilder后以新线程启动此函数
        """
        global msgLastRecvTime, XUID2playerName, timeSpentFBRun, msgList, server, server, connID, robotname, allplayers, connected
        try:
            connected = True
            msgList.append([-100, {"pluginRunType": "init"}, -1])
            sendwocmd("changesetting allow-cheats true")

            color("§e正在获取机器人游戏名和在线玩家.", info = "§e 加载 ")
            _retrying = 0
            while 1:
                    getResult = sendcmd("/tell @s get@a", True, 20)
                    if _root.debug:
                        print(getResult)
                    if getResult['SuccessCount']:
                        getRobotName = getResult["OutputMessages"][0]["Parameters"][1][3:]
                        break
                    elif _retrying >=10:
                        pass
                    else:
                        color("§6获取失败, 正在重试", info = "§6 重试 ")
                        _retrying += 1
            robotname = getRobotName
            if ")" in robotname:
                color("§cFastBuilder 机器人游戏名异常.", info = "§c 错误 ")
                exitChatbarMenu(reason = "机器人游戏名异常")
            if robotname not in adminhigh:
                adminhigh.append(robotname)
                
            allplayers = getTarget("@a", timeout = 20)

            
            createThread("玩家信息检测初始化", data = {}, func = playerXUIDThread)
            createThread("获取租赁服游戏时间并计算tps", data = {}, func = getGameTimeRepeat)
            createThread("执行repeat类插件", data = {}, func = pluginRepeat)

            timeSpentRun = float(time.time()-timeStartRun)
            timeSpentDotCSRun = timeSpentRun-timeSpentFBRun
            color("§6Super特制版DotCS第一版, 下个版本再做加载速度优化吧awa")
            color("§a成功启动 DotCS 社区版, 用时: %.2fs. (DotCS: %.2fs, FB: %.2fs)" % (timeSpentRun, timeSpentDotCSRun, timeSpentFBRun), info = "§a 成功 ")
            color('§6".命令"系统成功启动.')
            color("§6共加载 %d§r§6 个插件/函数." % len(pluginList))
            
            tellrawText("@a", "§6DotCS§f", "§a插件启动成功")
            sendcmd("/time add 0")
            sendcmd("/kill @e[type=xp_orb]")
            sendcmd("/gamemode c")
            sendcmd("/effect @s resistance 999999 19 true")
            sendcmd("/effect @s invisibility 999999 0 true")
            sendcmd(f"/tp {_root.defaultPosX} {_root.defaultPosY} {_root.defaultPosZ}")
            
            if not faststart:
                color("在控制台输入'faststart'可进入快速启动模式", info = " 提示 ")

            log("§6FastBuilder 机器人名: %s" % robotname, info = "§6  FB  ")
            log("§e当前在线玩家: "+(", ".join(allplayers)), info = "§e 信息 ")

            while True:
                if exiting:
                    return
                if msgList == []:
                    if time.time()-msgLastRecvTime >= 30:
                        log("§c30秒未收到数据包", info = "§c 错误 ")
                        exitChatbarMenu(reason = "Receive packet timed out")
                    time.sleep(0.01)
                    continue
                try:
                    rev = msgList.pop(0)
                    packetType = rev[0]
                    jsonPkt = rev[1]
                    packetNum = rev[2]
                    pluginRunType = ""
                except:
                    continue
                if packetType == 63 and jsonPkt["ActionType"] == 0:
                    XUID2playerName[jsonPkt["Entries"][0]["XUID"]] = jsonPkt["Entries"][0]["Username"]
                    jsonPkt = {'TextType': 2, 'NeedsTranslation': True, 'SourceName': '', 'Message': '§e%multiplayer.player.joining', 'Parameters': [jsonPkt["Entries"][0]["Username"]], 'XUID': '', 'PlatformChatID': '', 'PlayerRuntimeID': ''}
                    packetType = 9

                # 已经实现类型数据的解析
                # 处理文字信息.
                if packetType == 9:
                    # 初始化
                    textType = jsonPkt["TextType"]
                    playername = jsonPkt["SourceName"]
                    msg = jsonPkt["Message"]
                    try:
                        playername = playername.replace(">§r", "").split("><")[1]
                    except:
                        pass

                    # 处理收到的say信息
                    # 将其统一格式
                    if textType == 8:
                        msg = msg.split("] ", 1)[1]

                    # 处理收到的tellraw信息
                    if textType == 9:
                        msg = msg.replace('{"rawtext":[{"text":"', "").replace('"}]}', "").replace('"},{"text":"', "").replace(r"\n", "\n"+str(textType)+" ").replace("§l", "")
                        if msg[-1] == "\n":
                            msg = msg[:-1]
                        if "报错, 信息:" not in msg:
                            msg += "§r"
                            log(str(textType)+" "+msg, info = " 信息 ")

                    # 处理系统信息
                    elif textType == 2:
                        # 处理玩家准备进服信息
                        if msg == "§e%multiplayer.player.joining":
                            playername = jsonPkt["Parameters"][0]
                            log("§e%s 正在加入游戏" % playername, info = " 信息 ")
                            hasPWord = False
                            if getPlayerData("prohibitedWord", playername, "False") == "False":
                                if prohibitedWordTest(playername):
                                    hasPWord = True
                                    setPlayerData("prohibitedWord", playername, "True")
                            else:
                                hasPWord = True
                            if hasPWord:
                                log("§c玩家 %s 的游戏名中包含违禁词, 正在踢出." % playername, info = "§c 警告 ")
                                sendwocmd('/kick "%s" §c您的名称内有违禁词, 无法进服.' % playername)
                                continue
                            pluginRunType = "player prejoin"

                        # 处理玩家进服信息
                        if msg == "§e%multiplayer.player.joined":
                            playername = jsonPkt["Parameters"][0]
                            if playername not in allplayers:
                                allplayers.append(playername)
                            log("§e%s 加入了游戏" % playername, info = " 信息 ")
                            pluginRunType = "player join"

                        # 处理玩家退出信息
                        elif msg == "§e%multiplayer.player.left":
                            playername = jsonPkt["Parameters"][0]
                            if playername in allplayers:
                                allplayers.remove(playername)
                            log("§e%s 退出了游戏" % playername, info = " 信息 ")
                            sendcmd("/scoreboard players reset %s" % playername)
                            pluginRunType = "player leave"

                        # 处理玩家死亡信息
                        elif msg[0:6] == "death.":
                            playername = jsonPkt["Parameters"][0]
                            if playername in allplayers:
                                if len(jsonPkt["Parameters"]) == 2:
                                    killer = jsonPkt["Parameters"][1]
                                else:
                                    killer = None
                                log("%s 失败了, 信息: %s" % (playername, msg), info = " 信息 ")
                                pluginRunType = "player death"

                        # 过滤其他信息
                        else:
                            pass

                    # 处理玩家在聊天栏发送的信息, tell信息以及say信息
                    elif textType == 1 or textType == 7 or textType == 8:
                        if not (msg.startswith("test") or msg.startswith("get")):
                            log(str(textType)+" <"+playername+">"+" "+msg, info = " 信息 ")
                        if playername in allplayers or playername == robotname:
                            pluginRunType = "player message"


                if packetType == -100:
                    pluginRunType = jsonPkt["pluginRunType"]

                for i in pluginList:
                    if i.enable:
                        for j in ["packet -1", "packet %d" % packetType, pluginRunType]:
                            try:
                                if j in i.pluginCode:
                                    exec(i.pluginCode[j])
                            except PluginSkip: # 感谢SuperScript提供的建议. # awa
                                pass
                            except Exception as err:
                                errmsg = "插件 %s %s 报错, 信息:\n%s" % (i.pluginName, pluginRunType, str(err))
                                color("§c"+traceback.format_exc(), info = "§c 错误 ")
                                log("§c" + errmsg, sendtogamewithERROR = True, info = "§c 错误 ")


        except Exception as err:
            errmsg = "信息处理报错, 信息:\n"+str(err)
            color("§c"+traceback.format_exc(), info = "§c 错误 ")
            log("§c" + errmsg, info = "§c 错误 ")
            exitChatbarMenu(reason = "数据包进程信息处理错误")


    def revPacket(self) -> None:
        """
        连接FastBuilder并接收其发送来的包的函数
        你不应该使用此函数, 命令系统会在运行FastBuilder后以新线程启动此函数
        """
        global msgLastRecvTime, timeSpentFBRun, msgList, connID, timeStartFBRun, FBlog

        # 尝试连接
        color("§e正在连接到 FastBuilder.", info = "§e 加载 ")
        startTime = time.time()
        while True:
            try:
                if exiting:
                    return
                connID = conn.ConnectFB("%s:%d" % (FBip, FBport))
                break
            except:
                spendTime = time.time()-startTime
                if spendTime >= 60:
                    color("§cFastBuilder超过60秒未连接上租赁服, 正在退出.", info = "§c 错误 ")
                    exitChatbarMenu(reason = "FastBuilder timed out.")
                color("§e正在连接到 FastBuilder, %.5fs" % spendTime, replace = True, replaceByNext = True, info = "§e 加载 ")
                time.sleep(0.01)

        # 连上了
        color("§a成功连接到 FastBuilder.", info = "§a 成功 ")
        timeSpentFBRun = float(time.time()-timeStartFBRun)
        msgRecved = False

        # 开始收取聊天信息
        packetNum = 0
        while True:
            try:
                if exiting:
                    return
                packetNum += 1
                bytesPkt = conn.RecvGamePacket(connID)
                packetType = conn.inspectPacketID(bytesPkt)
                msgLastRecvTime = time.time()
                if not msgRecved:
                    msgRecved = True
                if packetNum == 1:
                    createThread("处理数据包", {}, processPacket)
                # if packetType == 39 or packetType == 40 or packetType == 111 or packetType == 123 or packetType == 58 or packetType == 108 or packetType == 158 or packetType == 67:
                #     continue
                jsonPkt = json.loads(conn.GamePacketBytesAsIsJsonStr(bytesPkt))
                pluginRunType = "packet on another thread %d" % packetType
                if packetType == 79:
                    uuid = jsonPkt["CommandOrigin"]["UUID"]
                    for i in list(sendcmdResponse):
                        if i == uuid:
                            sendcmdResponse[i] = jsonPkt
                    for i in list(PWordResponse):
                        if i == uuid:
                            PWordResponse[i] = True
                msgList.append([packetType, jsonPkt, packetNum])
                for i in pluginList:
                    try:
                        if i.enable and pluginRunType in i.pluginCode:
                            exec(i.pluginCode[pluginRunType])
                    except Exception as err:
                        errmsg = "插件 %s %s 报错, 信息:\n%s" % (i.pluginName, pluginRunType, str(err))
                        color("§c"+traceback.format_exc(), info = "§c 错误 ")
                        log("§c" + errmsg, sendtogamewithERROR = True, info = "§c 错误 ")

            except Exception as err:
                errmsg = "收取数据包报错, 信息:\n"+str(err)
                color("§c"+traceback.format_exc(), info = "§c 错误 ")
                log("§c" + errmsg, info = "§c 错误 ")
                exitChatbarMenu(reason = "收取数据包报错")


    def consoleInput(self) -> None:
        """
        控制台执行代码或使用聊天栏菜单的函数
        你不应该使用此函数, 命令系统会启动时以新线程运行此函数
        """
        while True:
            try:
                time.sleep(0.1)
                input_msg = input("")
                if not input_msg:
                    continue
                if input_msg in ["exit", ".exit", "stop", ".stop", "restart", ".restart"]:
                    exitChatbarMenu()
                    time.sleep(1)
                elif input_msg == "faststart":
                    setStatus("faststart", "True")
                elif input_msg[0] == "/":
                    sendcmd(input_msg)
                elif input_msg[0] == "!":
                    sendwocmd(input_msg)
                elif input_msg[0] == "?":
                    sendfbcmd(input_msg)
                elif input_msg[0] == ".":
                    msgList.append([9, {"TextType": 1, "SourceName": robotname, "Message": input_msg}, -1])
                elif input_msg == "list":
                    print(allplayers)
                else:
                    exec(input_msg)
            except Exception as err:
                errmsg = "控制台执行命令线程报错, 信息:\n"+str(err)
                color("§c"+traceback.format_exc(), info = "§c 错误 ")
                log("§c" + errmsg, sendtogamewithERROR = True, info = "§c 错误 ")



    """""""""""
    CLASS PART
    """""""""""
    class PluginSkip(Exception):
        pass


    constChangeLock = threading.Lock()
    class _const():
        def __init__(self):
            object.__setattr__(self, "__dict_hidden__", {})
            object.__setattr__(self, "__dict_hidden2__", {})

        def __setattr__(self, key, value):
            for i in [self, const, const2]:
                if key in object.__getattribute__(i, "__dict_hidden__"):
                    raise Exception("You can not change a const variable.")
            constChangeLock.acquire()
            object.__getattribute__(const, "__dict_hidden__").update({key: value})
            object.__getattribute__(const, "__dict_hidden2__").update({key: value})
            object.__getattribute__(const2, "__dict_hidden__").update({key: value})
            object.__getattribute__(const2, "__dict_hidden2__").update({key: value})
            constChangeLock.release()

        def __delattr__(self, key):
            if key in object.__getattribute__(self, "__dict_hidden__"):
                raise Exception("You can not delete a const variable.")
            else:
                raise AttributeError(key)

        def __getattribute__(self, key):
            result = object.__getattribute__(self, "__dict_hidden__")
            if key not in object.__getattribute__(self, "__dict_hidden__"):
                raise KeyError(key)
            return result[key]

        def __dir__(self):
            raise Exception("You can not access this.")
    const = _const()
    const2 = _const()


    class createThread(threading.Thread):
        def __init__(self, name, data = {}, func = "", output = True):
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
                if self.output:
                    color("§e启动线程 %s." % self.name, info = "§e 线程 ")
                if getType(self.func) != "str":
                    self.func(self)
                else:
                    exec("%s(self)" % self.func)
            except Exception as err:
                errmsg = ("线程 %s 报错, 信息:\n" % self.name)+str(err)
                color("§c"+traceback.format_exc(), info = "§c 错误 ")
                log("§c" + errmsg, sendtogamewithERROR = True, info = "§c 错误 ")
            except SystemExit as err:
                pass
                # color("§eThread %s has been terminated forcely." % self.name)
            finally:
                if self.output:
                    color("§e终止线程 %s." % self.name, info = "§e 线程 ")
                threadList.remove(self)

        def get_id(self):
            if hasattr(self, '_thread_id'):
                return self._thread_id
            for id, thread in threading._active.items():
                if thread is self:
                    return id

        def stop(self):
            self.stopping = True
            # color("§eTerminating thread %s." % self.name)
            thread_id = self.get_id()
            res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, ctypes.py_object(SystemExit))
            if res > 1:
                ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
                color("§c终止线程失败", info = "§c 错误 ")


    pluginList = []
    class plugin():
        def __init__(self, pluginName, pluginCode):
            self.pluginName = pluginName
            self.pluginCode = pluginCode
            self.enable = True
            self.globals = globals()
            self.locals = {}
            pluginList.append(self)


    """""""""""""""
      RUNNING PART
    """""""""""""""
    if __name__ == "__main__":
        version = "v0.10.7" # 设置版本号
        timeStartRun = time.time() # 记录启动时间
        FBip = "127.0.0.1"
        FBport = 8000
        if os.path.isfile("robotOld.exe"):
            os.remove("robotOld.exe")
        if os.path.isfile("robotNew.exe"):
            os.remove("robotNew.exe")
        faststart = getStatus("faststart")
        if faststart == "获取失败":
            faststart = ""
        if not faststart:
            pass

        # color(title4)
        color('§b".命令"系统社区版§e[Lite]§b\n".Dot" Command System Community Lite(DotCS)\n社区版及其自带插件作者: 7912, Lite开发: SuperScript', info = "§b 信息 ")
        color("833303126")
        color('§b用户交流群: §e833303126', info = "§b 信息 ")

        # 检测fbtoken文件
        if "fbtoken" not in os.listdir():
            color("§c请下载fbtoken, 放进文件夹后重启.", info = "§c WARN ")
            color("§ctoken获取: FastBuilder官网: http://uc.fastbuilder.pro", info = "§c WARN ")
            exitChatbarMenu(delay = 60, reason = "§c请下载fbtoken, 放进目录后重启.")

        color("FastBuilder 连接地址: %s:%d" % (FBip, FBport), info = " 信息 ")

        # 如果租赁服号未设置, 则请求输入租赁服号并存入server.txt
        color("§e正在读取租赁服配置信息.", info = "§e 加载 ")
        if not os.path.isfile("server.txt"):
            json.dump({"code": "0", "password": "0"}, open("server.txt", "w", encoding = "utf-8"), indent = 4, ensure_ascii = True, sort_keys = True)
        serverConfig = json.load(open("server.txt", "r", encoding = "utf-8"))
        try:
            server, serverPassword = str(serverConfig["code"]), str(serverConfig["password"])
        except:
            json.dump({"code": "0", "password": "0"}, open("server.txt", "w", encoding = "utf-8"), indent = 4, ensure_ascii = True, sort_keys = True)
            server, serverPassword = "0", "0"
        json.dump({"code": server, "password": serverPassword}, open("server.txt", "w", encoding = "utf-8"), indent = 4, ensure_ascii = True, sort_keys = True)
        if server == "0":
            server = input("请输入您的租赁服服务器号: ")
            json.dump({"code": server, "password": serverPassword}, open("server.txt", "w", encoding = "utf-8"), indent = 4, ensure_ascii = True, sort_keys = True)
        if serverPassword == "0":
            serverPassword = input("请输入您服务器的密码[没有请直接按回车]: ")
            if not serverPassword:
                serverPassword = "7912"
            json.dump({"code": server, "password": serverPassword}, open("server.txt", "w", encoding = "utf-8"), indent = 4, ensure_ascii = True, sort_keys = True)

        FBkill()
        updateCheck()

        # 加载插件
        # if "获取玩家手持物品.py" in os.listdir("plugin"):
        #     os.remove("plugin/获取玩家手持物品.py")
        # if getStatus("pluginupdate1") != "update":
        #     fileDownload("http://www.dotcs.community/update/获取玩家手持物品或装备.py", "plugin/获取玩家手持物品或装备.py")
        #     setStatus("pluginupdate1", "update")

        
        color("§e正在加载插件.", info = "§e 加载 ")
        color("§e[总进度 1/2] 正在读取插件.", info = "§e 加载 ")
        if not _root.DefColor:
            def color(*_, **__):pass
        if os.listdir("plugin") == []:
            color("x167c请在plugin文件夹放入插件.", info = "§c 提示 ")
            exitChatbarMenu(delay = 20, reason = "请在plugin文件夹放入插件.")
            
        if not os.path.isfile(_root.fbname):
            for i in os.listdir():
                if (i.startswith("phoenixbuilder") or i.startswith("fastbuilder")) and i.endswith(".exe"):
                    os.rename(i, _root.fbname)
        if not os.path.isfile(_root.fbname):        
                color("§c请下载PhoenixBuilder到该文件夹", info = "§c 提示 ")
                exitChatbarMenu(delay = 20, reason = "请下载PhoenixBuilder到该文件夹")
    
        pluginlist = []
        for filename in os.listdir("plugin"):
            if filename.endswith(".py") or filename.endswith(".py.enc"):
                pluginlist.append(filename)

        for i in range(len(pluginlist)):
            filename = pluginlist[i]
            color("§e[总进度 1/2][插件 %d/%d] 加载插件: %s" % (i+1, len(pluginlist), filename), replace = True, replaceByNext = True, info = "§e 加载 ")
            with open("plugin/"+filename, "rb") as file:
                if filename.endswith(".py.enc"):
                    pluginCode = TDES.decrypt(file.read(), "DotCS Community plugin.", False)
                else:
                    pluginCode = file.read()
                pluginCodeList = pluginCode.decode("utf-8").replace("\r", "").split("# PLUGIN TYPE: ")[1:]
                pluginCodeDict = {}
                for i in pluginCodeList:
                    pluginCodeDict[i.split("\n", 1)[0]] = i.split("\n", 1)[1]
                plugin(filename, pluginCodeDict)
        del pluginlist, pluginCode, pluginCodeList, pluginCodeDict

        color("§e[总进度 2/2] 正在执行 def 类型插件.", info = "§e 加载 ")
        pluginRunType = "def"
        pluginIndex = 0
        i: plugin
        for i in pluginList:
            pluginIndex += 1
            color("§e[总进度 2/2][插件 %d/%d] 执行插件: %s" % (pluginIndex, len(pluginList), i.pluginName), replace = True, replaceByNext = True, info = "§e 加载 ")
            try:
                if i.enable and pluginRunType in i.pluginCode:
                    exec(i.pluginCode[pluginRunType])
            except Exception as err:
                errmsg = "插件 %s %s 报错, 信息:\n%s" % (i.pluginName, pluginRunType, str(err))
                color("§c"+traceback.format_exc(), info = "§c 错误 ")
                log("§c" + errmsg, sendtogamewithERROR = True, info = "§c 错误 ")
                exitChatbarMenu(delay = 60, reason = "加载插件: %s 类型: %s 失败, 插件报错." % (i.pluginName, pluginRunType))
                
        color = Color.colorSet
                
        color("§a成功加载所有插件.", info = "§a 成功 ")

        # 启动FastBuilder并等待连接.
        runFB()
        timeStartFBRun = time.time()
        color("§e正在等待 FastBuilder 连接到租赁服 %s." % server, info = "§e 加载 ")
        createThread("控制台执行命令", data = {}, func = consoleInput)
        createThread("收取数据包", data = {}, func = revPacket)
        createThread("检测命令系统更新并校准在线玩家", data = {}, func = othersRepeat)

        while not exiting:
            time.sleep(0.1)

        sys.exit()


except SystemExit:
    try:
        if exitReason is None:
            color("§e正在退出, 请稍等.", info = "§e 退出 ")
        else:
            color("§e正在退出, 原因: %s" % str(exitReason), info = "§e 退出 ")
        color("§e正在终止子线程.", info = "§e 线程 ")
        startTime = time.time()
        while threadList and time.time() - startTime < 10:
            for i in threadList[:]:
                i.stop()
            time.sleep(1)
        if connected:
            conn.ReleaseConnByID(connID)
            time.sleep(0.5)
        if exitDelay != 0:
            countdown(exitDelay, "§e正在退出")
    except:
        pass
    finally:
        try:
            FBkill()
        except:
            pass
        threadNum = len(threadList)
        if threadNum >= 1:
            color("§c强制退出命令系统, %d 个线程还未被终止:" % threadNum, info = "§c 错误 ")
            for i in range(len(threadList)):
                color("§c%d. %s" % (i+1, threadList[i].name), info = "§c 错误 ")
        elif threadNum == 0:
            color("§a正常退出.", info = "§a 信息 ")


except:
    try:
        if not connected:
            color("§c"+traceback.format_exc(), info = "§c 错误 ")
        if exitReason is None:
            color("§e正在退出, 请稍等.", info = "§e 退出 ")
        else:
            color("§e正在退出, 原因: %s" % str(exitReason), info = "§e 退出 ")
        color("§e正在终止子线程.", info = "§e 线程 ")
        startTime = time.time()
        while threadList and time.time() - startTime < 10:
            for i in threadList[:]:
                i.stop()
            time.sleep(1)
        if connected:
            conn.ReleaseConnByID(connID)
            time.sleep(0.5)
        if exitDelay != 0:
            countdown(exitDelay, "§e正在退出")
    except:
        pass
    finally:
        try:
            FBkill()
        except:
            pass
        threadNum = len(threadList)
        if threadNum >= 1:
            color("§c强制退出命令系统, %d 个线程还未被终止:" % threadNum, info = "§c 错误 ")
            for i in range(len(threadList)):
                color("§c%d. %s" % (i+1, threadList[i].name), info = "§c 错误 ")
        elif threadNum == 0:
            color("§a正常退出.", info = "§a 信息 ")
