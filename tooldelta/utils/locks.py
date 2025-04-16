from collections.abc import Callable
from threading import Lock

from . import fmts
from .tooldelta_thread import ThreadExit


class ChatbarLock:
    """
    聊天栏锁, 用于防止玩家同时开启多个聊天栏对话

    调用了该锁的所有代码, 在另一个进程使用该锁的时候, 尝试调用其他锁会导致进程直接退出, 直到此锁退出为止

    示例(以类式插件为例):
    ```python
    class MyPlugin(Plugin):
        ...
        def on_player_message(self, player: str, msg: str):
            with ChatbarLock(player):
                # 如果玩家处在另一个on_player_message进程 (锁环境) 中
                # 则在上面就会直接引发 SystemExit
                ...
    ```
    """

    __slots__ = ("oth_cb", "player")

    def __init__(self, player: str, oth_cb: Callable[[str], None] = lambda _: None):
        self.player = player
        self.oth_cb = oth_cb

    def __enter__(self):
        if self.player in players_in_chatbar_lock:
            self.oth_cb(self.player)
            fmts.print_war(f"玩家 {self.player} 的线程锁正在锁定状态")
            raise ThreadExit
        if self.player not in players_in_chatbar_lock:
            players_in_chatbar_lock.append(self.player)

    def __exit__(self, *_):
        players_in_chatbar_lock.remove(self.player)


class BotActionLock:
    """
    机器人行动锁, 用于防止多个线程同时使用机器人与游戏交互, 造成错误
    """

    __slots__ = ("name", "when_locked")

    def __init__(self, lock_name: str, when_locked: Callable[[], None] | None = None):
        """
        Args:
            lock_name (str): 行动锁名

        Args:
            lock_name (str): _description_
            when_locked (Callable[[], None] | None, optional): _description_. Defaults to None.
        """
        global bot_action_lock_current_name
        bot_action_lock_current_name = lock_name
        self.name = lock_name
        self.when_locked = when_locked

    def __enter__(self):
        locked = bot_action_lock.locked()
        if locked:
            fmts.print_war(f"[BotAction] {self.name} 与 {bot_action_lock_current_name} 冲突")
        if locked and self.when_locked is not None:
            self.when_locked()
        else:
            bot_action_lock.acquire()

    def __exit__(self, *_):
        if bot_action_lock.locked():
            bot_action_lock.release()


players_in_chatbar_lock: list[str] = []
bot_action_lock = Lock()
bot_action_lock_current_name = ""
