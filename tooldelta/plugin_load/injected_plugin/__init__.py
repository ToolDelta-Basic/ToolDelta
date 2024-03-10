import asyncio
from concurrent.futures import thread
from dataclasses import dataclass
import os
import sys
import importlib
import threading

from tooldelta.color_print import Print
from tooldelta.plugin_manager import plugin_manager
from tooldelta.plugin_load import plugin_is_enabled


# 定义插件处理函数列表
player_message_funcs = {}
player_prejoin_funcs = {}
player_join_funcs = {}
player_left_funcs = {}
player_death_funcs = {}
repeat_funcs = {}
init_plugin_funcs = {}


def player_message(priority=None):
    def decorator(func):
        player_message_funcs[func] = priority
        return func

    return decorator


def player_prejoin(priority=None):
    def decorator(func):
        player_prejoin_funcs[func] = priority
        return func

    return decorator


def player_join(priority=None):
    def decorator(func):
        player_join_funcs[func] = priority
        return func

    return decorator


def player_left(priority=None):
    def decorator(func):
        player_left_funcs[func] = priority
        return func

    return decorator


def player_death(priority=None):
    def decorator(func):
        player_death_funcs[func] = priority
        return func

    return decorator


def init(priority=None):
    def decorator(func):
        init_plugin_funcs[func] = priority
        return func

    return decorator


def repeat(*args):
    def decorator(func):
        repeat_funcs[func] = args[0]
        return func

    return decorator


# repeat_task
async def repeat_task(func, time):
    while True:
        await asyncio.sleep(time)
        # 防止出错
        try:
            await func()
        except Exception as e:
            Print.print_err(f"repeat_task error: {e}")


async def execute_asyncio_task(func_dict: dict, *args, **kwargs):
    tasks = []
    none_tasks = []

    # 将任务添加到 tasks 列表或 none_tasks 列表中
    for func, priority in func_dict.items():
        if priority is not None:
            tasks.append((priority, func(*args, **kwargs)))
        else:
            none_tasks.append((priority, func(*args, **kwargs)))

    # 按优先级对非 None 任务排序
    tasks.sort(key=lambda x: x[0])

    # 将 none_tasks 列表附加到已排序的任务列表的末尾
    tasks += none_tasks

    await asyncio.gather(*[task[1] for task in tasks])


# 并发初始化插件
async def execute_init():
    await execute_asyncio_task(init_plugin_funcs)


async def run_repeat():
    # 为字典中的每一个函数创建一个循环特定时间的任务
    tasks = []
    for func, time in repeat_funcs.items():
        tasks.append(repeat_task(func, time))
    # 并发执行所有任务
    await asyncio.gather(*tasks)


async def safe_jump():
    try:
        main_task.cancel()
    except NameError:
        return


main_task: asyncio.Task


async def execute_repeat():
    global main_task
    main_task = asyncio.create_task(run_repeat())
    try:
        await main_task
    except asyncio.CancelledError:
        Print.print_suc("重复任务 repeat_task 已退出！")


@dataclass(order=True)
class player_name:
    playername: str

@dataclass(order=True)
class player_message_info(player_name):
    message: str
@dataclass(order=True)
class player_death_info(player_name):
    message: str
    killer: str = None
# 处理玩家消息并执行插件
async def execute_player_message(playername, message):
    await execute_asyncio_task(player_message_funcs, player_message_info(playername=playername, message=message))


async def execute_death_message(playername, killer, message):
    await execute_asyncio_task(player_death_funcs,player_death_info(playername=playername, killer=killer, message=message))


async def execute_player_join(playername):
    await execute_asyncio_task(player_join_funcs, player_name(playername=playername))

async def execute_player_prejoin(playername):
    await execute_asyncio_task(player_prejoin_funcs, player_name(playername=playername))

async def execute_player_left(playername):
    await execute_asyncio_task(player_left_funcs, player_name(playername=playername))


async def load_plugin_file(file):
    # 导入插件模块
    module_name = file
    sys.path.append(os.path.join(os.getcwd(), "插件文件", "ToolDelta注入式插件"))
    plugin_module = importlib.import_module(module_name)
    meta_data = create_plugin_metadata(
        getattr(plugin_module, "__plugin_meta__", {"name": module_name})
    )
    # 获取插件元数据
    plugin_manager.test_name_same(meta_data.name, file)
    if not plugin_manager.plugin_is_registered("injected", meta_data.name):
        plugin_manager.auto_register_plugin("injected", meta_data)
    return meta_data


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
    name = metadata_dict.get("name", "未命名插件")
    version = metadata_dict.get("version", "1.0")
    description = metadata_dict.get("description", "未知插件")
    usage = metadata_dict.get("usage", "")
    author = metadata_dict.get("author", "未知")
    homepage = metadata_dict.get("homepage", "")

    return PluginMetadata(name, author, description, version, usage, homepage)


async def load_plugin(plugin_grp):
    tasks = []

    # 读取本目录下的文件夹名字
    PLUGIN_PATH = os.path.join(os.getcwd(), "插件文件", "ToolDelta注入式插件")
    for file in os.listdir(PLUGIN_PATH):
        if not plugin_is_enabled(file):
            continue
        if os.path.isdir(os.path.join(PLUGIN_PATH, file)):
            plugin_grp.injected_plugin_loaded_num += 1
            task = asyncio.create_task(load_plugin_file(file))
            tasks.append(task)

    # 顺序加载插件并收集插件元数据
    all_plugin_metadata = []
    for task in tasks:
        plugin_metadata = await task
        all_plugin_metadata.append(plugin_metadata)

    # 打印所有插件的元数据
    for metadata in all_plugin_metadata:
        Print.print_suc(
            f"成功载入插件 {metadata.name} 版本: {metadata.version} 作者: {metadata.author}"
        )
