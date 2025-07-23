from .lang_parser import parse_file, REPLACER
from .zh_CN import LANG

translator_pool: dict[str, REPLACER] = {}


def init_pool():
    p = parse_file(LANG)
    translator_pool.update(p)


def ensure_inited():
    if not translator_pool:
        raise ValueError(
            "翻译数据池未初始化, 使用 mc_translator.init_pool() 以初始化数据池。"
        )
