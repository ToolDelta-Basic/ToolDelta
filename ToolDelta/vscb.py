# FURTURE library for Plugin Emulator
import json, re
from .color_print import Print

FLOW_UP = 2 ** 31 - 1
FLOW_DOWN = -2 ** 31
FLOW_FIX = 2 ** 32
scbs = {}

class ExecFailed(Exception):...

def input_int(__prompt = "", errmsg = "请输入整数"):
    while 1:
        try:
            return int(input(Print.fmt_info(__prompt)))
        except ValueError:
            Print.print_err(errmsg)
            continue

def scb_exists(scbname):
    return scbname in scbs.keys()

def test_overflow(num):
    while num >= FLOW_UP:
        num -= FLOW_FIX
    while num <= FLOW_DOWN:
        num += FLOW_FIX

def require_score(scbname, tar_name, not_set_to_0 = False):
    if not scb_exists(scbname):
        raise ExecFailed(f"计分板 {scbname} 不存在")
    if scbs[scbname].get(tar_name) is not None:
        return scbs[scbname][tar_name]
    elif not_set_to_0:
        scbs[scbname][tar_name] = 0
        return 0
    else:
        score = input_int(f"需要计分板 {scbname} 的 {tar_name} 的分数, 请输入: ")
        scbs[scbname][tar_name] = score
        return score

def sendcmd(cmd: str, waitForResp = False, timeout = 30):
    if cmd.startswith("/"):
        cmd = cmd[1:]
    cmds = cmd.split()
    try:
        match cmds[0]:
            case "scoreboard":
                if cmds[1] == "objectives":
                    if cmds[2] == "add":
                        scbname = cmds[3]
                        assert cmds[4] == "dummy"
                        if scb_exists(scbname):
                            raise ExecFailed(f"计分板 {scbname} 已存在")
                        assert len(scbname) in range(16), "计分板名太长"
                        scbs[scbname] = {}
                    elif cmds[2] == "remove":
                        scbname = cmds[3]
                        if not scb_exists(scbname):
                            raise ExecFailed(f"计分板 {scbname} 不存在")
                    assert cmds[2] == "setdisplay"
                elif cmds[1] == "players":
                    if cmds[2] in ["add", "remove"]:
                        # To be discussed
                        if cmd[2] == "remove":
                            fx = -1
                        else:
                            fx = 1
                        target, scbname, addscore = cmds[3:5]
                        if scbs.get(scbname) is None:
                            raise ExecFailed(f"计分板 {scbname} 不存在")
                        final = scbs[scbname].get(target, 0) + int(addscore) * fx
                        scbs[scbname][target] = test_overflow(final)
                    elif cmds[2] == "operation":
                        target1, scb1, op, target2, scb2 = cmds[3:8]
                        assert op in ["+=", "-=", "=", "*=", "/=", "%="], "计分板运算符不合法"
                        match op:
                            case "+=":
                                final = require_score(scb1, target1) + require_score(scb2, target2)
                            case "-=":
                                final = require_score(scb1, target1) + require_score(scb2, target2)
                            case "*=":
                                final = require_score(scb1, target1) * require_score(scb2, target2)
                            case "/=":
                                final = int(require_score(scb1, target1) / require_score(scb2, target2))
                            case "%=":
                                final = require_score(scb1, target1) % require_score(scb2, target2)
                        scbs[scbname][target1] = test_overflow(final)
                    elif cmds[2] == "reset":
                        target, scb = cmds[3:5]
                        require_score(scb, target)
                        del scbs[scbname][target]

    except (IndexError, AssertionError):
        ...
