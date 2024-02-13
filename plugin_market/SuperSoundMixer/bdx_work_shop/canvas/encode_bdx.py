import sys
import os
import brotli
import struct
import json
import base64
from hashlib import sha256
import requests


class BdxEncoder(object):
    # command block
    CB = 'command_block'
    # repeat command block
    REPEAT_CB = 'repeating_command_block'
    # chain commnad block
    CHAIN_CB = 'chain_command_block'

    MODE_CB = 0
    MODE_REPEAT_CB = 1
    MODE_CHAIN_CB = 2

    # face down
    FACE_DOWN = 0
    FACE_UPPER = 1
    # z--
    FACE_NORTH = 2
    FACE_ZNN = 2
    # z++
    FACE_SOUTH = 3
    FACE_ZPP = 3
    # x--
    FACE_WEST = 4
    FACE_XNN = 4
    # x++
    FACE_EAST = 5
    FACE_XPP = 5

    cb_mode = ['Impulse', 'Repeat', 'Chain']
    cb_face = [
        'down', 'up', 'north (z-)', 'source (z+)', 'west (x-)', 'east (x+)'
    ]

    def __init__(self,
                 author=None,
                 need_sign=True,
                 sign_token=None,
                 log_path=None,
                 log_level=None) -> None:
        super().__init__()
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
        self.sign_api = 'https://uc.fastbuilder.pro/signbdx.web'

        self.author = author
        self.need_sign = need_sign
        if os.environ.get('HOME'):
            HOME=os.environ['HOME']
        elif os.environ.get('HOMEPATH'):
            HOME=os.environ['HOMEPATH']
        else:
            print("cannot find user home, you may encounter error")
            HOME="$HOME"
        self.token = os.path.join(HOME,
                                  '.config/fastbuilder/fbtoken')
        if sign_token is not None:
            self.token = sign_token
        self.block_name_id_mapping = {}
        self.block_id_name_mapping = []
        self.bdx_cmd_bytes = []

        self._need_log = True
        self.line_no = 0
        self.log_level = {
            'RESERVED': 1,
            'DEPRECATED': 1,
            'cache': 1,
            'place_block': 1,
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

        self.log_file = None
        if log_path is not None:
            self.log_file = open(log_path, 'w+')
        else:
            print('encoder log file not set, send to screen')

        self.log_off = False

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

    def log(self, *args, **kwargs):
        if self.log_off:
            return
        if self._need_log:
            print(*args, **kwargs, file=self.log_file)

    def log_bytes(self, bytes):
        if self.log_off:
            return
        if self._need_log:
            self.log(str(bytes)[2:-1], end='')

    def log_cmd_args(self, str_in, new_line=False):
        if self.log_off:
            return
        if self._need_log:
            if new_line:
                self.log(f'\n{"":<7s}        {"":20s}{str_in:40s}:', end='')
            else:
                self.log(f'{str_in:40s}:', end='')

    def log_cmd_op(self, op_code, str_in, new_line=True):
        if self.log_off:
            return
        if self._need_log:
            self.line_no += 1
            if new_line:
                self.log(
                    f'\n{self.line_no:<7d} [{hex(op_code):4s}] {str_in:20s}',
                    end='')
            else:
                self.log(
                    f'{self.line_no:<7d} [{hex(op_code):4s}] {str_in:20s}',
                    end='')

    def _write_val(self, val, l=2, b=True, s=False):
        "[l][b][s] len, big_edian, sign"
        bytes = struct.pack(self.dtype_len_fmt[l][b][s], val)
        self.log_bytes(bytes)
        self.bdx_cmd_bytes.append(bytes)
        return self

    def _write_op(self, op):
        bytes = struct.pack('B', op)
        self.bdx_cmd_bytes.append(bytes)
        return self

    def _write_Byte(self, val):
        self._write_val(val, l=1, s=False)

    def _write_byte(self, val):
        self._write_val(val, l=1, s=True)

    def _write_uint_16(self, val):
        self._write_val(val, l=2, s=False)

    def _write_int_16(self, val):
        self._write_val(val, l=2, s=True)

    def _write_uint_32(self, val):
        self._write_val(val, l=4, s=False)

    def _write_int_32(self, val):
        self._write_val(val, l=4, s=True)

    def _write_uint_64(self, val):
        self._write_val(val, l=8, s=False)

    def _write_int_64(self, val):
        self._write_val(val, l=8, s=True)

    def _write_str(self, in_str):
        bytes = in_str.encode(encoding='utf-8') + b'\x00'
        self.log_bytes(bytes)
        self.bdx_cmd_bytes.append(bytes)

    def encode(self,
               cmds=[],
               palette=None,
               author=None,
               need_sign=None,
               sign_token=None):
        if author is not None:
            self.author = author
        if need_sign is None:
            need_sign = self.need_sign
        if self.author is None:
            self.need_sign = False
            print('author not set, cannot sign')
        if sign_token is None:
            token = self.token
        if palette is None:
            palette=[]
        self.bdx_cmd_bytes = []
        self.line_no = 0
        self.write_cmds(cmds, palette)
        return self.post_process(self.bdx_cmd_bytes, need_sign, token)

    def sign(self, file_content, token):
        hash_hex = sha256(file_content).hexdigest()
        body = '{"hash": "' + hash_hex + '", "token": "' + token + '"}'
        response = requests.post(
            self.sign_api,
            data=body,
            headers={"User-Agent": "PhoenixBuilder/General"})
        response_json = response.json()
        if response_json['success'] == True:
            return base64.b64decode(response_json['sign'])
        else:
            raise ValueError('sign fail,response is: ' + response.text)

    def get_op_table(self):
        return {
            1: ('cache', 'addToBlockPalette', self.add_to_block_palette),
            2: ('DEPRECATED', 'addX', self.DEPRECATED),
            3: ('DEPRECATED', 'X++', self.DEPRECATED),
            4: ('DEPRECATED', 'addY', self.DEPRECATED),
            5: ('DEPRECATED', 'Y++', self.DEPRECATED),
            6: ('add_unsigned', 'addZ', self.add_unsigned),
            7: ('place_block', 'placeBlock', self.place_block),
            8: ('shift', 'Z++', self.shift),
            9: ('nop', 'NOP', self.nop),
            10: ('DEPRECATED', 'jumpX', self.DEPRECATED),
            11: ('DEPRECATED', 'jumpY', self.DEPRECATED),
            12: ('add_unsigned_big', 'jumpZ', lambda: self.add_unsigned_big),
            13: ('RESERVED', 'RESERVED', self.RESERVED),
            14: ('shift', '*X++', self.shift),
            15: ('shift', '*X--', self.shift),
            16: ('shift', '*Y++', self.shift),
            17: ('shift', '*Y--', self.shift),
            18: ('shift', '*Z++', self.shift),
            19: ('shift', '*Z--', self.shift),
            20: ('add', '*addX', self.add),
            21: ('add_big', '*addBigX', self.add_big),
            22: ('add', '*addY', self.add),
            23: ('add_big', '*addBigY', self.add_big),
            24: ('add', '*addZ', self.add),
            25: ('add_big', '*addBigZ', self.add_big),
            26: ('assign_command_block_data', 'assignCommandBlockData',
                 self.assign_command_block_data),
            27: ('place_command_block_with_data', 'placeCommandBlockWithData',
                 self.place_command_block_with_data),
            28: ('add_small', 'addSmallX', self.add_small),
            29: ('add_small', 'addSmallY', self.add_small),
            30: ('add_small', 'addSmallZ', self.add_small),
        }

    def place_block(self, block, block_data):
        if isinstance(block, str):
            block_id = self.add_to_block_palette(block)
        else:
            block_id = block
        if self._need_log:
            block_name = self.block_id_name_mapping[block_id]
            self.log_cmd_args(f'place {block_name}[{block_id}]({block_data})')
        self._write_uint_16(block_id)
        self._write_uint_16(block_data)

    def nop(self):
        pass

    def add_unsigned(self, offset):
        self.log_cmd_args(f'offset (unsigned) {offset}')
        self._write_uint_16(offset)

    def add_unsigned_big(self, offset):
        # here fb use int(int32(binary.BigEndian.Uint32()))
        # to conver it triple times, but we use sign=true
        self.log_cmd_args(f'offset (unsigned big) {offset}')
        self._write_val(offset, l=4, s=False)

    def shift(self):
        pass

    def add_small(self, offset):
        self.log_cmd_args(f'offset (small,1) {offset}')
        self._write_byte(offset)

    def add(self, offset):
        self.log_cmd_args(f'offset (medium,2) {offset}')
        self._write_int_16(offset)

    def add_big(self, offset):
        self.log_cmd_args(f'offset (big,4) {offset}')
        self._write_int_32(offset)

    def assign_command_block_data(self,
                                  cb_mode,
                                  command='',
                                  cb_name='',
                                  lastout='',
                                  tick_delay=0,
                                  first_tick=False,
                                  track_out=False,
                                  conditional=False,
                                  redstone=False):
        self._write_val(cb_mode, l=4)
        self.log_cmd_args(f'command={command}', new_line=True)
        self._write_str(command)
        self.log_cmd_args(f'cb_name={cb_name}', new_line=True)
        self._write_str(cb_name)
        self.log_cmd_args(f'lastout={lastout}', new_line=True)
        self._write_str(lastout)
        self.log_cmd_args(
            f'delay={tick_delay}, first_tick={first_tick}, track_out={track_out}, conditional={conditional}, redstone={redstone}',
            new_line=True)
        self._write_val(tick_delay, l=4, s=True)
        self._write_Byte(1 if first_tick else 0)
        self._write_Byte(1 if track_out else 0)
        self._write_Byte(1 if conditional else 0)
        self._write_Byte(1 if redstone else 0)

    def place_command_block_with_data(self,
                                      block=None,
                                      block_val=FACE_DOWN,
                                      cb_mode=None,
                                      command='',
                                      cb_name='',
                                      lastout='',
                                      tick_delay=0,
                                      first_tick=False,
                                      track_out=False,
                                      conditional=False,
                                      redstone=False):
        assert block is not None or cb_mode is not None, 'must set block or mode'
        block_id, block_name = None, None
        if block is None:
            block = [self.CB, self.REPEAT_CB, self.CHAIN_CB][cb_mode]
        if isinstance(block, str):
            block_id = self.add_to_block_palette(block)
            block_name = block
        else:
            block_id = block
        if cb_mode is None:
            cb_mode = {
                self.CB: self.MODE_CB,
                self.REPEAT_CB: self.MODE_REPEAT_CB,
                self.CHAIN_CB: self.CHAIN_CB
            }[block_name]
        if self._need_log:
            block_name = self.block_id_name_mapping[block_id]
            mode_name = self.cb_mode[cb_mode]
            self.log_cmd_args(
                f'place {block_name}[{block_id}]({block_val}) mode={mode_name}'
            )
        self._write_uint_16(block_id)
        self._write_uint_16(block_val)
        self._write_val(cb_mode, l=4)
        self.log_cmd_args(f'command={command}', new_line=True)
        self._write_str(command)
        self.log_cmd_args(f'cb_name={cb_name}', new_line=True)
        self._write_str(cb_name)
        self.log_cmd_args(f'lastout={lastout}', new_line=True)
        self._write_str(lastout)
        self.log_cmd_args(
            f'delay={tick_delay}, first_tick={first_tick}, track_out={track_out}, conditional={conditional}, redstone={redstone}',
            new_line=True)
        self._write_val(tick_delay, l=4, s=True)
        self._write_Byte(1 if first_tick else 0)
        self._write_Byte(1 if track_out else 0)
        self._write_Byte(1 if conditional else 0)
        self._write_Byte(1 if redstone else 0)

    def RESERVED(self):
        raise NotImplementedError(
            "RESERVED command, shouldn't be used by your program")

    def DEPRECATED(self):
        raise NotImplementedError("(DEPRECATED)!")

    def post_process(self, bdx_cmd_bytes, need_sign, token):
        bdx_cmd_bytes = b''.join(bdx_cmd_bytes)
        bdx_bytes = b'BDX\x00' + bdx_cmd_bytes
        if need_sign:
            if os.path.exists(self.token):
                with open(self.token, 'r') as f:
                    token = f.read()
            else:
                assert isinstance(token, str),f'token is {token}'
            sign_bytes = self.sign(bdx_bytes, token)
            sign_len = len(sign_bytes)
            len_bytes = struct.pack('B', sign_len)
            tail = struct.pack('B', 88) + sign_bytes + len_bytes + struct.pack(
                'B', 90)
            bdx_bytes = bdx_bytes + tail
            self.bdx_cmd_bytes = bdx_cmd_bytes
            self.bdx_bytes = bdx_cmd_bytes + tail
        else:
            bdx_bytes = bdx_bytes + b'XE'
            self.bdx_cmd_bytes = bdx_cmd_bytes
            self.bdx_bytes = bdx_cmd_bytes + b'XE'
        return b'BD@' + brotli.compress(bdx_bytes, quality=6)

    def add_to_block_palette(self, block_name):
        if self.block_name_id_mapping.get(block_name) is not None:
            return self.block_name_id_mapping[block_name]
        else:
            block_id = len(self.block_id_name_mapping)
            if self.log_level['cache'] > 1:
                self.log_cmd_op(1, f'cache')
            self._write_op(1)
            if self.log_level['cache'] > 1:
                self.log_cmd_args(f'{block_name} as {block_id}')
            self.block_id_name_mapping.append(block_name)
            self.block_name_id_mapping[block_name] = block_id
            self._write_str(block_name)
        return block_id

    def write_cmd(self, op_code, op_group, op_name, op, params):
        if self.log_level[op_group] > 0:
            self._need_log = True
            if op_code == 26:
                op_name = 'assign CB + data'
            if op_code == 27:
                op_name = 'place CB + data'
            self.log_cmd_op(op_code, op_name)
        else:
            self._need_log = False
        if op_code != 1:
            # sometimes the block is already cached
            self._write_op(op_code)
        if params is None:
            op()
        elif isinstance(params, list) or isinstance(params, tuple):
            op(*params)
        elif isinstance(params, dict):
            op(**params)
        else:
            op(params)

    def write_cmds(self, cmds, palette):
        self.block_name_id_mapping = {}
        self.block_id_name_mapping = []
        self.bdx_cmd_bytes = []
        self.log(f'author : {self.author}\t[', end='')
        self._write_str(self.author)
        self.log(f']', end='')
        self.log_off = True
        for k, v in self.log_level.items():
            if v > 0:
                self.log_off = False
                break
        assert len(palette) == len(list(set(palette)))
        if palette is not None:
            self._need_log = self.log_level['cache'] > 1
            for block_name in palette:
                self.add_to_block_palette(block_name)

        # create look up table first
        op_name_code_mapping = {}
        op_code_name_mapping = {}
        for op_code, (op_group, op_name, op) in self.op_table.items():
            op_code_name_mapping[op_name] = op_code
            op_name_code_mapping[op_code] = op_name

        cmd0 = cmds[0]
        if len(cmd0) == 3:
            # op_code, op_name, params format
            for (op_code, _op_name, params) in cmds:
                op_group, op_name, op = self.op_table[op_code]
                assert _op_name == op_name, f'{_op_name} {op_name} mismatch'
                self.write_cmd(op_code, op_group, op_name, op, params)
        elif len(cmd0) == 2:
            if isinstance(cmd0[0], str):
                # op_name params format
                for (op_name, params) in cmds:
                    op_code = op_code_name_mapping[op_name]
                    op_group, op_name, op = self.op_table[op_code]
                    self.write_cmd(op_code, op_group, op_name, op, params)
            else:
                # op_code  params format
                for (op_code, params) in cmds:
                    op_group, op_name, op = self.op_table[op_code]
                    self.write_cmd(op_code, op_group, op_name, op, params)
        else:
            raise NotImplementedError("unsupport format")

        self._need_log = True
        print()


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('at least tell me what .json to encode')
        print('python3 thisfile.py rigmarole_in.json encoded.bdx log.txt')
        exit(0)

    in_json_name = sys.argv[1]
    out_bdx_name = 'encode_out.bdx'
    log_file_name = None

    if len(sys.argv) > 2:
        out_bdx_name = sys.argv[2]
    if len(sys.argv) > 3:
        log_file_name = sys.argv[3]

    encoder = BdxEncoder(need_sign=True,
                         log_path=log_file_name,
                         author='2401PT')
    encoder.log_nothing()
    encoder.log_command_block_only()

    with open(in_json_name, 'r') as f:
        data_to_write = json.load(f)

    cmds = data_to_write["cmds"]
    palette = None
    author = encoder.author
    fb_token = None
    # it is ok to include palette here or just in cmds
    # if 'palette' in data_to_write.keys():
    #     palette = data_to_write["palette"]
    if 'author' in data_to_write.keys():
        author = data_to_write["author"]
    if 'fb_token' in data_to_write.keys():
        fb_token = data_to_write['fb_token']
    bdx_bytes = encoder.encode(cmds=cmds,
                               author=author,
                               palette=palette,
                               sign_token=fb_token)

    with open(out_bdx_name, 'wb') as f:
        f.write(bdx_bytes)