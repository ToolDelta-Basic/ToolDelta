import dotcs_libs.color_print
from dotcs_libs.basic_mods import *
from dotcs_libs.plugin_load import Plugin, PluginAPI, PluginGroup
from dotcs_libs.packets import Packet_CommandOutput
from dotcs_libs.cfg import Cfg
from dotcs_libs import old_dotcs_env
from dotcs_libs import conn

Print = dotcs_libs.color_print.Print()

class Frame:
    class ThreadExit(SystemExit):...
    class FrameBasic:
        max_connect_fb_time = 60
        connect_fb_start_time = time.time()
    class ClassicThread(threading.Thread):
        def __init__(this, func: Callable, args: tuple = (), **kwargs):
            super().__init__(target = func)
            this.func = func
            this.daemon = True
            this.all_args = [args, kwargs]
            this.start()

        def run(this):
            try:
                this.func(*this.all_args[0], **this.all_args[1])
            except Frame.ThreadExit:
                pass
            except Exception as err:
                traceback.print_exc()

        def get_id(this):
            if hasattr(this, '_thread_id'):
                return this._thread_id
            for id, thread in threading._active.items():
                if thread is this:
                    return id
                
        def stop(this):
            res = ctypes.pythonapi.PyThreadState_SetAsyncExc(this.get_id(), ctypes.py_object(Frame.ThreadExit))
            return res

    MAX_PACKET_CACHE = 500
    sys_data = FrameBasic()
    con: int
    conPort: int = 8080
    serverNumber: str = "48285363"
    serverPasswd: int
    consoleMenu = []
    link_game_ctrl = None
    link_plugin_group = None
    use_nohup = False
    fb_pipe: subprocess.Popen = None
    _old_dotcs_threadinglist = []
    status = 0

    def read_cfg(this):
        Cfg.default_cfg("租赁服登录配置.json", Cfg.default_server_login)
        try:
            cfgs = Cfg.get_cfg("租赁服登录配置.json", Cfg.std_server_login)
            this.serverNumber = str(cfgs["服务器号"])
            this.serverPasswd = cfgs["密码"]
        except:
            Print.print_err("租赁服登录配置有误， 需要更正")
            exit()
        if this.serverNumber == "0":
            while 1:
                try:
                    this.serverNumber = input(Print.fmt_info("请输入租赁服号: ", "§b 输入 "))
                    this.serverPasswd = input(Print.fmt_info("请输入租赁服密码(没有请直接回车): ", "§b 输入 ")) or "0"
                    std = Cfg.default_server_login
                    std["服务器号"] = int(this.serverNumber)
                    std["密码"] = int(this.serverPasswd)
                    cfgs = Cfg.default_cfg("租赁服登录配置.json", std, True)
                    Print.print_suc("登录配置设置成功")
                    break
                except:
                    Print.print_err("输入有误， 租赁服号和密码应当是纯数字")

    def welcome(this):
        Print.print_with_info("§dDotCS - Panel Pro Embed By SuperScript", "§d 加载 ")
        Print.print_with_info("§dDotCS - Linux 已启动", "§d 加载 ")

    def basicMkDir(this):
        os.makedirs("DotCS原版插件", exist_ok=True)
        os.makedirs("DotCS新版插件", exist_ok=True)
        os.makedirs("DotCS无OP运行组件", exist_ok=True)
        os.makedirs("status", exist_ok=True)
        os.makedirs("data/status", exist_ok=True)
        os.makedirs("data/player", exist_ok=True)

    def runFB(this, ip = "0.0.0.0", port="8080"):
        if not this.use_nohup:
            con_cmd = f"fastbuilder --no-readline --no-update-check --listen-external {ip}:{port} -c {this.serverNumber} {f'-p {this.serverPasswd}' if this.serverPasswd else ''}"
            this.fb_pipe = subprocess.Popen(con_cmd,  stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
            Print.print_suc("FastBuilder 进程已启动.")
        else:
            threading.Thread(target=os.system, args=(f"nohup fastbuilder --no-readline --no-update-check --listen-external {ip}:{port} -c {this.serverNumber}",)).start()
    
    def close_fb_thread(this):
        if this.use_nohup:
            kill_succ = 0
            for proc in psutil.process_iter():
                proc_name = proc.name()
                if "fastbuilder" in proc_name or "phoenixbuilder" in proc_name:
                    proc.kill()
                    kill_succ = 1
            if kill_succ:
                Print.print_suc("§a成功关闭FB进程")
        else:
            this.fb_pipe.kill()
            Print.print_suc("§a成功关闭FB进程")
                
    def set_game_control(this, game_ctrl):
        this.link_game_ctrl = game_ctrl

    def set_plugin_group(this, plug_grp):
        this.link_plugin_group = plug_grp

    def get_game_control(this):
        return this.link_game_ctrl

    def run_conn(this, ip = "0.0.0.0", port="8080"):
        connect_fb_start_time = time.time()
        while 1:
            try:
                this.con = conn.ConnectFB(ip + ":" + port)
                Print.print_suc("§a成功连接上FastBuilder.")
                return 1
            except:
                if time.time() - connect_fb_start_time > this.sys_data.max_connect_fb_time:
                    Print.print_err(f"§4{this.sys_data.max_connect_fb_time}秒内未连接上FB，已退出")
                    this.close_fb_thread()
                    return 0
                
    def outputFBMsgsThread(this):
        threading.Thread(target=this._outputFBMsgsThread).start()

    def ConsoleCmd_thread(this):
        threading.Thread(target=this._console_cmd_thread).start()

    def add_console_cmd_trigger(this, triggers: list[str], usage: str, func: Callable[[list[str]], None]):
        try:
            if this.consoleMenu.index(triggers) != -1:
                Print.print_war(f"§6后台指令关键词冲突: {func}, 不予添加至指令菜单")
        except:
            this.consoleMenu.append([usage, func, triggers])

    def init_basic_help_menu(this, cmd):
        menu = this.get_console_menus()
        Print.print_inf("§a以下是可选的菜单指令项：")
        for k in menu:
            Print.print_inf(f" §f{' / '.join(k[2])}  §7->  {k[0]}")

    def get_console_menus(this):
        return this.consoleMenu

    def _console_cmd_thread(this):
        this.add_console_cmd_trigger(["?", "help", "帮助"], "查询可用菜单指令", this.init_basic_help_menu)
        while 1:
            rsp = input()
            if this.status == 2 or this.status == 3:
                break
            for k in this.consoleMenu:
                if not rsp:
                    continue
                elif rsp.split()[0] in k[2]:
                    res = this._try_execute_console_cmd(k[1], rsp, 0, None)
                    if res == -1:
                        return
                else:
                    for tri in k[2]:
                        if rsp.startswith(tri):
                            res = this._try_execute_console_cmd(k[1], rsp, 1, tri)
                            if res == -1:
                                return

    def _try_execute_console_cmd(this, func, rsp, mode, arg1):
        try:
            if mode == 0:
                rsp_arg = rsp.split()[1:]
            elif mode == 1:
                rsp_arg = rsp[len(arg1):].split()
        except IndexError:
            Print.print_err("[控制台执行命令] 指令缺少参数")
        try:
            func(rsp_arg)
            return 1
        except Exception as err:
            if "id 0 out of range 0" in str(err):
                return -1
            Print.print_err(f"控制台指令出错： {err}")
            return 0

    def _outputFBMsgsThread(this):
        if this.use_nohup:
            with open("nohup.out", "w", encoding='utf-8') as f:
                f.close()
        while 1:
            if this.use_nohup:
                # 弃用
                time.sleep(1)
                with open("nohup.out", "r", encoding='utf-8') as f:
                    tmps = f.read()
                    f.close()
                if tmps:
                    if "租赁服未找到" in tmps and "ERROR" in tmps:
                        Print.print_err(f"§c租赁服号: {this.serverNumber} 未找到, 有可能是租赁服关闭中, 或是设置了等级或密码")
                    elif "租赁服号尚未授权" in tmp and "ERROR" in tmps:
                        Print.print_err(f"§c租赁服号: {this.serverNumber} ，你还没有该服务器号的卡槽， 请前往用户中心购买")
                    elif "https://github.com/LNSSPsd/PhoenixBuilder" in tmps:
                        Print.print_with_info(tmps.split("\n")[3], "§b  FB  ")
                    elif "Transfer: accept new connection @ " in tmps:
                        Print.print_with_info("FastBuilder 监听端口已开放", "§b  FB  ")
                    else:
                        for tmp in tmps.split("\n"): 
                            if not tmp:
                                continue
                            Print.print_with_info(tmp, "§b  FB  §r")
                    with open("nohup.out", "w", encoding='utf-8') as _f:
                        _f.close()
            else:
                tmp = this.fb_pipe.stdout.readline().decode("utf-8").strip("\n")
                if not tmp:
                    continue
                elif "ERROR" in tmp:
                    if "租赁服未找到" in tmp:
                        Print.print_err(f"§c租赁服号: {this.serverNumber} 未找到, 有可能是租赁服关闭中, 或是设置了等级或密码")
                    elif "租赁服号尚未授权" in tmp:
                        Print.print_err(f"§c租赁服号: {this.serverNumber} ，你还没有该服务器号的卡槽， 请前往用户中心购买")
                    elif "bad handshake" in tmp:
                        Print.print_err("§c无法连接到验证服务器, 可能是FB服务器崩溃, 或者是你的IP处于黑名单中")
                        try:
                            Print.print_war("尝试连接到 FastBuilder 验证服务器")
                            requests.get("http://uc.fastbuilder.pro", timeout=10)
                            Print.print_err("??? 未知情况， 有可能只是验证服务器崩溃， 用户中心并没有崩溃")
                        except:
                            Print.print_err("§cFastBuilder服务器无法访问， 请等待修复(加入FastBuilder频道查看详情)")
                            exit()
                    elif "无效用户" in tmp and "请重新登录" in tmp:
                        Print.print_err("§cFastBuilder Token 无法使用， 请重新下载")
                elif "Transfer: accept new connection @ " in tmp:
                    Print.print_with_info("FastBuilder 监听端口已开放: " + tmp.split()[-1], "§b  FB  ")
                elif tmp.startswith("panic"):
                    Print.print_err(f"FastBuilder 出现问题: {tmp[7:]}")
                    thread_processPacket.stop()
                    this.status = 2
                    this.fb_pipe.kill()
                    return
                else:
                    Print.print_with_info(tmp, "§b  FB  §r")

    def reload_plugins(this):...

    # Can custom
    def on_plugin_err(this, pluginName: str, exc: Exception, trace: str):
        Print.print_err(f"§4插件 {pluginName} 报错, 信息：§c\n" + trace)

    def get_on_plugin_err(this):
        return this.on_plugin_err
    
    def _get_old_dotcs_env(this):
        """Create an old dotcs env"""
        return old_dotcs_env.get_dotcs_env(this)

class GameManager:
    command_req = []
    command_resp = {}
    players_uuid = {}
    allplayers = []
    bot_name = ""
    linked_frame: Frame
    pkt_unique_id: int = 0
    pkt_cache: list = []
    require_listen_packet_list = [9, 79, 63]
    store_uuid_pkt = None
    requireUUIDPacket = True

    def __init__(this, frame: Frame):
        this.linked_frame = frame

    def reset(this):
        this.command_req.clear()
        this.command_resp.clear()
        this.players_uuid.clear()
        this.allplayers.clear()
        this.bot_name = ""
        this.linked_frame: Frame
        this.pkt_unique_id: int = 0
        this.pkt_cache.clear()
        this.require_listen_packet_list.clear()
        this.require_listen_packet_list += [9, 79, 63]
        this.store_uuid_pkt.clear()
        this.requireUUIDPacket = True

    def add_listen_pkt(this, pkt_type: int):
        if pkt_type not in this.require_listen_packet_list:
            this.require_listen_packet_list.append(pkt_type)

    def simpleProcessGamePacket(this):
        con = this.linked_frame.con
        plugin_grp = this.linked_frame.link_plugin_group
        this.pkt_unique_id = 0
        try:
            while 1:
                packet_bytes = conn.RecvGamePacket(con)
                packet_type = conn.inspectPacketID(packet_bytes)
                this.pkt_unique_id += 1
                if packet_type not in this.require_listen_packet_list:
                    continue
                else:
                    packetGetTime = time.time()
                    packet_mapping = json.loads(conn.GamePacketBytesAsIsJsonStr(packet_bytes))
                    if packet_type == 79:
                        cmd_uuid = packet_mapping["CommandOrigin"]["UUID"].encode()
                        if cmd_uuid in this.command_req:
                            this.command_resp[cmd_uuid] = [packetGetTime, packet_mapping]
                    elif packet_type == 63:
                        if this.requireUUIDPacket:
                            this.store_uuid_pkt = packet_mapping
                        else:
                            this.processPlayerList(packet_mapping)
                    this.processGamePacketWithPlugin(packet_mapping, packet_type, plugin_grp)
        except Exception as err:
            if "recv on a closed connection" in str(err):
                this.linked_frame.status = 2
                return
            print(traceback.format_exc())

    def processPlayerList(this, pkt):
        for player in pkt["Entries"]:
            isJoining = bool(player["Skin"]["SkinData"])
            playername = player["Username"]
            if isJoining:
                this.players_uuid[playername] = player["UUID"]
                this.allplayers.append(playername) if not playername in this.allplayers else None
                Print.print_inf(f"§e{playername} 加入了游戏")
            else:
                playername = "???"
                for k in this.players_uuid:
                    if this.players_uuid[k] == player["UUID"]:
                        playername = k
                        break
                this.allplayers.remove(playername) if playername != "???" else None
                Print.print_inf(f"§e{playername} 退出了游戏")

    def processGamePacketWithPlugin(this, pkt: dict, pkt_type: int, plugin_grp: PluginGroup):
        if pkt_type == 9: 
            match pkt['TextType']:
                case 2:
                    if pkt['Message'] == "§e%multiplayer.player.joined":
                        player = pkt["Parameters"][0]
                        plugin_grp.execute_player_prejoin(player, this.linked_frame.get_on_plugin_err())
                    if pkt['Message'] == "§e%multiplayer.player.join":
                        player = pkt["Parameters"][0]
                        plugin_grp.execute_player_join(player, this.linked_frame.get_on_plugin_err())
                    elif pkt['Message'] == "§e%multiplayer.player.left":
                        player = pkt["Parameters"][0]
                        plugin_grp.execute_player_leave(player, this.linked_frame.get_on_plugin_err())
                    elif pkt['Message'].startswith("death."):
                        Print.print_inf(f"{pkt['Parameters'][0]} 失败了: {pkt['Message']}")
                        if len(pkt["Parameters"]) >= 2:
                            killer = pkt["Parameters"][1]
                        else:
                            killer = None
                        plugin_grp.execute_player_death(pkt['Parameters'][0], killer, pkt['Message'], this.linked_frame.get_on_plugin_err())
                case 1 | 7:
                    player, msg = pkt['SourceName'], pkt['Message']
                    plugin_grp.execute_player_message(player, msg, this.linked_frame.get_on_plugin_err())
                    Print.print_inf(f"<{player}> {msg}")
                case 8:
                    player, msg = pkt['SourceName'], pkt['Message']
                    Print.print_inf(f"{player} say -> {msg.strip(f'[{player}]')}")
                    plugin_grp.execute_player_message(player, msg, this.linked_frame.get_on_plugin_err())
                case 9:
                    msg = pkt['Message'].strip('{"rawtext":[{"text":"').strip("\n").strip('"}]}')
                    Print.print_inf(f"{msg}")
                    
        if pkt_type in plugin_grp.listen_packets:
            this.pkt_cache.append([pkt_type, pkt])

    def threadPacketProcessFunc(this):
        while 1:
            lastPTime = 0
            if this.pkt_cache:
                typ, pkt = this.pkt_cache.pop(0)
                plugin_group.processPacketFunc(typ, pkt)
            if len(this.pkt_cache) > 100 and time.time() - lastPTime > 5:
                Print.print_war("数据包缓冲区量 > 100")
                lastPTime = time.time()
            elif len(this.pkt_cache) > this.linked_frame.MAX_PACKET_CACHE:
                Print.print_err(f"数据包缓冲区量 > {this.linked_frame.MAX_PACKET_CACHE} 超最大阈值， 已清空缓存区")
                this.pkt_cache.clear()

    def dotcs_joingame_init(this):
        startDetTime = time.time()
        while not this.store_uuid_pkt and time.time() - startDetTime < 10:pass
        if not this.store_uuid_pkt:
            this.linked_frame.status = 2
            Print.print_err("未收取到UUID包， 重启DotCS")
            exit()
            return
        else:
            this.processPlayerList(this.store_uuid_pkt)
            this.requireUUIDPacket = False
        Print.print_suc("初始化完成, 在线玩家: " + ", ".join(this.allplayers))
        this.linked_frame.status = 1
            
    def waitUntilProcess(this):
        this.requireUUIDPacket = True
        this.allplayers.clear()
        this.players_uuid.clear()
        while this.pkt_unique_id == 0:pass

    def clearCmdRespList(this):
        while 1:
            time.sleep(3)
            for k in this.command_resp.copy():
                if time.time() - this.command_resp[k][0] > 10:
                    del this.command_resp[k]

    def tps_thread(this):
        "not archieved"
        return
        lastGameTime = int(this.sendcmd("time query daytime", True, 10).OutputMessages[0].Parameters[0])
        while 1:
            try:
                st_time = time.time()
                tps = int(this.sendcmd("time query gametime", True, 10).OutputMessages[0].Parameters[0])
                st_time = time.time() - st_time
                lastGameTime = tps
            except Exception as err:
                pass
            time.sleep(10)

    def sendwocmd(this, cmd: str):
        conn.SendNoResponseCommand(this.linked_frame.con, cmd)

    def sendcmd(this, cmd: str, waitForResp: bool = False, timeout: int = 30):
        uuid = conn.SendMCCommand(this.linked_frame.con, cmd)
        if waitForResp:
            this.command_req.append(uuid)
            waitStartTime = time.time()
            while 1:
                res = this.command_resp.get(uuid, None)
                if res:
                    this.command_req.remove(uuid)
                    del this.command_resp[uuid]
                    return Packet_CommandOutput(res[1])
                elif time.time() - waitStartTime > timeout:
                    this.command_req.remove(uuid)
                    raise TimeoutError(1, "指令返回获取超时")
        else:
            return uuid
        
    def sendwscmd(this, cmd: str, waitForResp: bool = False, timeout: int = 30):
        uuid = conn.SendWSCommand(this.linked_frame.con, cmd)
        if waitForResp:
            this.command_req.append(uuid)
            waitStartTime = time.time()
            while 1:
                res = this.command_resp.get(uuid, None)
                if res:
                    this.command_req.remove(uuid)
                    del this.command_resp[uuid]
                    return Packet_CommandOutput(res[1])
                elif time.time() - waitStartTime > timeout:
                    this.command_req.remove(uuid)
                    raise TimeoutError(1, "指令返回获取超时")
        else:
            return uuid
        
    def sendfbcmd(this, cmd: str):
        conn.SendFBCommand(this.linked_frame.con, cmd)

    def sendPacket(this, pktType: int, pkt: dict):
        b = conn.JsonStrAsIsGamePacketBytes(pktType, json.dumps(pkt))
        conn.SendGamePacketBytes(this.linked_frame.con, b)
        
    def say_to(this, target: str, msg: str):
        this.sendwocmd("tellraw " + target + ' {"rawtext":[{"text":"' + msg + '"}]}')

    def player_title(this, target: str, text: str):
        this.sendwocmd(f"title {target} title {text}")

    def player_subtitle(this, target: str, text: str):
        this.sendwocmd(f"title {target} subtitle {text}")

    def player_actionbar(this, target: str, text: str):
        this.sendwocmd(f"title {target} actionbar {text}")

try:
    frame = Frame()
    plugin_group = PluginGroup(frame)
    game_manager = GameManager(frame)
    frame.set_game_control(game_manager)
    frame.set_plugin_group(plugin_group)
    frame.welcome()
    frame.basicMkDir()
    frame.read_cfg()
    plugin_group.read_plugin_from_old(dotcs_module_env)
    plugin_group.read_plugin_from_new(globals())
    plugin_group.execute_def(frame.get_on_plugin_err())
    frame.ConsoleCmd_thread()
    while 1:
        if frame.status in [0, 2]:
            frame.runFB(port=str(frame.conPort))
            frame.outputFBMsgsThread()
            frame.run_conn(port=str(frame.conPort))
            thread_processPacket = Frame.ClassicThread(game_manager.simpleProcessGamePacket)
            game_manager.waitUntilProcess()
            thread_processPacketFunc = Frame.ClassicThread(game_manager.threadPacketProcessFunc)
            threading.Thread(target=game_manager.tps_thread).start()
            game_manager.dotcs_joingame_init()
        plugin_group.execute_init(frame.get_on_plugin_err())
        frame.status = 1
        while frame.status == 1:
            continue
        thread_processPacket.stop()
        thread_processPacketFunc.stop()
        if frame.status == 0:
            break
        elif frame.status == 2:
            Print.print_war("FB断开连接， 尝试重启")
        elif frame.status == 11:
            Print.print_war("开始重载插件 (注意: 这是不安全的做法)")
            time.sleep(0.1)
            plugin_group.reset()
            game_manager.reset()
            frame.consoleMenu.clear()
            frame.set_game_control(game_manager)
            frame.set_plugin_group(plugin_group)
            plugin_group.read_plugin_from_old(dotcs_module_env)
            plugin_group.read_plugin_from_new(globals())
            plugin_group.execute_def(frame.get_on_plugin_err())

except KeyboardInterrupt:
    Print.print_suc("正在退出.")

except Exception:
    traceback.print_exc()
    frame.close_fb_thread()
    os._exit(0)