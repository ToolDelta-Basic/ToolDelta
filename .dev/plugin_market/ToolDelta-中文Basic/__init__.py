import re, time, os
from typing import Callable

from tooldelta import Frame, Plugin, plugins, Config, Builtins, Print

@plugins.add_plugin_as_api("ToolDelta-中文Basic")
class Compiler(Plugin):
    name = "ToolDelta-中文Basic"
    author = "SuperScript"
    version = (0, 0, 2)

    class ScriptExit(Exception):...
    class PlayerExitInterrupt(ScriptExit):...
    class SelectTimeout(ScriptExit):...

    rule1 = re.compile(r'"([^"]*)"=跳转到([0-9]+)',)
    ruleFindStrVar = re.compile(r'([^ ]*?)="([^"]*)"')
    ruleFindIntVar = re.compile(r'([^ ]*?)=([0-9]+)')

    def __init__(self, f: Frame):
        self.f = f
        self.game_ctrl = f.get_game_control()
        self.commands_id_hashmap = {}
        self.reg_cmds_with_checkers = {}
        self.compiled_scripts = {}
        self.make_dirs()
        self.evt_scripts = {
            "injected": {}, 
            "player_message": {},
            "player_join": {},
            "player_leave": {}
        }

    # ---------- API ----------
    def add_command(self, cmd: str, cmd_valid_checker: Callable[[list[str]], bool], executer: Callable):
        """
        扩展 TD-中文Basic 的语法, 添加命令
        cmd: 指令名
        cmd_valid_checker: 检查传入的指令参数是否合法, 不合法可使用 assert 引发报错提示
        executer: 接收参数并执行的方法
        """
        self.commands_id_hashmap[hash(cmd)] = executer
        self.reg_cmds_with_checkers[cmd] = cmd_valid_checker

    def load_scripts(self):
        for script_folder in os.listdir(os.path.join(self.data_path, "脚本文件")):
            fopath = os.path.join(self.data_path, "脚本文件", script_folder)
            err = 0
            for file in os.listdir(fopath):
                if file == "启动.txt":
                    with open(fopath + "/" + "启动.txt", "r", encoding="utf-8") as f:
                        self.evt_scripts["injected"], err = self.script_parse(f.read())
                elif file == "玩家进入.txt":
                    with open(fopath + "/" + "玩家进入.txt", "r", encoding="utf-8") as f:
                        self.evt_scripts["player_join"], err = self.script_parse(f.read(), {"玩家名": 1})
                elif file == "玩家退出.txt":
                    with open(fopath + "/" + "玩家退出.txt", "r", encoding="utf-8") as f:
                        self.evt_scripts["player_leave"], err = self.script_parse(f.read(), {"玩家名": 1})
                elif file == "玩家发言.txt":
                    with open(fopath + "/" + "玩家发言.txt", "r", encoding="utf-8") as f:
                        self.evt_scripts["player_message"], err = self.script_parse(f.read(), {"玩家名": 1, "消息": 1})
            if err is None:
                Print.print_suc(f"ToolDelta-中文Basic: 已加载脚本: {fopath}/{file}")
            elif err == 0:
                Print.print_war(f"ToolDelta-中文Basic: 脚本文件夹为空: {fopath}")
            else:
                Print.print_err(f"ToolDelta-中文Basic: 加载脚本 {fopath}/{file} 出现问题:\n" + str(err.args[0]))
                raise SystemExit

    def get_player_plot_path(self, player: str) -> str:
        return self.data_path + f"/player_vars/{player}.json"

    def param_2_dict(self, re_str):
        # 识别变量赋值表达式
        res = {}
        re_list1 = self.ruleFindIntVar.findall(re_str)
        re_list2 = self.ruleFindStrVar.findall(re_str)
        for k, v in re_list1:
            res[k] = int(v)
        for k, v in re_list2:
            res[k] = v
        return res
    
    def on_def(self):
        self.funclib = plugins.get_plugin_api("基本插件功能库")

    def on_inject(self):
        for k, v in self.evt_scripts["injected"].items():
            self.run_script(v, {})

    def on_player_join(self, player: str):
        for k, v in self.evt_scripts["player_join"].items():
            self.run_script(v, {"玩家名": player})

    def on_player_leave(self, player: str):
        for k, v in self.evt_scripts["player_leave"].items():
            self.run_script(v, {"玩家名": player})

    def on_player_leave(self, player: str, msg: str):
        for k, v in self.evt_scripts["player_message"].items():
            self.run_script(v, {"玩家名": player, "消息": msg})

    @Builtins.new_thread
    def run_script(self, script_name, args_dict):
        self.execute_script(script_name, args_dict)

    def make_dirs(self):
        os.makedirs(os.path.join(self.data_path, "player_vars"), exist_ok = True)
        os.makedirs(os.path.join(self.data_path, "脚本文件"))
    
    def script_parse(self, scripts: str, pre_variables_reg = None):
        """
        将脚本编译为执行器可以执行的命令序列.
        (ID)
        退出: 0, 跳转: 1, 执行: 2
        设定: 3, 判断: 4, 等待: 5,
        导出变量: 6, 读取变量: 7,
        简单运算: 9
        """
        scr_lines: list[tuple[int, list[str]]] = []
        cmp_scripts = []
        loc_vars_register = {"空变量": 2}
        scr_lines_finder: dict[int, int] = {}
        now_line_counter = 0
        # 注册初始变量的类型: 0=int, 1=string, 2=空变量
        scr_lines_register = []
        if pre_variables_reg is not None:
            for k, v in pre_variables_reg.items():
                loc_vars_register[k] = v
        def _add_cmp(id: int, args = None):
            # 添加操作码和参数
            cmp_scripts.append((id, args))
        def _simple_assert_len(args, nlen):
            # 简单地判断参数数量是否合法
            assert len(args) == nlen, f"需要参数数量 {nlen} 个， 实际上 {len(args)} 个"
        def _simple_assert_ln(ln):
            # 简单地判断代码行数是否合法
            assert ln in scr_lines_register, f"不存在第 {int(ln, 16)} 行代码"
        _get_var_type = lambda varname : loc_vars_register.get(varname)
        _easy_hex = lambda x: hex(x)[2:]
        try:
            rawlines = scripts.splitlines()
            for lett in rawlines:
                if not lett.strip() or lett.startswith("#"):
                    continue
                try:
                    linecount = int(lett.split()[0])
                    scr_lines_register.append(_easy_hex(linecount))
                except ValueError:
                    return None, AssertionError(f"{lett.split()[0]} 不是有效的行数")
                scr_lines.append((linecount, lett.split()[1:]))
                scr_lines_finder[linecount] = now_line_counter
                now_line_counter += 1
        except Exception as err:
            return None, err
        try:
            for (ln, args) in sorted(scr_lines, key = lambda x: x[0]):
                match args[0]:
                    case "结束":
                        _simple_assert_len(args, 1)
                        _add_cmp(0)
                        # 结束
                    case "跳转" | "跳转到":
                        _simple_assert_len(args, 2)
                        seq1 = int(args[1])
                        _simple_assert_ln(_easy_hex(seq1))
                        _add_cmp(1, scr_lines_finder[seq1])
                        # 跳转到 <代码行数>
                    case "执行" | "执行指令":
                        assert len(args) > 1, "执行命令 至少需要2个参数"
                        seq1 = " ".join(args[1:])
                        _add_cmp(2, seq1)
                        # 执行 <mc指令>
                    case "设定" | "设定变量":
                        """
                        md: 0=const_int, 1=const_str, 2=等待聊天栏输入, 3=等待聊天栏输入纯数字, 4=玩家计分板分数, 5=玩家坐标 
                        md2: 0=int, 1=str 
                        """
                        assert len(args) > 2, "设定命令 至少需要2个参数"
                        assert args[2] == "为", "语法错误"
                        seq1 = args[1]
                        seq2 = args[3]
                        res = None
                        if seq2.isnumeric() or (len(seq2) > 1 and seq2[0] == "-" and seq2[1:].isnumeric()):
                            md = 0
                            md2 = 0
                            res = int(seq2)
                        elif " ".join(args[3:]).startswith('"') and " ".join(args[3:]).endswith('"'):
                            md = 1
                            md2 = 1
                            res = " ".join(args[3:])[1:-1]
                        elif seq2 == "等待聊天栏输入":
                            md = 2
                            md2 = 1
                        elif seq2 == "等待聊天栏输入纯数字":
                            md = 3
                            md2 = 0
                        elif seq2 == "当前玩家计分板分数":
                            _simple_assert_len(args, 5)
                            md = 4
                            md2 = 0
                            res = args[4]
                        elif seq2 == "玩家当前坐标":
                            md = 5
                            md2 = 1
                        elif seq2 == "当前时间ticks":
                            md = 6
                            md2 = 0
                        else:
                            raise AssertionError(f"无法识别的表达式: " + " ".join(args[3:]))
                        assert not(loc_vars_register.get(seq1)is not None and loc_vars_register.get(seq1) != md2), "变量类型已被定义, 无法更改"
                        loc_vars_register[seq1] = md2
                        _add_cmp(3, [md, md2, seq1, res])
                        # 设定变量 设定模式, 变量类型, 变量名[, 值]
                    case "判断":
                        # 判断 变量 操作符 变量 成立=跳转到??? 不成立=跳转到???
                        _simple_assert_len(args, 6)
                        seq1 = args[1]
                        seq2 = args[3]
                        assert _get_var_type(seq1) is not None and _get_var_type(seq2) is not None, (
                            f"变量 {seq1} 或 变量 {seq2} 还没有被设定 (判断语句中暂时无法直接使用非变量, 你可以先设定变量)"
                        )
                        match args[2]:
                            case "=" | "==": args[2] = 0
                            case "!=" | "=!": args[2] = 1
                            case "<": args[2] = 2
                            case "<=": args[2] = 3
                            case ">": args[2] = 4
                            case ">=": args[2] = 5
                            case _:
                                raise AssertionError("判断操作符只能为 <, >, ==, <=, >= !=")
                        assert args[4].startswith("成立=跳转到") and args[5].startswith("不成立=跳转到"), (
                            "判断命令: 第5、6个参数应为： 成立=跳转到<脚本行数>, 不成立=跳转到<脚本行数>"
                        )
                        if args[2] in [2, 3, 4, 5] and (_get_var_type(seq1) != 0 or _get_var_type(seq2) != 0):
                            raise AssertionError("判断命令: 暂时只能比较数值变量大小")
                        try:
                            seq3 = int(args[4][6:])
                            seq4 = int(args[5][7:])
                            _simple_assert_ln(_easy_hex(seq3))
                            _simple_assert_ln(_easy_hex(seq4))
                        except ValueError:
                            raise AssertionError('"跳转到"指向的代码行数只能为纯数字')
                        _add_cmp(4, (seq1, args[2], seq2, scr_lines_finder[seq3], scr_lines_finder[seq4]))
                        # 变量1, 操作符, 变量2, 成立跳转, 不成立跳转
                    case "等待":
                        _simple_assert_len(args, 2)
                        try:
                            seq1 = float(args[1])
                            assert seq1 > 0
                        except:
                            raise AssertionError(f"等待命令 参数应为正整数, 为秒数")
                        _add_cmp(5, seq1)
                    case "导出变量" | "存储变量":
                        _simple_assert_len(args, 4)
                        assert args[2] == "->", "导出个人变量格式应为 内存变量名 -> 磁盘变量名"
                        assert args[1] in loc_vars_register.keys(), f"变量 {args[1]} 未定义, 不能使用, 请先设定"
                        _add_cmp(6, (args[1], args[3]))
                    case "读取变量":
                        _simple_assert_len(args, 6)
                        assert args[2] == "<-" and args[4] == "类型为" and args[5] in ["数值", "字符串"], "读取个人变量格式应为 内存变量名 <- 磁盘变量名 类型为 数字/字符串"
                        _add_cmp(7, (args[1], args[3]))
                        loc_vars_register[args[1]] = ["数值", "字符串"].index(args[5])
                    case "简单运算":
                        # var1 <- var2 () var3
                        _simple_assert_len(args, 6)
                        assert args[2] == "<-" and args[4] in ["+", "-", "*", "/", "%"], f"格式不正确: 应为 变量 <- 变量1 运算符 变量2"
                        assert args[3] in loc_vars_register.keys() and args[5] in loc_vars_register.keys(), f"变量 {args[3]} 或 {args[5]} 未定义, 不能使用, 请先设定"
                        assert loc_vars_register[args[3]] == loc_vars_register[args[5]] == 0, "只能对数值型变量进行运算"
                        loc_vars_register[args[1]] = 0
                        _add_cmp(8, (args[1], ["+", "-", "*", "/", "%"].index(args[4]), args[3], args[5]))
                    case _:
                        if args[0] in self.reg_cmds_with_checkers.keys():
                            cmd = args[0]
                            self.reg_cmds_with_checkers[cmd](len(args))
                            _add_cmp(hash(cmd), None if len(args) == 1 else args[1:])
                        else:
                            raise AssertionError(f"无法被识别的指令: {args[0]}")
            return cmp_scripts, None
        except AssertionError as err:
            return None, AssertionError(f"第{ln}行 出现问题: {err}")
        
    def execute_script(self, script_name: str, pre_variables: None | dict = None):
        """"
        执行传入的指令码
        """
        #last_save_pos = tmpjson.read(self.get_player_plot_path(player))["plots_progress"].get(plot_name)
        #if last_save_pos is not None:
        #    pointer = last_save_pos
        #else:
        #    pointer = 0
        if pre_variables.get("玩家名") is not None:
            player = pre_variables.get("玩家名")
            path = self.get_player_plot_path(player)
        else:
            player = None
        tmpjson = Builtins.TMPJson
        tmpjson.loadPathJson(path, False)
        if tmpjson.read(path) is None:
            tmpjson.write(path, {})
        pointer = 0
        script_code = self.compiled_scripts[script_name]
        loc_vars = {"空变量": None}
        if pre_variables is not None:
            loc_vars.update(pre_variables)
        plot_terminated = False
        try:
            while pointer < len(script_code):
                if plot_terminated:
                    raise self.SelectTimeout()
                if not player in self.game_ctrl.allplayers:
                    raise self.PlayerExitInterrupt()
                cmd = script_code[pointer]
                match cmd[0]:
                    case 0:
                        break
                    case 1:
                        pointer = cmd[1]
                        continue
                    case 2:
                        self.game_ctrl.sendwocmd(self.var_replace(loc_vars, cmd[1]))
                    case 3:
                        setmode, _, name, value = cmd[1]
                        match setmode:
                            case 0 | 1:
                                loc_vars[name] = value
                            case 2:
                                try:
                                    res = self.funclib.waitMsg(player, 180)
                                    if res is None:
                                        res = ""
                                    else:
                                        self.game_ctrl.say_to(player, "§a输入完成, 请退出聊天栏")
                                    loc_vars[name] = res
                                except IOError:
                                    plot_terminated = True
                                    break
                            case 3:
                                while 1:
                                    try:
                                        res = int(self.funclib.waitMsg(player, 180))
                                        loc_vars[name] = res
                                        self.game_ctrl.say_to(player, "§a输入完成, 请退出聊天栏")
                                        break
                                    except ValueError:
                                        self.game_ctrl.say_to(player, "§c请输入纯数字")
                                    except IOError:
                                        plot_terminated = True
                                        break
                            case 4:
                                try:
                                    res = self.funclib.getScore(player, value)
                                except:
                                    res = None
                                loc_vars[name] = res
                            case 5:
                                x, y, z = self.funclib.getPosXYZ(player)
                                loc_vars[name] = f"{int(x)} {int(y)} {int(z)}"
                            case 6:
                                loc_vars[name] = int(time.time())
                    case 4:
                        seq1, op, seq2, jmp1, jmp2 = cmd[1]
                        seq1 = loc_vars[seq1]
                        seq2 = loc_vars[seq2]
                        res = [
                            (lambda x, y: x == y),
                            (lambda x, y: x != y),
                            (lambda x, y: x < y),
                            (lambda x, y: x <= y),
                            (lambda x, y: x > y),
                            (lambda x, y: x >= y)
                        ][op](seq1, seq2)
                        pointer = jmp1 if res else jmp2
                        continue
                    case 5:
                        time.sleep(cmd[1])
                    case 13:
                        seq1, seq2 = cmd[1]
                        old = tmpjson.read(path)
                        old[seq2] = loc_vars[seq1]
                        tmpjson.write(path, old)
                    case 14:
                        seq1, seq2 = cmd[1]
                        old = tmpjson.read(path)
                        loc_vars[seq1] = old.get(seq2)
                    case 15:
                        seq1, op, seq2, seq3 = cmd[1]
                        op = (
                            lambda x, y:x+y,
                            lambda x, y:x-y,
                            lambda x, y:x*y,
                            lambda x, y:x/y,
                            lambda x, y:x%y
                        )[op]
                        loc_vars[seq1] = int(op(loc_vars[seq2], loc_vars[seq3]))
                pointer += 1
        except self.PlayerExitInterrupt:
            Print.print_war(f"玩家 {player} 在脚本执行结束之前退出了游戏")
        except self.ScriptExit:
            ...
        
    @staticmethod
    def var_replace(loc_vars: dict[str, object], sub: str):
        myrule = re.compile(r"(\[变量:([^\]]*)\])")
        for varsub, varname in myrule.findall(sub):
            varvalue = loc_vars.get(varname, f"<未定义的变量名:{varname}>")
            sub = sub.replace(varsub, str(varvalue))
        return sub

def examplefunc1():
    rule = re.compile(r'([^ ]*?)=([0-9]+)')
    print(rule.findall(' 变量1=""  变量2=154154 '))

def examplefunc2():
    example = """
    10 设定 a 为 1
    20 设定 b 为 2
    100 判断 a == b 成立=跳转到200 不成立=跳转到300
    200 结束
    300 结束
    """
    res, err = Compiler(Frame()).script_parse(example)
    if err:
        raise err
    else:
        print(res)

if __name__ == "__main__":
    examplefunc2()