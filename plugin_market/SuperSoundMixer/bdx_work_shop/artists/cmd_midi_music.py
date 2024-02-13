import collections
import os
from ..canvas import Canvas
import mido
from collections import defaultdict
# try:
#     from piano_transcription_inference import PianoTranscription, sample_rate, load_audio
# except:
#     print('you may need to install piano_transcription_inference first if you want programe convert your music to midi automatically ')


class Artist(Canvas):
    def __init__(self, canvas: Canvas, x=None, y=None, z=None):
        super().__init__()
        self.target_canvas = canvas
        self.target_xyz = {'ox': x, 'oy': y, 'oz': z}

        #   表示对应音效 最高阶，中间阶(为1时)，和最低阶，每一阶频率变换是 2^(1/12)
        self.instruments = {
            'bell':  (102, 90, 78),
            'harp': (78, 66, 54),
            'pling': (78, 66, 54),
            'bass':  (54, 42, 30),
            'guitar': (66, 54, 42),
            'bit': (78, 66, 54)   #-SuperScript: 加了这个就是打算把乐器加上一个正弦方波(音符盒绿宝石块演奏的音效)..
        }

        self.default_instrumentes_mapping=defaultdict(lambda :[
            (30,None),
            (54,'bass'),
            (78,'harp'),
            (102,'bell'),
            (128,None)
        ])

    def get_simple_music_represet(self, midi_msgs):
        # 所以按照 midi 的意思，不同的channel 可能是不同的乐器？
        # 那我还是先按照 channel 将 所有的 notes 分开吧
        channels_msgs = defaultdict(lambda: [])
        duration = 0.0
        for msg in midi_msgs:
            duration += msg.time
            if not (msg.type == 'note_on' or msg.type == 'note_off'):
                print(f'meta : {msg},ignored')
                continue
            else:
                # 怎么channel全是0 啊
                # print(msg.channel)
                dict_msg = {'channel': msg.channel,
                            'note': msg.bytes()[1],
                            'velocity': msg.bytes()[2],
                            'off': msg.type == 'note_off',
                            'time': duration}
                channels_msgs[msg.channel].append(dict_msg)
        print(f'duration : {duration:.2f}s')
        print(
            f'notes : {sum([len(notes) for notes in channels_msgs.values()])}')
        print(f'channels :{len(channels_msgs)}')
        return channels_msgs

    def align_note(self, notes_by_tick, tick, dict_note):
        # 这里会发生一个小问题，由于时间和游戏刻对齐了
        # 可能导致多个note挤在一个游戏刻里，
        # 所以我们需要处理这种情况
        note, velocity, time, note_off = dict_note['note'], dict_note[
            'velocity'], dict_note['time'], dict_note['off']

        if not (note, velocity, note_off) in notes_by_tick[tick]:
            notes_by_tick[tick].append((note, velocity, note_off))
        # if velocity > 0:
        #     for cmp_note in notes_by_tick[tick]:
        #         if cmp_note[1] == 0 and note in [n[0] for n in notes_by_tick[tick] if n[1] > 0]:
        #             notes_by_tick[tick-1].append(cmp_note)
        #             notes_by_tick[tick].remove(cmp_note)
        # else:
        #     for cmp_note in notes_by_tick[tick]:
        #         if cmp_note[1] == 0 and note in [n[0] for n in notes_by_tick[tick] if n[1] > 0]:
        #             notes_by_tick[tick+1].append(cmp_note)
        #             notes_by_tick[tick].remove(cmp_note)

    def translate_notes_in_one_channel_to_cmds(self, notes_by_tick, instruments):
        # 暂且先只考虑 高音部由 bell， 中音部由 piano/pling， 低音部由 bass 三个构成的组合吧
        cmds = []
        for tick, notes in notes_by_tick.items():
            for note, velocity, _ in notes:
                velocity /= 128
                for max_note,instrument_name in instruments:
                    if note < max_note:
                        if instrument_name is None:
                            print(f'cannot handle note: {note}')
                        else:
                            pitch = 2**((note-self.instruments[instrument_name][1])/12)
                            cmds.append((tick, instrument_name, pitch, velocity))
                            break
                # if note > 102 or note < 30:
                #     print(f'note too high/low, cannot handle {note}')
                #     continue
                # if note > 78:
                #     pitch = 2**((note-self.instruments['bell'][1])/12)
                #     cmds.append((tick, 'bell', pitch, velocity))
                # elif note < 54:
                #     pitch = 2**((note-self.instruments['bass'][1])/12)
                #     cmds.append((tick, 'bass', pitch, velocity))
                # else:
                #     pitch = 2**((note-self.instruments['harp'][1])/12)
                #     if pling:
                #         cmds.append((tick, 'pling', pitch, velocity))
                #     else:
                #         cmds.append((tick, 'harp', pitch, velocity))
        return cmds

    def convert_music_to_mc_sound(self, music_file: str, instrumentes_mapping=None):
        # 太多问题搞不明白了，暂且先只考虑 高音部由 bell， 中音部由 piano/pling， 低音部由 bass 三个构成的组合吧
        if instrumentes_mapping is None:
            instrumentes_mapping=self.default_instrumentes_mapping
        if not music_file.endswith('.mid'):
            file_name = os.path.split(music_file)[-1]
            if '.' in file_name:
                file_name = '.'.join(file_name.split('.')[:-1])
            file_name += '.mid'
            if os.path.exists(file_name):
                print(f'It seems that you have already convert tht music {music_file} to {file_name}')
            else:
                pass
            #     try:
            #         from piano_transcription_inference import PianoTranscription, sample_rate, load_audio
            #         import torch
            #         device = 'cuda' if torch.cuda.is_available() else 'cpu'
            #         print("Let's convert your file to midi first, so you can directly use it the next time")
            #     except:
            #         print('you may need to install piano_transcription_inference first if you want programe convert your music to midi automatically ')
            #         raise ImportError
            #     (audio, _) = load_audio(music_file, sr=sample_rate, mono=True)
            #     transcriptor = PianoTranscription(
            #         device=device, checkpoint_path=None)
            #     transcribed_dict = transcriptor.transcribe(audio, file_name)
            # midi_file = file_name
        else:
            midi_file = music_file
        channels_msgs = self.get_simple_music_represet(
            mido.MidiFile(midi_file, clip = True))

        # 在游戏的每个tick的所有note
        # mixed_notes_by_tick = defaultdict(lambda: [])
        all_note_cmds = []

        # 逐channel进行操作，按照midi的想法，理论上不同的channel可以用不同的乐器？
        # 但是我没有找到多个channel
        for channel_i, channel_msgs in channels_msgs.items():
            # 先看看这个channel 是什么情况，别到时候超了范围都不知道
            all_notes = [msg['note'] for msg in channel_msgs]
            max_note, min_note = max(all_notes), min(all_notes)
            print(
                f'channel {channel_i} max note : {max_note} min note : {min_note}')
            # 把所有同一个 tick 的 note 放在一起
            notes_by_tick = defaultdict(lambda: [])

            for dict_note in channel_msgs:
                time = dict_note['time']
                tick = round(time*20)/20
                # 这里会发生一个小问题，由于时间和游戏刻对齐了，可能导致多个note挤在一个游戏刻里，所以我们需要处理这种情况
                self.align_note(notes_by_tick, tick, dict_note)

            all_note_cmds += self.translate_notes_in_one_channel_to_cmds(
                notes_by_tick, instrumentes_mapping[channel_i])
        return sorted(all_note_cmds, key=lambda x: x[0])

    def write_to_cbs(self,
                     cmds,
                     cmds_wrapper="execute @a ~~~ playsound note.{} @s ~~~ {:.3f} {:.3f}",
                     x=None, y=None, z=None,
                     dir1=(1, 0, 0), dir2=(0, 0, 1), dir3=(0, 1, 0),
                     dir1_lim=8, dir2_lim=8,):

        cbs_array = [{'cb_mode': self.MODE_CB, 'command': '',
                      'cb_name': f'start', 'conditional': False, 'needRedstone': True}]
        current_tick = 0
        for tick, instrument, pitch, velocity in cmds:
            delay = tick-current_tick
            current_tick = tick
            cbs_array.append({'cb_mode': self.MODE_CHAIN_CB,
                              'cb_name': f'{tick/20:.2f}s',
                              'command': cmds_wrapper.format(instrument, velocity, pitch),
                              'tick_delay': delay})
        return self.snake_folding_cmds(x, y, z,
                                       dir1=dir1, dir2=dir2, dir3=dir3,
                                       dir1_lim=dir1_lim, dir2_lim=dir2_lim, array_is_cond_cb=None, cbs_array=cbs_array)
    def returnSelf(self):
        return self

    def to_canvas(self):
        self_host_ir = self.done()
        self.target_canvas.load_ir(self_host_ir, merge=True, **self.target_xyz)
        return self
