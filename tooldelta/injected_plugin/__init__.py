import asyncio
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
async def execute_player_message(message, playername):
    tasks = [func(message, playername) for func in player_message_funcs]
    await asyncio.gather(*tasks)


async def execute_player_join(playername):
    tasks = [func(playername) for func in player_join_funcs]
    await asyncio.gather(*tasks)


async def execute_player_left(playername):
    tasks = [func(playername) for func in player_left_funcs]
    await asyncio.gather(*tasks)


async def execute_init():
    task = [func() for func in init_plugin_funcs]
    await asyncio.gather(*task)


# 处理te并执行插件


async def load_plugin_file(file):
    # 导入插件模块
    module_name = file
    plugin_module = importlib.import_module(f"plugins.{module_name}")

    # 查找插件处理函数
    for value in plugin_module.__dict__.values():
        if callable(value) and hasattr(value, "__plugin_handler__"):
            # 执行插件处理函数
            event = getattr(value, "__plugin_handler__")
            await value(event)


async def load_plugin(frame2, game_control2):
    global game_control, frame
    game_control = game_control2
    frame = frame2
    tasks = []
    # 检查插件目录是否存在
    if not os.path.exists("plugins"):
        os.mkdir("plugins")

    # 读取本目录下的文件夹名字

    for file in os.listdir("plugins"):
        if os.path.isdir(os.path.join("plugins", file)):
            task = asyncio.create_task(load_plugin_file(file))
            tasks.append(task)

    # 并发加载插件
    await asyncio.gather(*tasks)


def sendcmd(*arg):
    game_control.sendcmd(*arg)


def sendwscmd(*arg):
    game_control.sendwscmd(*arg)


def sendwocmd(*arg):
    game_control.sendwocmd(*arg)


def sendPacket(*arg):
    game_control.sendPacket(*arg)


def sendPacketJson(*arg):
    game_control.sendPacketJson(*arg)


def sendfbcmd(*arg):
    game_control.sendfbcmd(*arg)


def tellrawText(playername: str, title: str | None = None, text: str = ""):
    """
    发送tellraw消息
    ---
    playername:str 玩家名.
    title:str 说话人.
    text:str 内容.
    """
    if title is None:
        sendcmd(r"""/tellraw %s {"rawtext":[{"text":"§r%s"}]}""" % (playername, text))
    else:
        sendcmd(
            r"""/tellraw %s {"rawtext":[{"text":"<%s> §r%s"}]}"""
            % (
                playername,
                title,
                text,
            )
        )
