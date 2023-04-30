import time, json, os, threading, traceback
import mido, threading, ctypes

Plugin: type
add_plugin: type
listen_packet: type
plugins: type

class stoppable_thread(threading.Thread):
    class ThreadExit(Exception):...
    def __init__(this, func, args: tuple = (), **kwargs):
        super().__init__(target = func)
        this.func = func
        this.daemon = True
        this.all_args = [args, kwargs]
        this.start()

    def run(this):
        try:
            this.func(*this.all_args[0], **this.all_args[1])
        except this.ThreadExit:
            return
        except Exception as err:
            traceback.print_exc()

    def getThreadID(this):
        if hasattr(this, '_thread_id'):
            return this._thread_id
        for id, thread in threading._active.items():
            if thread is this:
                return id
                
    def stop(this):
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(this.getThreadID(), ctypes.py_object(this.ThreadExit))
        return res

class SuperMidiTranser:
    def __init__(this):
        [os.mkdir(d) if not os.path.isdir(d) else None for d in [
            f"data{os.sep}MIDIPlayer"
        ]]
        this.instrument_id_mapping = {} # 乐器名映射MC乐器
        this.channel: dict[str, list[int, int]] = {} # 音轨映射乐器
    # 下表感谢频道成员-玛卡巴卡
    ins_id_to_type = [
        [(0, 2), "note.harp", 66],
        [(2, 3), "note.pling", 66],
        [(3, 4), "note.harp", 66],
        [(4, 6), "note.pling", 66],
        [(6, 8), "note.harp", 66],
        [(8, 9), "note.share", 66],
        [(9, 10), "note.harp", 66],
        [(10, 11), "note.didgeridoo", 66],
        [(11, 12), "note.harp", 66],
        [(12, 13), "note.xylophone", 66],
        [(13, 14), "note.chime", 66],
        [(14, 16), "note.harp", 66],
        [(16, 17), "note.bass", 66],
        [(17, 23), "note.harp", 66],
        [(23, 31), "note.guitar", 66],
        [(31, 40), "note.bass", 66],
        [(40, 44), "note.harp", 66],
        [(44, 45), "note.iron_xylophone", 66],
        [(45, 46), "note.guitar", 66],
        [(46, 48), "note.harp", 66],
        [(48, 50), "note.guitar", 66],
        [(50, 52), "note.bit", 66],
        [(52, 54), "note.harp", 66],
        [(54, 55), "note.bit", 66],
        [(55, 64), "note.flute", 66],
        [(64, 68), "note.bit", 66],
        [(68, 69), "note.fulte", 66],
        [(69, 71), "note.harp", 66],
        [(71, 75), "note.fulte", 66],
        [(75, 80), "note.harp", 66],
        [(80, 104), "note.bit", 66],
        [(104, 105), "note.harp", 66],
        [(105, 106), "note.banjo", 66],
        [(106, 111), "note.harp", 66],
        [(111, 112), "note.guitar", 66],
        [(112, 113), "note.harp", 66],
        [(113, 114), "note.bell", 66],
        [(114, 115), "note.harp", 66],
        [(115, 116), "note.cow_bell", 66],
        [(116, 117), "note.basedrum", 66],
        [(117, 118), "note.bass", 66],
        [(118, 119), "note.bit", 66],
        [(119, 120), "note.basebrum", 66],
        [(120, 121), "note.guitar", 66],
        [(121, 125), "note.harp", 66],
        [(125, 126), "note.hat", 66],
        [(126, 127), "note.basedrum", 66],
        [(127, 128), "note.snare", 66]
    ]
    
    def findInstrument(this, program: int):
        res = this.instrument_id_mapping.get(str(program), None)
        if res:
            return res
        for ins in this.ins_id_to_type:
            if program in range(*ins[0]):
                this.instrument_id_mapping[str(program)] = [ins[1], ins[2]]
                return ins[1], ins[2]
        return "note.pling", 66

    def setChanInstrument(this, chan: int, instrument: int, std_note: int):
        this.channel[str(chan)] = [instrument, std_note]

    def translate(this, mid_file):
        note_cmds = []
        sum_time = 0
        for mid_msg in mido.MidiFile(filename=mid_file, clip=True):
            sum_time += mid_msg.time
            if mid_msg.type == "note_on" or mid_msg.type == "note_off":
                # mid_msg.channel; bytes() -> [_, note, vol]
                _, note, vol = mid_msg.bytes()
                noteoff = sum_time
                try:
                    use_instrument, std_note = this.channel[str(mid_msg.channel)]
                except KeyError:
                    use_instrument, std_note = "note.pling", 66
                    this.channel[str(mid_msg.channel)] = [use_instrument, std_note]
                pit = 2 ** ((note-std_note)/12)
                note_cmds.append([sum_time, use_instrument, pit, note, round(vol/128, 3), mid_msg.channel])

            elif mid_msg.type == "program_change":
                this.setChanInstrument(mid_msg.channel, *this.findInstrument(mid_msg.program))
                print(f"channel: {mid_msg.channel} is set: {this.findInstrument(mid_msg.program)}")

        return note_cmds

midi_transer = SuperMidiTranser()

@add_plugin
class MusicGameBootstrap(Plugin):
    name = "音乐播放器"
    author = "SuperScript"
    version = (0, 0, 3)
    def __init__(this, frame):
        this.frame = frame
        this.game_ctrl = frame.get_game_control()
        
    def on_def(this):
        this.menu = plugins.getPluginAPI("chatbar_menu", (0, 0, 1))
        this.menu.add_trigger(["play"], "播放音乐", "<音乐名>", this.invoked)

    def invoked(this, player, args):
        try:
            threading.Thread(target=this.start_menu, args=(args[0], player)).start()
        except IndexError:
            this.game_ctrl.say_to(player, "§c需要参数： 音乐名")
        except:
            pass

    def start_menu(this, name: str, playsound_player: str):
        try:
            filepath = f"MIDIPlayer/{name}" if ".mid" in name else f"data/MIDIPlayer/{name}.mid"
            try:
                this.game_ctrl.say_to(playsound_player, "§6插件非专业版， 需要先转换为指令组播放， 请稍等")
                music_notes = midi_transer.translate(filepath)
            except FileNotFoundError:
                this.game_ctrl.say_to(playsound_player, f"§c音乐名未找到， 请将mid文件放置于 omega_storage/side/MIDIPlayer 文件夹内: {name}")
                return
            duration = 0

            for sum_time, instrument, pitch, note, vol, chan in music_notes:
                instrument = "note.pling"
                pitch = round(pitch, 3)
                time.sleep(round(sum_time - duration, 3))
                pitch = "" if instrument == "note.snare" else pitch
                this.game_ctrl.sendcmd(f"/execute {playsound_player} ~~~ playsound {instrument} @a ~~~ {vol} {pitch}")
                duration = sum_time

        except Exception as err:
            this.game_ctrl.say_to(playsound_player, f"§c出错: {err}")
            import traceback
            traceback.print_exc()