# Author: SuperScript
# Description: SuperSoundMixer
# PLUGIN TYPE: def
# if 1 == 0: from dotcs_editor import *  # 不可能加载成功的库! 仅供VSCode编辑时看着顺眼, 不要出现这么多未定义波浪线
import threading
import time
import os, traceback
import ujson as json
from json import JSONDecodeError
from .bdx_work_shop.canvas import Canvas
from .bdx_work_shop.canvas import irio
from collections import defaultdict
from .bdx_work_shop.artists.cmd_midi_music import Artist as MidiDo
from tooldelta import Print
from tooldelta.plugin_load import tellrawText, sendcmd, player_message

__plugin_meta__ = {
    "name": "音效器",
    "version": "0.0.1",
    "author": "SuperScript",
}


path = os.path.join("插件配置文件", "SuperSoundMixer"), os.path.join(
    "插件配置文件", "SuperSoundMixer", "SoundCmds"
)


if not os.path.isdir(path[0]):
    os.mkdir(path[0])
if not os.path.exists(path[1]):
    os.mkdir(path[1])
    with open(
        os.path.join("插件配置文件", "SuperSoundMixer", "readme.txt"),
        "w",
        encoding="utf-8",
    ) as txt:
        txt.write(
            """-SuperSoundMixer-
             - 本插件可用作租赁服命令方块播放音效的扩展：使用命令方块控制机器人向玩家播放音效或音乐.
             - 支持的音乐文件种类：.mid（MIDI）
             - 音乐文件放置的位置：   插件配置文件/SuperSoundMixer/
             - 详情请看使用说明"""
        )
        txt.close()


class SuperSoundMixer:
    def __init__(self):
        self.SuperSoundMixer_threadings_num: int = 0
        self.SuperSoundMixer_ThreadMusic = []

    def mixer_sound(
        self,
        sound_name,
        target="@p",
        instrument="note.pling",
        ignore_high=None,
        speed=1,
        loop=False,
    ):
        """使用这个函数以播放音乐: 会自动创建一个线程.
        >>> SuperSoundMixer.mixer_sound(音乐名: str, 播放目标: str, 乐器: str, 忽略高音: None | float, 音高倍率: float, 循环播放: bool)
        """
        sound_thread = threading.Thread(
            target=self.__mixer__,
            args=(sound_name, target, instrument, ignore_high, speed, loop),
        )
        sound_thread.start()

    def del_sound_thread(self, sound_name):
        """使用这个函数以停止一个音乐线程(音乐名)"""
        result = 0
        while sound_name in self.SuperSoundMixer_ThreadMusic:
            self.SuperSoundMixer_ThreadMusic.remove(sound_name)
            result += 1
        return result

    def __mixer__(
        self,
        sound_name,
        targ="@a",
        instrument="note.pling",
        ignore_high=None,
        speed=1,
        loop=False,
    ):
        self.SuperSoundMixer_threadings_num += 1
        self.SuperSoundMixer_ThreadMusic.append(sound_name)
        with open(
            "插件配置文件/SuperSoundMixer/SoundCmds/%s.txt" % sound_name,
            "r",
            encoding="utf-8",
        ) as music_txt:
            music_cmds = music_txt.read().split("\n")
            music_txt.close()
        while 1:
            lastTip = 0
            for i in music_cmds:
                try:
                    if not sound_name in self.SuperSoundMixer_ThreadMusic:
                        break  # 直接跳出线程
                    tip, _, note, vol = eval(i)
                    time.sleep((tip - lastTip) / 20 * (1 / speed))
                    if vol > 0:
                        if ignore_high:
                            if note < ignore_high:
                                sendcmd(
                                    "/execute {who} ~~~ playsound {ins} @s ~~~ {vol} {note}".format(
                                        who=targ,
                                        ins=instrument,
                                        vol=vol,
                                        note=note * speed,
                                    )
                                )
                        else:
                            sendcmd(
                                "/execute {who} ~~~ playsound {ins} @s ~~~ {vol} {note}".format(
                                    who=targ, ins=instrument, vol=vol, note=note * speed
                                )
                            )
                    lastTip = tip
                except:
                    pass  # 遇到音符读取错误的情况
            if not loop:
                break
            elif not sound_name in self.SuperSoundMixer_ThreadMusic:
                break  # 直接跳出线程
        self.SuperSoundMixer_threadings_num -= 1


def updateMidifile():
    for i in os.listdir("插件配置文件/SuperSoundMixer"):
        if i.endswith(".mid"):
            midi_input = "插件配置文件/SuperSoundMixer/" + i
            canvas = Canvas()
            p = canvas
            artist = MidiDo(canvas=canvas, y=p.y + 10)
            music_cmds = artist.convert_music_to_mc_sound(
                midi_input,
                instrumentes_mapping=defaultdict(
                    lambda: [(30, None), (127, "pling"), (128, None)]
                ),
            )
            with open(
                "插件配置文件/SuperSoundMixer/SoundCmds/%s.txt"
                % i.replace(".mid", ""),
                "w",
                encoding="utf-8",
            ) as musicfile:
                for tip, _ins, note, vol in music_cmds:
                    musicfile.write(
                        """({}, "{}", {}, {})""".format(tip, _ins, note, vol) + "\n"
                    )
            musicfile.close()
            os.remove("插件配置文件/SuperSoundMixer/" + i)


updateMidifile()
Print.print_war(
    "§bSuperSoundMixer>> §a打开 §e插件配置文件/SuperSoundMixer 文件夹 §a查看使用说明!."
)
time.sleep(0.5)


# 加载此插件后
# 可以使用如下示例方法直接向对象播放音乐:
# SuperSoundMixer.mixer_sound("C:/恶臭的BGM.mid", "@a[name=art]", "note.bass")
@player_message()
async def _(playername, msg):
    if playername.replace("§r", "").replace("§f", "") == "sound":
        exception: str = ""
        try:
            exception = "JSON语法有误"
            get_sound_data = json.loads(msg)
            exception = "缺少音效MIDI音乐名"
            midi_file = get_sound_data["name"]
            exception = "缺少播放对相:应是玩家名或mc的目标选择器"
            PlaySound_targ = get_sound_data["target"]
        except:
            tellrawText("@a", "§cSuperSoundMixer§f>> §4不正确的语法: %s." % exception)
            return
        finally:
            del exception
        try:
            if os.path.exists(
                "插件配置文件/SuperSoundMixer/SoundCmds/%s.txt"
                % get_sound_data["name"]
            ):
                try:
                    ignore_high = get_sound_data["ignore_pitch"]
                except KeyError:
                    ignore_high = None
                try:
                    pitch = get_sound_data["pitch"]
                except KeyError:
                    pitch = 1
                try:
                    instrument = get_sound_data["instrument"]
                except KeyError:
                    instrument = "note.pling"
                try:
                    instrument = get_sound_data["ignore_low"]
                except KeyError:
                    instrument = None
                if not "@" in PlaySound_targ:
                    Print.print_err(
                        "§cSuperSoundMixer§f>> %s -> %s" % (midi_file, PlaySound_targ)
                    )
                    # 音乐文件名(无mid后缀)   播放的对象         乐器                      忽略高音                   速度
            else:
                if os.path.exists(
                    "插件配置文件/SuperSoundMixer/%s.mid" % get_sound_data[2]
                ):
                    updateMidifile()
                    tellrawText("@a", "§cSuperSoundMixer§f>> §6文件正在初始化")
                else:
                    tellrawText("@a", "§cSuperSoundMixer§f>> §4音效MIDI文件不存在")
        except:
            print("SuperScript", traceback.format_exc())
