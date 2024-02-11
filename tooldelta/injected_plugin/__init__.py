import asyncio
from distutils.core import setup_keywords
import os
import importlib
from re import A
import ujson as json

from tooldelta.color_print import Print

# 定义插件处理函数列表
player_message_funcs = []
player_join_funcs = []
player_left_funcs = []
repeat_funcs = {}
init_plugin_funcs = []


def player_message():
    def decorator(func):
        player_message_funcs.append(func)
        return func

    return decorator


def player_join():
    def decorator(func):
        player_join_funcs.append(func)
        return func

    return decorator


def player_left():
    def decorator(func):
        player_left_funcs.append(func)
        return func

    return decorator


def repeat(*args):
    def decorator(func):
        repeat_funcs[func] = args[0]
        return func

    return decorator


def init():
    def decorator(func):
        init_plugin_funcs.append(func)
        return func

    return decorator


# repeat_task
def repeat_task(func, time):
    while True:
        asyncio.sleep(time)
        # 防止出错
        try:
            func()
        except Exception as e:
            Print.print_err(f"repeat_task error: {e}")

async def execute_repeat():
    # 为字典每一个函数创建一个循环特定时间的任务
    for func, time in repeat_funcs.items():
        asyncio.create_task(repeat_task(func, time))  # 创建任务
    # 并发执行所有任务
    await asyncio.gather(*asyncio.all_tasks())


# 处理玩家消息并执行插件
async def execute_player_message(playername, message):
    tasks = [func(message, playername) for func in player_message_funcs]
    await asyncio.gather(*tasks)


async def execute_player_join(playername):
    tasks = [func(playername) for func in player_join_funcs]
    await asyncio.gather(*tasks)


async def execute_player_left(playername):
    tasks = [func(playername) for func in player_left_funcs]
    await asyncio.gather(*tasks)


async def load_plugin_file(file):
    # 导入插件模块
    module_name = file
    plugin_module = importlib.import_module(f"plugins.{module_name}")
    # 获取插件元数据
    return getattr(plugin_module, "__plugin_meta__", None)
class PluginMetadata:
    def __init__(
        self,
        name,
        author,
        description,
        version,
        usage,
        homepage,
    ):
        self.name = name
        self.author = author
        self.description = description
        self.usage = usage
        self.version = version
        self.homepage = homepage


def create_plugin_metadata(metadata_dict: dict):
    """
    创建插件元数据。

    参数:
        - metadata_dict (dict): 包含插件元数据的字典.

    返回:
        PluginMetadata: 插件元数据对象.
    """
    name = metadata_dict.get("name","未命名插件")
    version = metadata_dict.get("version","1.0")
    description = metadata_dict.get("description","未知插件")
    usage = metadata_dict.get("usage", "")
    author = metadata_dict.get("author", "未知")
    homepage = metadata_dict.get("homepage","")

    return PluginMetadata(name, author, description, version, usage, homepage)


# 快捷导入插件函数
from .movent import (
    sendcmd,
    sendfbcmd,
    sendPacket,
    sendPacketJson,
    sendwocmd,
    sendwscmd,
    tellrawText,
    get_all_player,
)
