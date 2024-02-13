import os
from canvas import Canvas
from canvas import irio
from collections import defaultdict
from artists.cmd_midi_music import Artist as CmdMusicArtist

midi_input = 'data/Undertale.mid'
canvas_output = 'output/sample07/midi_music_output.bdx'
os.makedirs('output/sample07', exist_ok=True)

canvas = Canvas()
p = canvas


artist = CmdMusicArtist(canvas=canvas, y=p.y+10)

# 问题在于乐器的映射
# 这是默认的映射方式，所有通道一样处理
# 高音部由 bell， 中音部由 piano(harp) 低音部由 bass 三个构成的组合
music_cmds = artist.convert_music_to_mc_sound(
    midi_input,
    instrumentes_mapping=defaultdict(lambda :[     # 所有通道都采用一样的处理方式
            (30,None),                              # <30 不处理
            (54,'note.bass'),                            # 30~54 bass
            (78,'note.harp'),                            # 54~78 harp 钢琴
            (102,'note.bell'),                           # 78~102 bell
            (128,None)                              # 128< 不处理
        ])
)

# 中音部由 pling (电子琴) 构成
music_cmds = artist.convert_music_to_mc_sound(
    midi_input,
    instrumentes_mapping=defaultdict(lambda :[     # 所有通道都采用一样的处理方式
            # (30,None),                              
            (54,'note.bass'),                            # 0~54 bass
            (78,'note.pling'),                            # 54~78 pling 电子琴 
            (102,'note.bell'),                           # <78~102 bell
            # (128,None)                              
        ])
)


# 也可以接收音乐，会先将音乐转化为 midi
# music_cmds = artist.convert_music_to_mc_sound(music_input, pling=True)


artist.write_to_cbs(music_cmds, x=0, y=0, z=0,
                    dir1=(1, 0, 0), dir1_lim=16,
                    dir2=(0, 0, 1), dir2_lim=16,
                    dir3=(0, 1, 0), cmds_wrapper="execute @a ~~~ playsound {} @s ~~~ {:.3f} {:.3f}")
artist.to_canvas()

final_ir = canvas.done()
irio.dump_ir_to_bdx(final_ir, canvas_output, need_sign=True, author='2401PT')
