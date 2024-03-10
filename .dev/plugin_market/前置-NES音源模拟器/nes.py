from tooldelta import Plugin, Frame, plugins

@plugins.add_plugin_as_api("NES音源模拟器")
class NES_Music_Studio(Plugin):
    name = "前置-NES音源模拟器"
    author = "SuperScript"
    version = (0, 0, 1)

    class SoundChip:
        channels_count = 0

        def format_seq(self, seqs):
            return []
        
        def playsound(self, seq, cmd_fmt):
            ...

    class C_2A03(SoundChip):
        ...

    def __init__(self, f: Frame):
        self.gc = f.get_game_control()
        self.frame = f