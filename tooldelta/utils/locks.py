from collections.abc import Callable

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
    示例(以注入式插件为例):
    ```
    @player_message()
    async def onPlayerChat(info: player_message_info):
        with ChatbarLock(info.playername):
            ...
    ```
    """

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

    def __exit__(self, e, e2, e3):
        players_in_chatbar_lock.remove(self.player)


players_in_chatbar_lock: list[str] = []
