import ctypes
import threading
import traceback
from typing import Any, TypeVar, ParamSpec, Generic
from collections.abc import Callable
from . import fmts


PT = ParamSpec("PT")


VT = TypeVar("VT")
RT = TypeVar("RT")
threads_list: list["ToolDeltaThread"] = []


class ThreadExit(SystemExit):
    """线程退出"""


class ToolDeltaThread(threading.Thread, Generic[PT, RT]):
    "简化 ToolDelta 子线程创建的 threading.Thread 的子类"

    SYSTEM = 0
    PLUGIN = 1
    PLUGIN_LOADER = 2

    def __init__(
        self,
        func: Callable[PT, RT],
        args: tuple = (),
        usage="",
        thread_level=PLUGIN,
        **kwargs,
    ):
        """新建一个 ToolDelta 子线程

        Args:
            func (Callable): 线程方法
            args (tuple, optional): 方法的参数项
            usage (str, optional): 线程的用途说明
            thread_level: 线程权限等级
            kwargs (dict, optional): 方法的关键词参数项
        """
        super().__init__(target=func)
        self.func = func
        self.daemon = True
        self.all_args = (args, kwargs)
        self.usage = usage or f"fn:{func.__name__}"
        self.stopping = False
        self._thread_level = thread_level
        self._ret: RT | None = None
        self._ret_exc = None
        self._stop_event = threading.Event()
        self.start()

    def run(self) -> None:
        """线程运行方法"""
        threads_list.append(self)
        try:
            args, kwargs = self.all_args
            self._ret = self.func(*args, **kwargs)
        except (SystemExit, ThreadExit) as e:
            self._ret_exc = e
            pass
        except ValueError as e:
            self._ret_exc = e
            if str(e) != "未连接到游戏":
                fmts.print_err(
                    f"线程 {self.usage or self.func.__name__} 出错:\n"
                    + traceback.format_exc()
                )
            else:
                fmts.print_war(f"线程 {self.usage} 因游戏断开连接被迫中断")
        except Exception as e:
            self._ret_exc = e
            fmts.print_err(
                f"线程 {self.usage or self.func.__name__} 出错:\n"
                + traceback.format_exc()
            )
        finally:
            threads_list.remove(self)
            self._stop_event.set()
            del self.all_args

    def stop(self) -> bool:
        """终止线程 注意: 不适合在有长时间sleep的线程内调用"""
        self.stopping = True
        thread_id = self.ident
        if thread_id is None:
            return True
        if not self.is_alive():
            return True
        # 也许不会出现问题了吧
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
            ctypes.c_long(thread_id), ctypes.py_object(ThreadExit)
        )
        if res == 0:
            fmts.print_err(f"§c线程ID {thread_id} 不存在")
            return False
        elif res > 1:
            # 线程修改出问题了? 终止了奇怪的线程?
            # 回退修改
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, None)
            fmts.print_err(f"§c终止线程 {self.name} 失败")
            return False
        self._stop_event.set()
        return True

    def block_get_result(self) -> RT:
        self._stop_event.wait()
        if self._ret_exc:
            raise self._ret_exc
        return self._ret  # type: ignore

    def block_get_result_with_timeout(self, timeout: float) -> RT | None:
        self._stop_event.wait(timeout)
        return self._ret


createThread = ToolDeltaThread


def get_threads_list() -> list["createThread"]:
    """返回使用 createThread 创建的全线程列表。"""
    return threads_list


def thread_func(usage: str, thread_level=ToolDeltaThread.PLUGIN):
    """
    在事件方法可能执行较久会造成堵塞时使用，方便快捷地创建一个新线程，例如:
    ```python
    @thread_func("一个会卡一分钟的线程")
    def on_inject(self):
        ...
    ```
    """

    def _recv_func(
        func: "Callable[PT, RT]",
    ) -> "Callable[PT, ToolDeltaThread[PT, RT]]":
        def thread_fun(*args: Any, **kwargs):
            return ToolDeltaThread(
                func,
                usage=usage,
                thread_level=thread_level,
                args=args,
                **kwargs,
            )

        thread_fun._orig = func
        thread_fun._usage = usage

        return thread_fun

    return _recv_func


def thread_gather(
    funcs_and_args: list[tuple[Callable[..., VT], tuple]],
) -> list[VT]:
    r"""
    使用回调线程作为并行器的伪异步执行器
    可以用于并发获取多个阻塞方法的返回
    ```
    >>> results = thread_gather([
        (requests.get, ("https://www.github.com",)),
        (time.sleep, (1,)),
        (sum, (1, 3, 5))
    ])
    >>> results
    [<Response 200>, None, 9]
    ```

    Args:
        funcs_and_args (list[tuple[Callable[..., VT], tuple]]): (方法, 参数) 的列表
    Returns

    Returns:
        list[VT]: 方法的返回 (按传入方法的顺序依次返回其结果)
    """
    res: list[Any] = [None] * len(funcs_and_args)
    finish_events = [threading.Event() for _ in range(len(funcs_and_args))]
    for i, (func, args) in enumerate(funcs_and_args):

        def _closet(_i: int, _func):
            def _cbfunc(*args):
                try:
                    assert isinstance(args, tuple), "传参必须是 tuple 类型"
                    res[_i] = _func(*args)
                finally:
                    finish_events[_i].set()

            return _cbfunc

        fun, usage = _closet(i, func), f"并行方法 {func.__name__}"
        ToolDeltaThread(fun, args, usage=usage)
    for evt in finish_events:
        evt.wait()
    return res


def force_stop_normal_threads():
    "强制终止非系统级线程, 仅系统内部调用"
    for i in threads_list:
        if i._thread_level != i.SYSTEM:
            fmts.print_suc(f"正在终止线程 {i.usage}  ", end="\r")
            res = i.stop()
            if res:
                fmts.print_suc(f"已终止线程 <{i.usage}>    ")
            else:
                fmts.print_suc(f"无法终止线程 <{i.usage}>  ")
