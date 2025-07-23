from .lang_parser import parse_file, REPLACER
from .zh_CN import LANG

translator_pool: dict[str, REPLACER] = {}


def init_pool():
    p = parse_file(LANG)
    translator_pool.update(p)
