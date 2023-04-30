Plugin: type
add_plugin: type
listen_packet: type

@add_plugin
class Geng(Plugin):
    name = "梗词回复"
    author = "SuperScript"
    version = (0, 0, 1)
    def __init__(this, frame):
        this.frame = frame
        this.game_ctrl = frame.get_game_control()

    def on_player_message(this, player, msg):
        match msg:
            case "你干嘛":
                this.game_ctrl.say_to(player, "你干嘛， 嗨嗨哟")