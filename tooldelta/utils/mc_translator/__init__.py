"""
Minecraft 文本翻译模块
"""

from .pool import init_pool
from .translator import translate

__all__ = ["init_pool", "translate"]
