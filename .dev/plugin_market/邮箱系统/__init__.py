from tooldelta import Plugin, PluginAPI, plugins, Frame, Builtins

JsonIO = Builtins.SimpleJsonDataReader


@plugins.add_plugin_as_api("邮箱系统")
class MailSystem(Plugin, PluginAPI):
    class Mail:
        def __init__(
            self,
            title: str,
            sender: str,
            date: int,
            content: str,
            give_items: dict[str, int] = None,
            exe_cmds: list[str] = None,
            func_hooks_and_args: dict[str, tuple] = None,
        ):
            if give_items is None:
                give_items = {}
            if exe_cmds is None:
                exe_cmds = []
            if func_hooks_and_args is None:
                func_hooks_and_args = {}
            self.sender, self.title, self.date = sender, title, date
            self.content = content
            self.give_items = give_items
            self.exec_cmds = exe_cmds
            self.func_hooks_and_args = func_hooks_and_args

        def dump(self):
            return {
                "title": self.title,
                "sender": self.sender,
                "date": self.date,
                "content": self.content,
                "give_items": self.give_items,
                "exec_cmds": self.exec_cmds,
                "func_hooks_and_args": self.func_hooks_and_args,
            }

    def __init__(self, f: Frame):
        self.frame = f
        self.gc = f.get_game_control()
        self.hooks = {}

    def add_func_hook(self, hook_name: str, func):
        self.hooks[hook_name] = func

    def send(self, who: str, mail: Mail):
        self._store_mail(mail)

    @staticmethod
    def _valid_name(name: str, it):
        counter = 0
        while name in it:
            counter += 1
            name = name.replace("(%d)" % (counter - 1), "") + "(%d)" % counter
        return name

    def _store_mail(self, who: str, m: Mail):
        old = JsonIO.readFileFrom("邮箱系统-玩家邮箱", who, {})
        valid_name = self._valid_name(m.title)
        m.title = valid_name
        old[valid_name] = m.dump()
        JsonIO.writeFileTo("邮箱系统-玩家邮箱", who, old)
