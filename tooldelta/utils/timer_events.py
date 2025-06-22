import threading
from typing import Any, TYPE_CHECKING
from collections.abc import Callable

from . import fmts
from .tooldelta_thread import ToolDeltaThread, thread_func

if TYPE_CHECKING:
    from typing import ParamSpec

    PT = ParamSpec("PT")

timer_event_stop = threading.Event()
timer_events_table: dict[int, list[tuple[str, Callable, tuple, dict, int]]] = {}
timer_event_lock = threading.Lock()


def timer_event(
    t: int, name: str | None = None, thread_priority=ToolDeltaThread.PLUGIN
):
    """
    将修饰器下的方法作为一个定时任务, 每隔一段时间被执行一次。
    注意: 请不要在函数内放可能造成堵塞的内容
    注意: 当方法被 timer_event 修饰后, 需要调用一次该方法才能开始定时任务线程!

    Args:
        seconds (int): 周期秒数
        name (Optional[str], optional): 名字, 默认为自动生成的

    ```python
        @timer_event(60, "定时问好")
        def greeting():
            print("Hello!")
        greeting()
    ```
    """

    def receiver(func: "Callable[PT, Any]") -> "Callable[PT, None]":
        def caller(*args, **kwargs):
            func_name = name or f"简易方法:{func.__name__}"
            timer_events_table.setdefault(t, [])
            timer_events_table[t].append(
                (func_name, func, args, kwargs, thread_priority)
            )

        return caller

    return receiver


def timer_events_clear():
    "清理所有定时任务"
    timer_event_lock.acquire()
    for k, funcs_args in timer_events_table.copy().items():
        for func_args in funcs_args:
            (_, _, _, _, priority) = func_args
            if priority != ToolDeltaThread.SYSTEM:
                timer_events_table[k].remove(func_args)
        if timer_events_table[k] == []:
            del timer_events_table[k]
    timer_event_lock.release()


def timer_event_boostrap():
    "启动定时任务, 请不要在系统调用以外调用"
    fmts.print_suc("已开始执行 ToolDelta定时任务 函数集.")
    _internal_timer_event_boostrap()


@thread_func("ToolDelta 定时任务", ToolDeltaThread.SYSTEM)
def _internal_timer_event_boostrap():
    timer = 0
    timer_event_stop.clear()
    while not timer_event_stop.is_set():
        timer_event_lock.acquire()
        for k, func_args in timer_events_table.copy().items():
            if timer % k == 0:
                for _, caller, args, kwargs, _ in func_args:
                    caller(*args, **kwargs)
        timer_event_lock.release()
        timer_event_stop.wait(1)
        timer += 1
