import sys
import brotli
import struct
import json
import base64
from hashlib import sha256
import requests


class BdxDecoder(object):
    def __init__(self,
                 log_path=None,
                 need_verify=False,
                 log_level=None) -> None:
        self.log_file = None
        if log_path is not None:
            self.log_file = open(log_path, 'w')
        else:
            print('decoder log file not set, send to screen')
        self.log_level = {
            'RESERVED': 1,
            'DEPRECATED': 1,
            'cache': 1,
            'place_block': 0,
            'add_and_back': 1,
            'shift_and_back': 1,
            'add_unsigned': 1,
            'add_unsigned_big': 1,
            'shift': 1,
            'add_small': 1,
            'add': 1,
            'add_big': 1,
            'assign_command_block_data': 1,
            'place_command_block_with_data': 1,
            'nop': 1
        }
        if log_level is not None:
            self.log_level.update(log_level)

        # [l][b][s] len, big_edian, sign
        self.dtype_len_fmt = {
            1: {
                True: {
                    True: '>b',
                    False: '>B'
                },
                False: {
                    True: '<b',
                    False: '<B'
                }
            },
            2: {
                True: {
                    True: '>h',
                    False: '>H'
                },
                False: {
                    True: '<h',
                    False: '<H'
                }
            },
            4: {
                True: {
                    True: '>i',
                    False: '>I'
                },
                False: {
                    True: '<i',
                    False: '<I'
                }
            },
            8: {
                True: {
                    True: '>l',
                    False: '>L'
                },
                False: {
                    True: '<l',
                    False: '<L'
                }
            }
        }

        self.op_table = self.get_op_table()

        self.cb_mode = ['Impulse', 'Repeat', 'Chain']
        self.cb_face = [
            'down', 'up', 'north (z-)', 'source (z+)', 'west (x-)', 'east (x+)'
        ]
        # x axis, y axis, z axis
        self.X, self.Y, self.Z = 0, 1, 2
        # move positive ++ move negative --
        self.P, self.N = 1, -1

        self.author = None,
        self.server_author = None

        self._need_log = True
        self.need_verify = need_verify
        self.verify_api = 'https://uc.fastbuilder.pro/verifybdx.web'

        self.curr = None
        self.pos = None
        self.cached_blocks = None
        # data after 'BDX\x00'  until file end
        self.bdx_bytes = None
        self.cmds = None

    def log_command_block_only(self):
        for k, v in self.log_level.items():
            self.log_level[k] = 0
        self.log_level.update({
            'assign_command_block_data': 1,
            'place_command_block_with_data': 1,
        })
        return self

    def log_nothing(self):
        for k, v in self.log_level.items():
            self.log_level[k] = 0
        return self

    def log_everthing(self):
        for k, v in self.log_level.items():
            self.log_level[k] = 1
        return self

    def decode(self, f, need_verify=None):
        self.curr = 0
        self.pos = [0, 0, 0]
        self.cached_blocks = []
        if need_verify is None:
            need_verify = self.need_verify
        self.bdx_bytes = self.preprocess(f, need_verify)
        self.cmds = self.read_cmds(need_verify)
        decode_out = {
            'author': self.author,
            'palette': self.cached_blocks,
            'last_pos': self.pos,
            'cmds': self.cmds
        }
        return decode_out

    def log(self, *args, **kwargs):
        if self._need_log:
            print(*args, **kwargs, file=self.log_file)

    def verify_bdx(self, file_content, sign):
        hash_hex = sha256(file_content).hexdigest()
        base64_sign = str(base64.b64encode(sign), 'ascii')

        body = '{"hash": "' + hash_hex + '", "sign": "' + base64_sign + '"}'
        response = requests.post(
            self.verify_api,
            data=body,
            headers={"User-Agent": "PhoenixBuilder/General"})
        response_json = response.json()
        if response_json['success']:
            return response_json['username']
        else:
            raise ValueError('verify fail' + response.text)

    def preprocess(self, f, need_verify):
        bdx_compressed_bytes = f.read()
        if not bdx_compressed_bytes[:3] == b'BD@':
            raise ValueError('head error')
        bdx_bytes = brotli.decompress(bdx_compressed_bytes[3:])
        if bdx_bytes[-1] == 90:
            self.log("file signed")
            lent = int(bdx_bytes[-2])
            sign = bdx_bytes[-lent - 2:-2]
            terminate_point = -lent - 2 - 1
            if bdx_bytes[terminate_point] == ord('X'):
                pass
            elif bdx_bytes[terminate_point - 1] == ord('X'):
                terminate_point -= 1
            else:
                raise ValueError
            if need_verify:
                self.server_author = self.verify_bdx(
                    bdx_bytes[:terminate_point], sign)
        else:
            self.log("file not signed")

        if not bdx_bytes[:4] == b'BDX\x00':
            raise ValueError('head error')
        bdx_bytes = bdx_bytes[4:]
        return bdx_bytes

    def _read_str(self):
        new_curr = self.curr
        while new_curr != len(self.bdx_bytes):
            if self.bdx_bytes[new_curr] == 0:
                break
            new_curr += 1
        prased_str = self.bdx_bytes[self.curr:new_curr].decode(
            encoding='utf-8')
        self.curr = new_curr + 1
        return prased_str

    def _get_val(self, l=2, b=True, s=False):
        "[l][b][s] len, big_edian, sign"
        buf = self.bdx_bytes[self.curr:self.curr + l]
        self.curr = self.curr + l
        return struct.unpack(self.dtype_len_fmt[l][b][s], buf)[0]

    def _get_be_uint_16(self):
        return self._get_val(2, True, False)

    def cache_block(self):
        block_name = self._read_str()
        block_id = len(self.cached_blocks)
        self.log(f'cache {block_name} as {block_id}')
        self.cached_blocks.append(block_name)
        return block_name

    def place_block(self):
        block_id = self._get_be_uint_16()
        block_name = self.cached_blocks[block_id]
        block_val = self._get_be_uint_16()
        self.log(f'{block_name}[{block_id}]({block_val})')
        return block_id, block_val

    def _get_op_code(self):
        op = self.bdx_bytes[self.curr]
        self.curr += 1
        return op

    def _print_pos(self, end='\n'):
        self.log(f"({self.pos[self.X]},{self.pos[self.Y]},{self.pos[self.Z]})",
                 end=end)

    def nop(self):
        return None

    def add_and_back(self, axis):
        """(DEPRECATED)! 
        first add offset to axis, and then set two other axis to 0"""
        self.log("(DEPRECATED)!")
        offset = self._get_be_uint_16()
        new_pos = self.pos[axis] + offset
        for a in [0, 1, 2]:
            if a != axis:
                self.pos[axis] = 0
            else:
                self.pos[axis] = new_pos
        self.log(f" offset: {offset} @ ", end="")
        self._print_pos()
        return offset

    def shift_and_back(self, axis):
        """(DEPRECATED)!
        first ++, and then set two other axis to 0"""
        self.log("(DEPRECATED)!")
        for a in [0, 1, 2]:
            if a != axis:
                self.pos[axis] += 1
            else:
                self.pos[axis] = 0
        self._print_pos()
        return None

    def add_unsigned(self, axis):
        offset = self._get_be_uint_16()
        self.pos[axis] += offset
        self.log(f" offset: {offset} @ ", end="")
        self._print_pos()
        return offset

    def add_unsigned_big(self, axis):
        # here fb use int(int32(binary.BigEndian.Uint32()))
        # to conver it triple times, but we use sign=true
        offset = int(self._get_val(l=4, s=False))
        self.pos[axis] += offset
        self.log(f" offset: {offset} @ ", end="")
        self._print_pos()
        return offset

    def RESERVED(self):
        raise NotImplementedError(
            "RESERVED command, shouldn't be used by your program")

    def DEPRECATED(self):
        raise NotImplementedError("(DEPRECATED)!")

    def SORRY(self):
        raise NotImplementedError("I'm so lazy, so have not been implemented")

    def shift(self, axis, d):
        self.pos[axis] += d
        self._print_pos()
        return None

    def add_small(self, axis):
        """wrap > 127||wrap < -127"""
        offset = int(self._get_val(l=1, s=True))
        self.pos[axis] += offset
        self.log(f" offset: {offset} @ ", end="")
        self._print_pos()
        return offset

    def add(self, axis):
        # here fb use int(int16(binary.BigEndian.Uint16()))
        # to conver it triple times, but we use sign=true
        offset = int(self._get_val(l=2, s=True))
        self.pos[axis] += offset
        self.log(f" offset: {offset} @ ", end="")
        self._print_pos()
        return offset

    def add_big(self, axis):
        # here fb use int(int32(binary.BigEndian.Uint32()))
        # to conver it triple times, but we use sign=true
        offset = int(self._get_val(l=4, s=True))
        self.pos[axis] += offset
        self.log(f" offset: {offset} @ ", end="")
        self._print_pos()
        return offset

    def assign_command_block_data(self):
        cb_mode = self._get_val(l=4)
        mode_name = self.cb_mode[cb_mode]
        command = self._read_str()
        cb_name = self._read_str()
        lastout = self._read_str()
        tick_delay = self._get_val(l=4, s=True)
        first_tick = self._get_val(l=1) == 1
        track_out = self._get_val(l=1) == 1
        conditional = self._get_val(l=1) == 1
        redstone = self._get_val(l=1) == 1
        self._print_pos()
        self.log(f'mode={mode_name}')
        self.log(f'command={command}')
        self.log(f'cb_name={cb_name}')
        self.log(f'lastout={lastout}')
        self.log(
            f'delay={tick_delay}, first_tick={first_tick}, track_out={track_out}, conditional={conditional}, redstone={redstone}\n'
        )
        return cb_mode, command, cb_name, lastout, tick_delay, first_tick, track_out, conditional, redstone

    def place_command_block_with_data(self):
        block_id = self._get_be_uint_16()
        block_name = self.cached_blocks[block_id]
        block_val = self._get_be_uint_16()
        cb_mode = self._get_val(l=4)
        mode_name = self.cb_mode[cb_mode]
        command = self._read_str()
        cb_name = self._read_str()
        lastout = self._read_str()
        tick_delay = self._get_val(l=4, s=True)
        first_tick = self._get_val(l=1) == 1
        track_out = self._get_val(l=1) == 1
        conditional = self._get_val(l=1) == 1
        redstone = self._get_val(l=1) == 1
        self._print_pos()
        self.log(f'{block_name}[{block_id}]({block_val}) mode={mode_name}')
        print(command)
        self.log(f'command={command}')
        self.log(f'cb_name={cb_name}')
        self.log(f'lastout={lastout}')
        self.log(
            f'delay={tick_delay}, first_tick={first_tick}, track_out={track_out}, conditional={conditional}, redstone={redstone}\n'
        )
        return block_id, block_val, cb_mode, command, cb_name, lastout, tick_delay, first_tick, track_out, conditional, redstone

    def get_op_table(self):
        return {
            1: ('cache', 'addToBlockPalette', self.cache_block),
            2: ('DEPRECATED', 'addX', self.DEPRECATED),
            3: ('DEPRECATED', 'X++', self.DEPRECATED),
            4: ('DEPRECATED', 'addY', self.DEPRECATED),
            5: ('DEPRECATED', 'Y++', self.DEPRECATED),
            6: ('add_unsigned', 'addZ', lambda: self.add_unsigned(self.Z)),
            7: ('place_block', 'placeBlock', self.place_block),
            8: ('shift', 'Z++', lambda: self.shift(self.Z, self.P)),
            9: ('nop', 'NOP', self.nop),
            10: ('DEPRECATED', 'jumpX', self.DEPRECATED),
            11: ('DEPRECATED', 'jumpY', self.DEPRECATED),
            12: ('add_unsigned_big', 'jumpZ',
                 lambda: self.add_unsigned_big(self.Z)),
            13: ('RESERVED', 'RESERVED', self.RESERVED),
            14: ('shift', '*X++', lambda: self.shift(self.X, self.P)),
            15: ('shift', '*X--', lambda: self.shift(self.X, self.N)),
            16: ('shift', '*Y++', lambda: self.shift(self.Y, self.P)),
            17: ('shift', '*Y--', lambda: self.shift(self.Y, self.N)),
            18: ('shift', '*Z++', lambda: self.shift(self.Z, self.P)),
            19: ('shift', '*Z--', lambda: self.shift(self.Z, self.N)),
            20: ('add', '*addX', lambda: self.add(self.X)),
            21: ('add_big', '*addBigX', lambda: self.add_big(self.X)),
            22: ('add', '*addY', lambda: self.add(self.Y)),
            23: ('add_big', '*addBigY', lambda: self.add_big(self.Y)),
            24: ('add', '*addZ', lambda: self.add(self.Z)),
            25: ('add_big', '*addBigZ', lambda: self.add_big(self.Z)),
            26: ('assign_command_block_data', 'assignCommandBlockData',
                 self.assign_command_block_data),
            27: ('place_command_block_with_data', 'placeCommandBlockWithData',
                 self.place_command_block_with_data),
            28: ('add_small', 'addSmallX', lambda: self.add_small(self.X)),
            29: ('add_small', 'addSmallY', lambda: self.add_small(self.Y)),
            30: ('add_small', 'addSmallZ', lambda: self.add_small(self.Z)),
        }

    def read_cmds(self, need_verify):
        bdx_bytes_len = len(self.bdx_bytes)
        decode_out = []
        self.author = self._read_str()
        self.log(f'author (in file):' + self.author)
        if need_verify:
            self.log(f'author (responsed by fb server):{self.server_author} ')
            if not self.author == self.server_author:
                ValueError('verify fail')
        self.log('cmd begin')
        line_no = 1
        while self.curr != bdx_bytes_len:
            op_code = self._get_op_code()
            if op_code == 88:
                self._need_log = True
                self.log('cmd end (end mark)')
                return decode_out
            op_group, op_name, op = self.op_table[op_code]
            if self.log_level[op_group] > 0:
                self._need_log = True
            else:
                self._need_log = False
            self.log(f"{line_no:<5d} {op_name:20s} :", end="")
            line_no += 1
            ret = op()
            decode_out.append((op_code, op_name, ret))
        self._need_log = True
        self.log('cmd end (reach border)')
        return decode_out


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('at least tell me what .bdx to decode')
        print(
            'python3 thisfile.py somebdx_in.bdx rigmarole_out.json readable_out.txt '
        )
        exit(0)

    in_bdx_name = sys.argv[1]
    out_file_name = 'decode_out.json'
    log_file_name = None

    if len(sys.argv) > 2:
        out_file_name = sys.argv[2]
    if len(sys.argv) > 3:
        log_file_name = sys.argv[3]

    decoder = BdxDecoder(log_file_name, need_verify=True)
    # decoder.log_command_block_only()

    with open(in_bdx_name, 'rb') as f:
        decode_out = decoder.decode(f)
        with open(out_file_name, 'w') as f:
            json.dump(decode_out, f)
