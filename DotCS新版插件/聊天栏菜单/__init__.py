addPluginAPI: type
PluginAPI: type
add_plugin: type
Plugin: type
plugins: type

@addPluginAPI("chatbar_menu", (0, 0, 1))
class ChatbarMenuAPI(PluginAPI):
    chatbar_trigger = []
    def __init__(this, frame):
        pass

    def add_trigger(this, triggers: list[str], argument_hint: str, usage: str, func,):
        if not isinstance(triggers, list):
            raise TypeError
        for tri in triggers:
            if not tri.startswith("."):
                triggers[triggers.index(tri)] = "." + tri
        this.chatbar_trigger.append([triggers, argument_hint, usage, func])

@add_plugin
class ChatbarMenu(Plugin):
    name = "聊天栏菜单"
    author = "SuperScript"
    version = (0, 0, 1)
    def __init__(this, frame):
        this.game_ctrl = frame.get_game_control()
        this.chatbar = plugins.getPluginAPI("chatbar_menu")

    def on_player_message(this, player: str, msg: str):
        if msg == ".help":
            for triggers, usage, argument_hint, func in this.chatbar.chatbar_trigger:
                this.game_ctrl.say_to(player, f" {' / '.join(triggers)}{' ' + argument_hint if argument_hint else ''}  §7§o{usage}")
        elif msg.startswith("."):
            for triggers, _, _, func in this.chatbar.chatbar_trigger:
                if msg.split()[0] in triggers:
                    args = msg.split()
                    if len(args) == 1:
                        args = []
                    else:
                        args = args[1:]
                    func(player, args)

    def on_player_join(this, player):
        print(player)