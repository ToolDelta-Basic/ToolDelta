import re

REPLACE_FLAG = tuple[int, str | None]
REPLACER = list[REPLACE_FLAG | str]

repl_rule = re.compile(r"%(?P<a>[0-9a-z\.]+)(?P<b>(\$[a-z]+)?)")

REPLACER_SPLIT = "\x00"


def parse_file(content: str):
    pool: dict[str, REPLACER] = {}
    for line in content.splitlines():
        if line.startswith("##") or line.strip() == "":
            continue
        key, repl = parse_line(line)
        pool[key] = repl
    return pool


def parse_line(line: str):
    comment_flag = line.find("\t#")
    if comment_flag != -1:
        line = line[:comment_flag]
    key, replacer = line.strip("\t").split("=", 1)
    return key, parse_replacer(replacer)


def parse_replacer(line: str):
    cached_result: list[REPLACE_FLAG] = []
    m = repl_rule.finditer(line)
    auto_index = 1
    newline = line
    for mgroup in m:
        mode1 = mgroup.group("a")
        mode2 = mgroup.group("b")
        repl_str = f"%{mode1}{mode2}"
        mode2 = mode2.removeprefix("$")
        if mode2 != "":
            # like %1$s
            repl_index = int(mode1)
            repl_mode = "%" + mode2
        elif mode1.isdigit():
            # like %1
            repl_index = int(mode1)
            repl_mode = None
        else:
            # like %.2f
            repl_index = auto_index
            repl_mode = "%" + mode1
        cached_result.append((repl_index, repl_mode))
        newline = newline.replace(repl_str, REPLACER_SPLIT)
        auto_index += 1
    result: REPLACER = []
    for i, param in enumerate(newline.split(REPLACER_SPLIT)):
        if i > 0:
            result.append(cached_result.pop(0))
        result.append(param)
    return result
