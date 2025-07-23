import re
from .pool import translator_pool, ensure_inited

sec_translator = re.compile(r"%([A-Za-z0-9\.\-_]+)")

# feat: 内置文本翻译器

def translate(key: str, args: list | None = None, translate_args=True) -> str:
    """
    将 Minecraft 的游戏消息文本翻译为中文。

    Args:
        key (str): 消息文本
        args (list | None, optional): 翻译时附带的参数项
        translate_args (bool, optional): 是否将参数项一并进行翻译

    Returns:
        str: 翻译后的文本, 翻译失败将返回原内容
    """
    ensure_inited()
    if key.startswith("§"):
        # e.g. §emultiplayer.player.joined
        color, key = split_color_and_key(key)
    else:
        color = ""
    if "%" in key:
        # if args is None:
        #     # key 内也有需要翻译的内容
        #     return color + sec_translator.sub(
        #         lambda t: translate(t.group(0)[1:]),
        #         key,
        #     )
        # else:
        key = key.replace("%", "")
    res = translator_pool.get(key)
    if res is None:
        return color + key
    if args is None:
        first_text = res[0]
        assert isinstance(first_text, str), str(res)
        return first_text
    sentence = ""
    for param in res:
        if isinstance(param, str):
            sentence += param
        else:
            idx, mode = param
            repl_arg = args[idx - 1]
            if isinstance(repl_arg, str):
                if translate_args:
                    repl_arg = sec_translator.sub(
                        lambda trans: translate(trans.group(0)),
                        repl_arg,
                    )
                sentence += repl_arg
            else:
                sentence += mode % repl_arg
    return color + sentence


def split_color_and_key(key_with_color: str):
    char_idx = 0
    color_chars = ""
    while 1:
        now_char = key_with_color[char_idx]
        if now_char == "§":
            color_chars += key_with_color[char_idx : char_idx + 2]
            char_idx += 2
        else:
            break
    return color_chars, key_with_color[char_idx:]
