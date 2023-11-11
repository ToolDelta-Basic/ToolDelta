#!/usr/bin/python3
# for install libs in debug mode;
import libs.get_python_libs
# start
import libs.color_print
import libs.sys_args
import libs.old_dotcs_env
import libs.builtins
import libs.rich_color_print
import libs.color_print
from libs.basic_mods import *
from libs.plugin_load import Plugin, PluginAPI, PluginGroup
from libs.packets import Packet_CommandOutput
from libs.cfg import Cfg as _Cfg
from libs.logger import publicLogger

PRG_NAME = "ToolDelta"
UPDATE_NOTE = ""
ADVANCED = False
Builtins = libs.builtins.Builtins
Config = _Cfg()
Print = libs.color_print.Print
async_loop = asyncio.new_event_loop()
sys_args_dict = libs.sys_args.SysArgsToDict(sys.argv)

Print.print_with_info("§d系统正在启动..", "§d 加载 ")

try:
    VERSION = tuple(int(v) for v in open("version","r", encoding = "utf-8").read().strip()[1:].split('.'))
except:
    # Current version
    VERSION = (0, 2, 0)

def set_output_mode():
    global Print
    if not Config.exists(os.path.join("data","输出模式.json")):
        Config.default_cfg(os.path.join("data","输出模式.json"), {"mode": 0})
    outputMode = Config.get_cfg(os.path.join("data","输出模式.json"), {"mode": int})
    if outputMode["mode"] == 0:
        Print.print_inf("在配置文件(data/输出模式.json)内可更改输出模式")
        Print.print_inf("[普通=1, rich=2] (修改了该配置后此条信息不再显示)")
    if outputMode["mode"] == 2:
        Print = libs.rich_color_print.Print
    else:
        Print = libs.color_print.Print
    del outputMode

def import_proxy_lib():
    global conn
    try:
        import libs.conn as conn
    except Exception as err:
        Print.print_err(f"加载外部库失败， 请检查其是否存在:{err}")
        raise SystemExit

class SysStatus:
    LAUNCHING = 0
    RUNNING = 1
    NORMAL_EXIT = 2
    FB_LAUNCH_EXC = 3
    FB_CRASHED = 4
    NEED_RESTART = 5

class Frame:
    class ThreadExit(SystemExit):...
    class SystemVersionException(OSError):...
    class FrameBasic:
        system_version = VERSION
        max_connect_fb_time = 60
        connect_fb_start_time = time.time()
        data_path = "data/"
    class ClassicThread(threading.Thread):
        def __init__(self, func: Callable, args: tuple = (), usage = "", **kwargs):
            super().__init__(target = func)
            self.func = func
            self.daemon = True
            self.all_args = [args, kwargs]
            self.usage = usage
            self.start()

        def run(self):
            try:
                self.func(*self.all_args[0], **self.all_args[1])
            except Frame.ThreadExit:
                pass
            except Exception as err:
                Print.print_err(traceback.format_exc())
                if self.usage == "fbconn":
                    frame.status = SysStatus.FB_CRASHED
                    return
                else:
                    Print.print_err(traceback.format_exc())

        def get_id(self):
            if hasattr(self, '_thread_id'):
                return self._thread_id
            for id, thread in threading._active.items():
                if thread is self:
                    return id
                
        def stop(self):
            res = ctypes.pythonapi.PyThreadState_SetAsyncExc(self.get_id(), ctypes.py_object(Frame.ThreadExit))
            return res
        
    PRG_NAME = PRG_NAME
    MAX_PACKET_CACHE = 500
    sys_data = FrameBasic()
    con: int
    conPort: int = 8080
    serverNumber: str = ""
    serverPasswd: int
    consoleMenu = []
    link_game_ctrl = None
    link_plugin_group = None
    fb_pipe: subprocess.Popen | None = None
    _old_dotcs_threadinglist = []
    status = SysStatus.LAUNCHING
    on_plugin_err = lambda _, *args, **kwargs: libs.builtins.on_plugin_err_common(*args, **kwargs)
    system_is_win = sys.platform in ["win32", "win64"]
    isInPanicMode = False
    UseSysFBtoken = False
    external_port = sys_args_dict.get("external-port")

    def check_use_token(self, tok_name = "", check_md = ""):
        res = libs.sys_args.SysArgsToDict(sys.argv)
        res = res.get(tok_name, 1)
        if (res == 1 and check_md) or res != check_md:
            Print.print_err(f"启动参数错误")
            raise SystemExit
        
    @staticmethod
    def download_file(f_url: str, f_dir: str):
        res = requests.get(f_url, stream = True)
        filesize = int(res.headers["content-length"])
        nowsize = 0
        succ = False
        try:
            with open(f_dir + ".tmp", "wb") as dwnf:
                for chk in res.iter_content(chunk_size = 1024):
                    prgs = nowsize / filesize
                    _tmp = int(prgs * 20)
                    bar = Print.colormode_replace("§f" + " " * _tmp + "§b" + " " * (20 - _tmp) + "§r", 7)
                    Print.print_with_info(f"{bar} {round(nowsize / 1024, 2)}KB / {round(filesize / 1024, 2)}KB", "§a 下载 §r", end = "\r")
                    nowsize += len(chk)
                    if chk: dwnf.write(chk)
            succ = True
        finally:
            if succ:
                os.rename(f_dir + ".tmp", f_dir)
            else:
                os.remove(f_dir + ".tmp")

    def downloadMissingFiles(self):
        mirror_src = "https://mirror.ghproxy.com/"
        file_get_src = mirror_src + "https://raw.githubusercontent.com/SuperScript-PRC/ToolDelta/main/require_files.json"
        try:
            files_to_get = json.loads(requests.get(file_get_src).text)
        except json.JSONDecodeError:
            Print.print_err("自动下载缺失文件失败: 文件源 JSON 不合法")
            sys.exit(0)
        except requests.Timeout:
            Print.print_err(f"自动下载缺失文件失败: URL 请求出现问题: 请求超时")
            sys.exit(0)
        except Exception as err:
            Print.print_err(f"自动下载缺失文件失败: URL 请求出现问题: {err}")
            sys.exit(0)
        try:
            Print.print_with_info(f"§d将自动检测缺失文件并补全","§d 加载 ")
            mirrs = files_to_get["Mirror"]
            download_mode = "Windows" if self.system_is_win else "Linux"
            files = files_to_get[download_mode]
            for fdir, furl in files.items():
                if not os.path.isfile(fdir):
                    Print.print_inf(f"文件: <{fdir}> 缺失, 正在下载..")
                    succ = False
                    for mirr in mirrs:
                        try:
                            self.download_file(mirr + "/https://github.com/" + furl, fdir)
                            succ = True
                            break
                        except requests.exceptions.RequestException:
                            Print.print_war("镜像源故障, 正在切换")
                            pass
                    if not succ:
                        Print.print_err("镜像源全不可用..")
                        raise SystemExit
                    Print.print_inf(f"文件: <{fdir}> 下载完成")
        except requests.Timeout:
            Print.print_err(f"自动检测文件并补全时出现错误: 超时, 自动跳过")
        except Exception as err:
            Print.print_err(f"自动检测文件并补全时出现错误: {err}")
            raise SystemExit
        return True

    def read_cfg(self):
        CFG = {
            "服务器号": 0,
            "密码": 0,
            "主动获取UUID": False,
        }
        CFG_STD = {
            "服务器号": int,
            "密码": int,
            "主动获取UUID": bool,
        }
        if not os.path.isfile("fbtoken"):
            Print.print_err("请到FB官网 user.fastbuilder.pro 下载FBToken, 并放在本目录中")
            raise SystemExit
        Config.default_cfg("租赁服登录配置.json", CFG)
        try:
            cfgs = Config.get_cfg("租赁服登录配置.json", CFG_STD)
            self.serverNumber = str(cfgs["服务器号"])
            self.serverPasswd = cfgs["密码"]
            self.server_cfgs = cfgs
        except Config.ConfigError:
            Print.print_err("租赁服登录配置有误， 需要更正")
            exit()
        if self.serverNumber == "0":
            while 1:
                try:
                    self.serverNumber = input(Print.fmt_info("请输入租赁服号: ", "§b 输入 "))
                    self.serverPasswd = input(Print.fmt_info("请输入租赁服密码(没有请直接回车): ", "§b 输入 ")) or "0"
                    std = CFG.copy()
                    std["服务器号"] = int(self.serverNumber)
                    std["密码"] = int(self.serverPasswd)
                    cfgs = Config.default_cfg("租赁服登录配置.json", std, True)
                    Print.print_suc("登录配置设置成功")
                    break
                except:
                    Print.print_err("输入有误， 租赁服号和密码应当是纯数字")

    def welcome(self):
        Print.print_with_info(f"§d{PRG_NAME} - Panel Embed By SuperScript", "§d 加载 ")
        Print.print_with_info(f"§d{PRG_NAME} v {'.'.join([str(i) for i in VERSION])}", "§d 加载 ")
        Print.print_with_info(f"§d{PRG_NAME} - Panel 已启动", "§d 加载 ")

    def plugin_load_finished(self, plugins: PluginGroup):
        Print.print_suc(f"成功载入 §f{plugins.normal_plugin_loaded_num}§a 个普通插件, §f{plugins.dotcs_plugin_loaded_num}§a 个DotCS插件")

    def basic_op(self):
        os.makedirs("DotCS兼容插件", exist_ok = True)
        os.makedirs("插件配置文件", exist_ok = True)
        os.makedirs(f"{PRG_NAME}插件", exist_ok = True)
        os.makedirs(f"{PRG_NAME}无OP运行组件", exist_ok = True)
        os.makedirs("status", exist_ok = True)
        os.makedirs("data/status", exist_ok = True)
        os.makedirs("data/players", exist_ok = True)

    def fbtokenFix(self):
        needFix = False
        with open("fbtoken", "r", encoding="utf-8") as f:
            token = f.read()
            if "\n" in token:
                Print.print_war("fbtoken里有换行符， 会造成fb登录失败， 已自动修复")
                needFix = True
        if needFix:
            with open("fbtoken", "w", encoding="utf-8") as f:
                f.write(token.replace("\n", ""))

    def getFreePort(self, start = 8080, usage = "none"):
        if frame.system_is_win:
            for port in range(start, 65535):
                r = os.popen(f"netstat -aon|findstr \":{port}\"", "r")
                if r.read() == '':
                    if usage == "fbconn":
                        self.conPort = port
                        Print.print_suc(f"FastBuilder 将会开放端口 {port}")
                        return
                    else:
                        return port
                else:
                    Print.print_war(f"端口 {port} 正被占用, 跳过")
        else:
                for port in range(start, 65535):
                    r = os.popen(f"netstat -aon|grep \":{port}\"", "r")
                    if r.read() == '':
                        if usage == "fbconn":
                            self.conPort = port
                            Print.print_suc(f"FastBuilder 将会开放端口 {port}")
                            return
                        else:
                            return port
                    else:
                        Print.print_war(f"端口 {port} 正被占用, 跳过")
        raise Exception("未找到空闲端口???")

    def runFB(self, ip = "0.0.0.0", port = 8080):
        if not self.system_is_win:
            os.system("chmod +x phoenixbuilder")
        if frame.downloadMissingFiles():
            if frame.system_is_win:
                if self.UseSysFBtoken:
                    con_cmd = f"phoenixbuilder.exe -T {self.fbtoken} --no-readline --no-update-check --listen-external {ip}:{port} -c {self.serverNumber} {f'-p {self.serverPasswd}' if self.serverPasswd else ''}"
                else:
                    con_cmd = f"phoenixbuilder.exe -t fbtoken --no-readline --no-update-check --listen-external {ip}:{port} -c {self.serverNumber} {f'-p {self.serverPasswd}' if self.serverPasswd else ''}"
            else:
                con_cmd = f"./phoenixbuilder -t fbtoken --no-readline --no-update-check --listen-external {ip}:{port} -c {self.serverNumber} {f'-p {self.serverPasswd}' if self.serverPasswd else ''}"
            self.fb_pipe = subprocess.Popen(con_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                            stderr=subprocess.STDOUT, shell=True)
            Print.print_suc("FastBuilder 进程已启动.")
            frame.outputFBMsgsThread()
        else:
            Print.print_err("download not success, denied")
    
    def close_fb_thread(self):
        try:
            assert self.fb_pipe is not None, "Broken pipe"
            self.fb_pipe.kill()
            Print.print_suc("成功关闭FB进程")
        except:
            Print.print_war("未能正常关闭FB进程")

    def system_exit(self):
        self.link_game_ctrl.say_to("@a", "§6ToolDelta Exit")
        if not self.external_port:
            assert self.fb_pipe is not None and self.fb_pipe.stdin is not None, "连接到FastBuilder的通道出现问题"
            self.fb_pipe.stdin.write("exit\n".encode('utf-8'))
            self.fb_pipe.stdin.flush()
        self.status = SysStatus.NORMAL_EXIT

    def run_conn(self, ip = "0.0.0.0", port = 8080, timeout = None):
        connect_fb_start_time = time.time()
        max_con_time = timeout or self.sys_data.max_connect_fb_time
        while 1:
            try:
                self.con = conn.ConnectFB(f"{ip}:{port}")
                Print.print_suc("§a成功连接上FastBuilder.")
                return 1
            except:
                if time.time() - connect_fb_start_time > max_con_time:
                    Print.print_err(f"§4{max_con_time}秒内未连接上FB，已退出")
                    self.close_fb_thread()
                    os._exit(0)
                elif self.status == SysStatus.FB_LAUNCH_EXC:
                    Print.print_err(f"§4连接FB时出现问题，已退出")
                    self.close_fb_thread()
                    os._exit(0)

    def add_console_cmd_trigger(self, triggers: list[str], arg_hint: str | None, usage: str, func: Callable[[list[str]], None]):
        try:
            if self.consoleMenu.index(triggers) != -1:
                Print.print_war(f"§6后台指令关键词冲突: {func}, 不予添加至指令菜单")
        except:
            self.consoleMenu.append([usage, arg_hint, func, triggers])

    def init_basic_help_menu(self, _):
        menu = self.get_console_menus()
        Print.print_inf("§a以下是可选的菜单指令项：")
        for usage, arg_hint, _, triggers in menu:
            if arg_hint:
                Print.print_inf(f" §e{' 或 '.join(triggers)} {arg_hint}  §f->  {usage}")
            else:
                Print.print_inf(f" §e{' 或 '.join(triggers)}  §f->  {usage}")

    def outputFBMsgsThread(self):
        threading.Thread(target=self._outputFBMsgsThread).start()

    def ConsoleCmd_thread(self):
        threading.Thread(target=self._console_cmd_thread).start()

    def _console_cmd_thread(self):
        self.add_console_cmd_trigger(["?", "help", "帮助"], None, "查询可用菜单指令", self.init_basic_help_menu)
        self.add_console_cmd_trigger(["exit"], None, f"退出并关闭{PRG_NAME}", lambda _: self.system_exit())
        self.add_console_cmd_trigger(["l&j"], None, f"测试玩家退出和进入", lambda p: game_control.test_player_leave_and_join(p[0]))
        try:
            while 1:
                rsp = input()
                if self.status not in [SysStatus.LAUNCHING, SysStatus.RUNNING]:
                    break
                for _, _, func, triggers in self.consoleMenu:
                    if not rsp:
                        continue
                    elif rsp.split()[0] in triggers:
                        res = self._try_execute_console_cmd(func, rsp, 0, None)
                        if res == -1:
                            return
                    else:
                        for tri in triggers:
                            if rsp.startswith(tri):
                                res = self._try_execute_console_cmd(func, rsp, 1, tri)
                                if res == -1:
                                    return
        except EOFError:
            frame.status = SysStatus.NORMAL_EXIT

    def _try_execute_console_cmd(self, func, rsp, mode, arg1):
        try:
            if mode == 0:
                rsp_arg = rsp.split()[1:]
            elif mode == 1:
                rsp_arg = rsp[len(arg1):].split()
        except IndexError:
            Print.print_err("[控制台执行命令] 指令缺少参数")
            return
        try:
            func(rsp_arg)
            return 1
        except Exception as err:
            if "id 0 out of range 0" in str(err):
                return -1
            Print.print_err(f"控制台指令出错： {err}")
            return 0

    def _outputFBMsgsThread(self):
        if self.fb_pipe.returncode:
            self.status = SysStatus.FB_LAUNCH_EXC
            raise "FB启动出现故障"
        while 1:
            assert self.fb_pipe is not None and self.fb_pipe.stdout is not None and self.fb_pipe.stdin is not None, "Broken pipe"
            tmp: str = self.fb_pipe.stdout.readline().decode("utf-8").strip("\n")
            if not tmp:
                continue
            elif " 简体中文" in tmp:
                try:
                    self.fb_pipe.stdin.write(f"{tmp[1]}\n".encode("utf-8"))
                    self.fb_pipe.stdin.flush()
                    Print.print_inf(f"语言已自动选择为简体中文： [{tmp[1]}]")
                except IndexError:
                    Print.print_war(f"未能自动选择为简体中文")
            elif "ERROR" in tmp:
                if "租赁服未找到" in tmp:
                    Print.print_err(f"§c租赁服号: {self.serverNumber} 未找到, 有可能是租赁服关闭中, 或是设置了等级或密码")
                elif "租赁服号尚未授权" in tmp:
                    Print.print_err(f"§c租赁服号: {self.serverNumber} ，你还没有该服务器号的卡槽， 请前往用户中心购买")
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
                Print.print_err(f"FastBuilder 出现问题: {tmp}")
                if not self.isInPanicMode:
                    self.ClassicThread(self.panic_later)
            else:
                Print.print_with_info(tmp, "§b  FB  §r")
            
    def panic_later(self):
        self.isInPanicMode = True
        time.sleep(1)
        self.status = SysStatus.FB_CRASHED
        self.fb_pipe.kill()
        self.isInPanicMode = False
    
    def _get_old_dotcs_env(self):
        """Create an old dotcs env"""
        return libs.old_dotcs_env.get_dotcs_env(self, Print)
    
    def get_console_menus(self):
        return self.consoleMenu
    
    def set_game_control(self, game_ctrl):
        self.link_game_ctrl = game_ctrl

    def set_plugin_group(self, plug_grp):
        self.link_plugin_group = plug_grp

    def get_game_control(self):
        return self.link_game_ctrl
    
    def safe_close(self):
        libs.builtins.safe_close()

class GameCtrl:
    def __init__(self, frame: Frame):
        self.linked_frame = frame
        self.command_req = []
        self.command_resp = {}
        self.players_uuid = {}
        self.allplayers_name = self.allplayers =  []
        self.bot_name = ""
        self.linked_frame: Frame
        self.pkt_unique_id: int = 0
        self.pkt_cache: list = []
        self.require_listen_packet_list = [9, 79, 63]
        self.store_uuid_pkt: dict[str, str] | None = None
        self.requireUUIDPacket = True

    def add_listen_pkt(self, pkt_type: int):
        if pkt_type not in self.require_listen_packet_list:
            self.require_listen_packet_list.append(pkt_type)

    def simpleProcessGamePacket(self):
        con = self.linked_frame.con
        plugin_grp: PluginGroup = self.linked_frame.link_plugin_group
        self.pkt_unique_id = 0
        try:
            while 1:
                packet_bytes = conn.RecvGamePacket(con)
                packet_type = packet_bytes[0]
                self.pkt_unique_id += 1
                if packet_type not in self.require_listen_packet_list:
                    continue
                else:
                    packetGetTime = time.time()
                    packet_mapping = ujson.loads(conn.GamePacketBytesAsIsJsonStr(packet_bytes))
                    if packet_type in plugin_grp.listen_packet_ids:
                        self.pkt_cache.append([packet_type, packet_mapping])
                    if packet_type == 79:
                        cmd_uuid = packet_mapping["CommandOrigin"]["UUID"].encode()
                        for iuuid in self.command_req:
                            if cmd_uuid == iuuid:
                                self.command_resp[iuuid] = [packetGetTime, packet_mapping]
                                break
                    elif packet_type == 63:
                        if self.requireUUIDPacket:
                            self.store_uuid_pkt = packet_mapping
                        else:
                            self.processPlayerList(packet_mapping)
        except Exception:
            self.linked_frame.status = SysStatus.FB_CRASHED
            raise

    def processPlayerList(self, pkt, first = False):
        for player in pkt["Entries"]:
            isJoining = bool(player["Skin"]["SkinData"])
            playername = player["Username"]
            if isJoining:
                self.players_uuid[playername] = player["UUID"]
                self.allplayers.append(playername) if playername not in self.allplayers else None
                if not first:
                    Print.print_inf(f"§e{playername} 加入了游戏, UUID: {player['UUID']}")
                    plugins.execute_player_join(playername, self.linked_frame.on_plugin_err)
                else:
                    self.bot_name = pkt["Entries"][0]["Username"]
            else:
                playername = "???"
                for k in self.players_uuid:
                    if self.players_uuid[k] == player["UUID"]:
                        playername = k
                        break
                self.allplayers.remove(playername) if playername != "???" else None
                Print.print_inf(f"§e{playername} 退出了游戏")

    def processMsgPacketWithPlugin(self, pkt: dict, pkt_type: int, plugin_grp: PluginGroup):
        if pkt_type == 9:
            match pkt['TextType']:
                case 2:
                    if pkt['Message'] == "§e%multiplayer.player.joined":
                        player = pkt["Parameters"][0]
                        plugin_grp.execute_player_prejoin(player, self.linked_frame.on_plugin_err)
                    if pkt['Message'] == "§e%multiplayer.player.join":
                        player = pkt["Parameters"][0]
                    elif pkt['Message'] == "§e%multiplayer.player.left":
                        player = pkt["Parameters"][0]
                        plugin_grp.execute_player_leave(player, self.linked_frame.on_plugin_err)
                    elif pkt['Message'].startswith("death."):
                        Print.print_inf(f"{pkt['Parameters'][0]} 失败了: {pkt['Message']}")
                        if len(pkt["Parameters"]) >= 2:
                            killer = pkt["Parameters"][1]
                        else:
                            killer = None
                        plugin_grp.execute_player_death(pkt['Parameters'][0], killer, pkt['Message'], self.linked_frame.on_plugin_err)
                case 1 | 7:
                    player, msg = pkt['SourceName'], pkt['Message']
                    plugin_grp.execute_player_message(player, msg, self.linked_frame.on_plugin_err)
                    Print.print_inf(f"<{player}> {msg}")
                case 8:
                    player, msg = pkt['SourceName'], pkt['Message']
                    Print.print_inf(f"{player} 使用say说: {msg.strip(f'[{player}]')}")
                    plugin_grp.execute_player_message(player, msg, self.linked_frame.on_plugin_err)
                case 9:
                    msg = pkt['Message']
                    try:
                        Print.print_inf(''.join([i["text"] for i in json.loads(msg)['rawtext']]))
                    except:
                        pass

    def threadPacketProcessFunc(self):
        while 1:
            lastPTime = 0
            if self.pkt_cache:
                typ, pkt = self.pkt_cache.pop(0)
                res = plugins.processPacketFunc(typ, pkt)
                if not res:
                    self.processMsgPacketWithPlugin(pkt, typ, plugins)
            if len(self.pkt_cache) > 100 and time.time() - lastPTime > 5:
                Print.print_war("数据包缓冲区量 > 100")
                lastPTime = time.time()
            elif len(self.pkt_cache) > self.linked_frame.MAX_PACKET_CACHE:
                Print.print_err(f"数据包缓冲区量 > {self.linked_frame.MAX_PACKET_CACHE} 超最大阈值， 已清空缓存区")
                self.pkt_cache.clear()

    def test_player_leave_and_join(self, player):
        Print.print_inf(f"正在测试{player}的进退游戏.")
        plugins.execute_player_leave(player, self.linked_frame.on_plugin_err)
        plugins.execute_player_join(player, self.linked_frame.on_plugin_err)

    def Inject(self):
        startDetTime = time.time()
        if self.linked_frame.server_cfgs["主动获取UUID"]:
            time.sleep(2)
            self.allplayers = self.allplayers_name = self.sendcmd("/testfor @a", True).OutputMessages[0].Parameters[0].split(", ")
            self.store_uuid_pkt = {'ActionType': 0, 'Entries': []}
            for playername in self.allplayers_name:
                Print.print_inf(f"开启主动获取UUID模式: 正在获取 {playername} 的UUID")
                res = self.sendcmd(f"/querytarget @a[name={playername}]", True)
                uuid = json.loads(res.OutputMessages[0].Parameters[0])[0]["uniqueId"]
                self.store_uuid_pkt["Entries"].append({'UUID': uuid, 'EntityUniqueID': -21474836462, 'Username': playername, 
                    'Skin':{"SkinData": 1}, 'XUID': None, 'PlatformChatID': '', 'BuildPlatform': 1})
                Print.print_inf(f"开启主动获取UUID模式: {playername} 的UUID为 {uuid}")
        else:
            while not self.store_uuid_pkt and time.time() - startDetTime < 60:pass
            if not self.store_uuid_pkt:
                self.linked_frame.status = SysStatus.NORMAL_EXIT
                Print.print_err("60s 内未收取到UUID包， 已退出")
                Print.print_err("可尝试在租赁服登录配置中将\"主动获取UUID\"设置为true来解决此问题")
                exit()
        self.processPlayerList(self.store_uuid_pkt, True)
        self.requireUUIDPacket = False
        Print.print_suc("初始化完成, 在线玩家: " + ", ".join(self.allplayers))
        time.sleep(0.5)
        self.say_to("@a", "§l§7[§f!§7] §r§fToolDelta Enabled!")
        self.say_to("@a", "§l§7[§f!§7] §r§f北京时间 " + datetime.datetime.now().strftime("§a%H§f : §a%M"))
        self.say_to("@a", "§l§7[§f!§7] §r§f输入.help获取更多帮助哦")
        self.linked_frame.status = SysStatus.RUNNING

    def Inject2(self):
        self.allplayers = self.allplayers_name = self.sendcmd("/testfor @a", True).OutputMessages[0].Parameters[0].split(", ")
        self.bot_name = self.sendcmd("/testfor @s", True).OutputMessages[0].Parameters[0]
        for player in self.allplayers:
            result = json.loads(
                self.sendcmd("/querytarget " + player, True).OutputMessages[0].Parameters[0]
            )[0]["uniqueId"]
            self.players_uuid[player] = result
            Print.print_inf(f"玩家: {player} 的UUID已获取: {result}")
        Print.print_suc("初始化完成, 在线玩家: " + ", ".join(self.allplayers) + ", 机器人ID: " + self.bot_name)
        time.sleep(0.5)
        self.say_to("@a", "§l§7[§f!§7] §r§fToolDelta Enabled!")
        self.say_to("@a", "§l§7[§f!§7] §r§f北京时间 " + datetime.datetime.now().strftime("§a%H§f : §a%M"))
        self.say_to("@a", "§l§7[§f!§7] §r§f输入.help获取更多帮助哦")
            
    def waitUntilProcess(self):
        self.requireUUIDPacket = True
        self.allplayers.clear()
        self.players_uuid.clear()
        while self.pkt_unique_id == 0:pass

    def clearCmdRespList(self):
        while 1:
            time.sleep(3)
            for k in self.command_resp.copy():
                if time.time() - self.command_resp[k][0] > 10:
                    del self.command_resp[k]

    def sendwocmd(self, cmd: str):
        conn.SendNoResponseCommand(self.linked_frame.con, cmd)

    def sendcmd(self, cmd: str, waitForResp: bool = False, timeout: int = 30):
        uuid = conn.SendMCCommand(self.linked_frame.con, cmd)
        if waitForResp:
            self.command_req.append(uuid)
            waitStartTime = time.time()
            while 1:
                res = self.command_resp.get(uuid)
                if res is not None:
                    self.command_req.remove(uuid)
                    del self.command_resp[uuid]
                    return Packet_CommandOutput(res[1])
                elif time.time() - waitStartTime > timeout:
                    self.command_req.remove(uuid)
                    raise TimeoutError(1, "指令返回获取超时")
        else:
            return uuid
        
    def sendwscmd(self, cmd: str, waitForResp: bool = False, timeout: int = 30):
        uuid = conn.SendWSCommand(self.linked_frame.con, cmd)
        if waitForResp:
            self.command_req.append(uuid)
            waitStartTime = time.time()
            while 1:
                res = self.command_resp.get(uuid, None)
                if res:
                    self.command_req.remove(uuid)
                    del self.command_resp[uuid]
                    return Packet_CommandOutput(res[1])
                elif time.time() - waitStartTime > timeout:
                    self.command_req.remove(uuid)
                    raise TimeoutError(1, "指令返回获取超时")
        else:
            return uuid
        
    def sendfbcmd(self, cmd: str):
        conn.SendFBCommand(self.linked_frame.con, cmd)

    def sendPacket(self, pktType: int, pkt: dict):
        b = conn.JsonStrAsIsGamePacketBytes(pktType, json.dumps(pkt))
        conn.SendGamePacketBytes(self.linked_frame.con, b)

    def sendPacketBytes(self, pkt: bytes):
        conn.SendGamePacketBytes(self.linked_frame.con, pkt)
        
    def say_to(self, target: str, msg: str):
        self.sendwocmd("tellraw " + target + ' {"rawtext":[{"text":"' + msg + '"}]}')

    def player_title(self, target: str, text: str):
        self.sendwocmd(f"title {target} title {text}")

    def player_subtitle(self, target: str, text: str):
        self.sendwocmd(f"title {target} subtitle {text}")

    def player_actionbar(self, target: str, text: str):
        self.sendwocmd(f"title {target} actionbar {text}")

try:
    frame = Frame()
    plugins = PluginGroup(frame, PRG_NAME)
    game_control = GameCtrl(frame)
    frame.set_game_control(game_control)
    frame.set_plugin_group(plugins)
    frame.welcome()
    frame.basic_op()
    frame.downloadMissingFiles()
    import_proxy_lib()
    set_output_mode()
    frame.read_cfg()
    frame.fbtokenFix()
    plugins.read_plugin_from_old(dotcs_module_env)
    plugins.read_plugin_from_new(globals())
    frame.plugin_load_finished(plugins)
    plugins.execute_def(frame.on_plugin_err)
    libs.builtins.tmpjson_save_thread(frame)
    if not frame.external_port:
        frame.getFreePort(usage="fbconn")
        while 1:
            if frame.status in [SysStatus.LAUNCHING, SysStatus.NEED_RESTART]:
                frame.runFB(port=frame.conPort)
                frame.run_conn(port=frame.conPort)
                thread_processPacket = Frame.ClassicThread(game_control.simpleProcessGamePacket)
                game_control.waitUntilProcess()
                thread_processPacketFunc = Frame.ClassicThread(game_control.threadPacketProcessFunc)
                frame.ConsoleCmd_thread()
                game_control.Inject()
            plugins.execute_init(frame.on_plugin_err)
            plugins.execute_dotcs_repeat(frame.on_plugin_err)
            frame.status = SysStatus.RUNNING
            while frame.status == SysStatus.RUNNING:
                time.sleep(0.2)
            thread_processPacket.stop()
            thread_processPacketFunc.stop()
            if frame.status == SysStatus.NORMAL_EXIT:
                break
            elif frame.status == SysStatus.NEED_RESTART:
                Print.print_war("FB断开连接， 尝试重启")
        if game_control.bot_name:
            game_control.sendcmd("kick " + game_control.bot_name)
            Print.print_inf(f"{game_control.bot_name} 已退出游戏.")
        else:
            Print.print_war(f"无法正常踢出机器人")
        frame.close_fb_thread()
        Print.print_inf("正在保存缓存数据.")
        frame.safe_close()
        Print.print_suc("正常退出.")
    else:
        Print.print_suc("正在执行 租赁服初始化..")
        Print.print_inf("§f正在使用 §bExternal §f模式启动, 关闭系统时将不会关闭FastBuilder.")
        frame.sys_data.connect_fb_start_time = 5
        Print.print_inf(f"§b尝试在端口{frame.external_port} 连接到FastBuilder")
        frame.run_conn(port=int(frame.external_port), timeout = 5)
        game_control.requireUUIDPacket = False
        thread_processPacket = Frame.ClassicThread(game_control.simpleProcessGamePacket, usage = "fbconn")
        thread_processPacketFunc = Frame.ClassicThread(game_control.threadPacketProcessFunc, usage = "fbconn")
        frame.ConsoleCmd_thread()
        game_control.Inject2()
        plugins.execute_init(frame.on_plugin_err)
        plugins.execute_dotcs_repeat(frame.on_plugin_err)
        frame.status = SysStatus.RUNNING
        while frame.status == SysStatus.RUNNING:
            time.sleep(0.2)
        if frame.status == SysStatus.NORMAL_EXIT:
            Print.print_err("§cFB断开连接")
        Print.print_inf("正在保存缓存数据.")
        frame.safe_close()
        Print.print_suc("正常退出.")
    os._exit(0)

except (SystemExit, KeyboardInterrupt):
    frame.safe_close()
    os._exit(0)

except Exception:
    Print.print_err("ToolDelta 运行中出现问题:")
    Print.print_err(traceback.format_exc())
    if not frame.external_port:
        frame.close_fb_thread()
    frame.safe_close()
    os._exit(0)
