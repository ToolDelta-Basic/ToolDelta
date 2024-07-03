"ToolDelta 注入式插件"

import asyncio
from dataclasses import dataclass
import os
import sys
import importlib

from typing import TYPE_CHECKING, Callable, List, Tuple
from ...color_print import Print
from ...plugin_load import (
    plugin_is_enabled,
    PluginAPINotFoundError,
    PluginAPIVersionError,
)

if TYPE_CHECKING:
    from tooldelta.plugin_load.PluginGroup import PluginGroup

# 定义插件处理函数列表
player_message_funcs: dict[Callable, int | None] = {}
player_prejoin_funcs: dict[Callable, int | None] = {}
player_join_funcs: dict[Callable, int | None] = {}
player_left_funcs: dict[Callable, int | None] = {}
player_death_funcs: dict[Callable, int | None] = {}
commmand_message_funcs: dict[Callable, int | None] = {}
repeat_funcs: dict[Callable, int | float] = {}
init_plugin_funcs: dict[Callable, int | None] = {}
frame_exit_funcs: dict[Callable, int | None] = {}


def player_message(priority: int | None = None) -> Callable:
    """载入处理玩家消息

    Args:
        priority (int, optional): 插件优先级

    Returns:
        Callable: 插件处理函数
    """

    def decorator(func):
        player_message_funcs[func] = priority
        return func

    return decorator


def player_prejoin(priority: int | None = None) -> Callable[["player_name"], None]:
    """载入处理玩家加入前事件

    Args:
        priority (int | None, optional): 插件优先级

    Returns:
        Callable: 插件处理函数
    """

    def decorator(func):
        player_prejoin_funcs[func] = priority
        return func

    return decorator


def player_join(priority: int | None = None) -> Callable:
    """载入处理玩家加入事件

    Args:
        priority (int | None, optional): 插件优先级

    Returns:
        Callable: 插件处理函数
    """

    def decorator(func):
        player_join_funcs[func] = priority
        return func

    return decorator


def player_left(priority: int | None = None) -> Callable:
    """载入处理玩家离开事件

    Args:
        priority (int | None, optional): 插件优先级

    Returns:
        Callable: 插件处理函数
    """

    def decorator(func):
        player_left_funcs[func] = priority
        return func

    return decorator


def player_death(priority: int | None = None) -> Callable:
    """载入处理玩家死亡事件

    Args:
        priority (int | None, optional): 插件优先级

    Returns:
        Callable: 插件处理函数
    """

    def decorator(func):
        player_death_funcs[func] = priority
        return func

    return decorator


def init(priority: int | None = None) -> Callable:
    """载入机器人进入游戏后初始化插件

    Args:
        priority (int | None, optional): 插件优先级

    Returns:
        Callable: 插件处理函数
    """

    def decorator(func):
        init_plugin_funcs[func] = priority
        return func

    return decorator


def frame_exit(priority: int | None = None) -> Callable:
    """载入处理框架退出事件的插件

    Args:
        priority (int | None, optional): 插件优先级

    Returns:
        Callable: 插件处理函数
    """

    def decorator(func):
        frame_exit_funcs[func] = priority
        return func

    return decorator


def repeat(retime: int | float = 5) -> Callable:
    """载入重复任务

    Args:
        retime (int, optional): 重复时间

    Returns:
        Callable: 插件处理函数
    """

    def decorator(func):
        repeat_funcs[func] = retime
        return func

    return decorator


async def command_say(priority: int | None = None) -> Callable:
    """载入处理命令消息

    Args:
        name (str): 命令名
        priority (int | None, optional): 插件优先级
    """

    def decorator(func):
        commmand_message_funcs[func] = priority
        return func

    return decorator


async def repeat_task(func: Callable, time: int | float) -> None:
    """执行重复任务（执行完等待一段时间再执行）

    Args:
        func (Callable): 定时执行的函数
        time (int | float): 重复时间
    """
    while True:
        await asyncio.sleep(time)
        # 防止出错
        try:
            await func()
        except Exception as e:
            Print.print_err(f"repeat_task error: {e}")


async def execute_asyncio_task(func_dict: dict, *args, **kwargs) -> None:
    """执行异步任务

    Args:
        func_dict (dict): 函数字典
    """
    tasks: List[Tuple[int, asyncio.Task]] = []
    none_tasks: List[Tuple[None, asyncio.Task]] = []
    # 将任务添加到 tasks 列表或 none_tasks 列表中
    for func, priority in func_dict.items():
        if priority is not None:
            tasks.append((priority, asyncio.create_task(func(*args, **kwargs))))
        else:
            none_tasks.append((priority, asyncio.create_task(func(*args, **kwargs))))

    # 按优先级对非 None 任务排序
    tasks.sort(key=lambda x: x[0])

    # 将 none_tasks 列表附加到已排序的任务列表的末尾
    task_list = none_tasks + tasks

    await asyncio.gather(*[task[1] for task in task_list])


async def execute_init() -> None:
    """执行初始化插件函数"""
    await execute_asyncio_task(init_plugin_funcs)


async def run_repeat():
    """执行重复任务"""
    # 为字典中的每一个函数创建一个循环特定时间的任务
    tasks = []
    for func, time in repeat_funcs.items():
        tasks.append(repeat_task(func, time))
    # 并发执行所有任务
    await asyncio.gather(*tasks)


async def safe_jump():
    """安全跳出重复任务"""
    try:
        main_task.cancel()
    except NameError:
        return


main_task: asyncio.Task


@dataclass(order=True)
class command_message_info:
    """命令消息信息"""

    name: str
    message: str


@dataclass(order=True)
class player_name:
    """玩家名字"""

    playername: str


@dataclass(order=True)
class player_message_info(player_name):
    """玩家消息信息"""

    message: str


@dataclass(order=True)
class player_death_info(player_name):
    """玩家死亡信息"""

    message: str
    killer: str | None = None


async def execute_repeat() -> None:
    """执行重复任务"""
    # skipcq: PYL-W0603
    global main_task
    main_task = asyncio.create_task(run_repeat())
    try:
        await main_task
    except asyncio.CancelledError:
        Print.print_suc("重复任务 repeat_task 已退出！")


async def execute_player_message(playername: str, message: str) -> None:
    """执行玩家消息处理函数

    Args:
        playername (str): 玩家名字
        message (str): 消息
    """
    await execute_asyncio_task(
        player_message_funcs,
        player_message_info(playername=playername, message=message),
    )


async def execute_death_message(
    playername: str, killer: str | None, message: str
) -> None:
    """执行玩家死亡处理函数

    Args:
        playername (str): 玩家名字
        killer (str | None): 凶手
        message (str): 消息
    """
    await execute_asyncio_task(
        player_death_funcs,
        player_death_info(playername=playername, killer=killer, message=message),
    )


async def execute_player_join(playername: str) -> None:
    """执行玩家加入处理函数

    Args:
        playername (str): 玩家名字
    """
    await execute_asyncio_task(player_join_funcs, player_name(playername=playername))


async def execute_player_prejoin(playername: str) -> None:
    """执行玩家加入前处理函数

    Args:
        playername (str): 玩家名字
    """
    await execute_asyncio_task(player_prejoin_funcs, player_name(playername=playername))


async def execute_player_left(playername: str) -> None:
    """执行玩家离开处理函数

    Args:
        playername (str): 玩家名字
    """
    await execute_asyncio_task(player_left_funcs, player_name(playername=playername))


async def execute_command_say(name: str, message: str) -> None:
    """执行命令消息处理函数

    Args:
        message (str): 消息 say
    """
    await execute_asyncio_task(
        commmand_message_funcs, command_message_info(name=name, message=message)
    )


async def execute_frame_exit() -> None:
    """执行框架退出处理函数"""
    await execute_asyncio_task(frame_exit_funcs)


class PluginMetadata:
    """插件元数据"""

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


def create_plugin_metadata(metadata_dict: dict) -> PluginMetadata:
    """创建插件元数据

    Args:
        metadata_dict (dict): 插件元数据字典

    Returns:
        PluginMetadata: 插件元数据
    """
    name = metadata_dict.get("name", "未命名插件")
    version = metadata_dict.get("version", "1.0")
    description = metadata_dict.get("description", "未知插件")
    usage = metadata_dict.get("usage", "")
    author = metadata_dict.get("author", "未知")
    homepage = metadata_dict.get("homepage", "")

    return PluginMetadata(name, author, description, version, usage, homepage)


async def load_plugin_file(file: str) -> PluginMetadata:
    """加载插件文件

    Args:
        file (str): 插件文件名

    Returns:
        PluginMetadata: 插件元数据
    """
    try:
        # 导入插件模块
        sys.path.append(os.path.join("插件文件", "ToolDelta注入式插件"))
        plugin_module = importlib.import_module(file)
        meta_data = create_plugin_metadata(
            getattr(plugin_module, "__plugin_meta__", {"name": file})
        )
        # 获取插件元数据
        return meta_data
    except PluginAPIVersionError as err:
        Print.print_err(
            f"插件 {file} 加载出现问题：需要 {err.name} 的 API 最低版本为 {err.m_ver}, 实际上只有 {err.n_ver}"
        )
        raise
    except PluginAPINotFoundError as err:
        Print.print_err(f"插件 {file} 加载出现问题：需要前置插件 API {err.name}")
        raise


async def load_plugin(plugin_grp: "PluginGroup") -> None:
    """加载插件

    Args:
        plugin_grp (PluginGroup): 插件组
    """
    tasks = []

    # 读取本目录下的文件夹名字
    PLUGIN_PATH = os.path.join(os.getcwd(), "插件文件", "ToolDelta注入式插件")
    for file in os.listdir(PLUGIN_PATH):
        if not plugin_is_enabled(file):
            continue
        if os.path.isdir(os.path.join(PLUGIN_PATH, file)):
            plugin_grp.injected_plugin_loaded_num += 1
            plugin_grp.loaded_plugins_name.append(file)
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
            f"成功载入插件 {metadata.name} 版本：{metadata.version} 作者：{metadata.author}"
        )
