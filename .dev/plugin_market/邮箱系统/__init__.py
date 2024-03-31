from tooldelta import Plugin, plugins, Frame, Builtins, Config

JsonIO = Builtins.SimpleJsonDataReader


@plugins.add_plugin_as_api("邮箱系统")
class MailSystem(Plugin):
    class Mail:
        def __init__(
            self,
            title: str,
            sender: str,
            date: int,
            content: str,
            give_items: dict[str, tuple[int, int]] = None,
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

    def read_cfg(self):
        CFG_STD = {
            "收到邮件提示": str,
        }
        CFG_DEFAULT = {
            "收到邮件提示": "§7[§f!§7] §f收到新邮件: [邮件标题省略]"
        }
        self.cfg = Config.getPluginConfigAndVersion(
            self.name, CFG_STD, CFG_DEFAULT
        )
        self.mail_notice = self.cfg["收到邮件提示"]

    # ------- API ---------

    def add_func_hook(self, hook_name: str, func):
        self.hooks[hook_name] = func

    def send(self, who: str, mail: Mail):
        self._store_mail(who, mail)
        if who in self.gc.allplayers:
            self.gc.say_to(who, Builtins.SimpleFmt(
                {"[邮箱标题省略]": mail.title[:20] + "..",
                "[邮箱标题]": mail.title},
                self.mail_notice
            ))

    # -----------------------

    @staticmethod
    def _valid_name(name: str, it):
        counter = 0
        while name in it:
            counter += 1
            name = name.replace(f"({(counter - 1)})", "") +f"({counter})"
        return name

    def _store_mail(self, who: str, m: Mail):
        old = JsonIO.readFileFrom("邮箱系统-玩家邮箱", who, {})
        valid_name = self._valid_name(m.title)
        m.title = valid_name
        old[valid_name] = m.dump()
        JsonIO.writeFileTo("邮箱系统-玩家邮箱", who, old)

    def _execute_mail(self, who: str, mail: Mail):
        for itemid, (count, specid) in mail.give_items.items():
            self.gc.sendwocmd(f"/give @a[name={who}] {itemid} {count} {specid}")
        for cmd in mail.exec_cmds:
            self.gc.sendwocmd(Builtins.SimpleFmt({"[玩家名]": who}, cmd))
        for funchook, args in mail.func_hooks_and_args.items():
            self.hooks[funchook](*args)
