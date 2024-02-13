from .ir import IR
import numpy as np


class Canvas(object):
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
    FACE_UP = 1
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
    # clear block bid
    CLEAR = -1

    def __init__(self, ir=None):
        self.ir = ir
        if self.ir is None:
            self.ir = IR()
        self.x, self.y, self.z = 0, 0, 0
        self._tmp_matrix = []

        # 当值为true时，代表可能在同一个 xyz 有多个不同的方块
        self.matrix_changed = False

    def get_bid(self, block):
        if len(block) == 1:
            block = (block, 0, None)
        elif len(block) == 2:
            block = (*block, None)
        return self.ir.get_block_bid(block)

    def move_to(self, x=None, y=None, z=None):
        '''移动到指定的x,y,z，留空时保持位置不变'''
        self.x = self.x if x is None else x
        self.y = self.y if y is None else y
        self.z = self.z if z is None else z

    def _append_block(self, x=None, y=None, z=None, block=None, bid=None):
        '''为了提高效率，append 时不立刻更新 matrix，而是在commit时将多个append一起更新'''
        x = self.x if x is None else x
        y = self.y if y is None else y
        z = self.z if z is None else z
        if bid is None:
            bid = self.get_bid(block)
        self._tmp_matrix.append([x, y, z, bid])
        return self

    def _commit_append(self):
        '''提交前面append缓存的block'''
        if self._tmp_matrix == []:
            return
        tmp_matrix = np.array(self._tmp_matrix, dtype=np.int32).conjugate()
        self._tmp_matrix = []
        self.ir.ir_matrix = np.vstack([self.ir.ir_matrix, tmp_matrix])
        self.matrix_changed = True

    def commit_matrix(self):
        '''由于使用稀疏矩阵表示，一个位置(x,y,z)可能被多次赋值，以最后一次的值为准刷新整个稀疏矩阵，这个操作很耗时，单身如果有很多冗余的方块，后续操作可能变快'''
        if self.matrix_changed:
            self.ir.rearrange()
            self.matrix_changed = False
        return self

    def done(self):
        '''在导出之前，应该进行一次,以完成所有操作的提交'''
        if self._tmp_matrix != []:
            self._commit_append()
        if self.matrix_changed == True:
            self.commit_matrix()
        return self.ir

    def setblock(self, block_name='air', block_val=0,
                 x=None, y=None, z=None,
                 cb_data=None,
                 bid=None,
                 remove=False):
        ''' 在绝对坐标放置，留空为当前位置'''
        if remove:
            self._append_block(x, y, z, None, bid=-1)
        else:
            self._append_block(x, y, z,
                               (block_name, block_val, cb_data),
                               bid=bid)
        return self

    def place_command_block_with_data(self, x=None, y=None, z=None,
                                      block_name=None,
                                      facing=FACE_DOWN,
                                      cb_mode=MODE_CB,
                                      command='', cb_name='',
                                      tick_delay=0,
                                      execute_on_first_tick=False, track_output=False,
                                      conditional=False,
                                      needRedstone=False,
                                      ):
        assert block_name is not None or cb_mode is not None, 'must set block or mode'
        if block_name is None:
            block_name = [self.CB, self.REPEAT_CB, self.CHAIN_CB][cb_mode]
        if cb_mode is None:
            print(block_name)
            cb_mode = int({
                self.CB: self.MODE_CB,
                self.REPEAT_CB: self.MODE_REPEAT_CB,
                self.CHAIN_CB: self.MODE_CHAIN_CB
            }[block_name])
            print(cb_mode)
        cb_data = (cb_mode, command, cb_name, '', tick_delay,
                   execute_on_first_tick, track_output, conditional, needRedstone)
        self._append_block(x, y, z, (block_name, facing, cb_data))
        return self

    def load_ir(self, ir, ox=None, oy=None, oz=None, merge=True):
        '''
            merge 选项决定 bid 的处理方式， 
            为 False 时可能导致重复的bid，
            但是计算简化很多，
            为True时不会出现冗余的bid，但是慢一些
        '''
        # 应用之前的所有操作
        self._commit_append()
        # 从当前位置加载一个新的ir
        in_matrix, in_lookup, in_blocks = \
            ir.ir_matrix.copy(), ir.ir_lookup, ir.ir_blocks
        # 更新坐标
        ox = self.x if ox is None else ox
        oy = self.y if oy is None else oy
        oz = self.z if oz is None else oz
        # 更新 bid
        if not merge:
            bid_offset = len(self.ir.ir_blocks)
            # 更新
            in_matrix += [ox, oy, oz, bid_offset]
            # 合并 blocks
            self.ir.ir_blocks += in_blocks
            # 重新计算 lookup
            self.ir.rebuild_bid_lookup()
        else:
            bid_remapping = {}
            in_matrix += [ox, oy, oz, 0]
            for ri, (x, y, z, old_bid) in enumerate(in_matrix):
                new_bid = bid_remapping.get(old_bid)
                if new_bid is None:
                    block = in_blocks[old_bid]
                    new_bid = self.get_bid(block)
                    bid_remapping[old_bid] = new_bid
                in_matrix[ri, 3] = new_bid
        # 合并 matrix
        self.ir.ir_matrix = np.vstack([self.ir.ir_matrix, in_matrix])
        self.matrix_changed = True
        return self

    def fill(self, block_name='air', block_val=0,
             x=None, y=None, z=None,
             ex=None, ey=None, ez=None,
             cb_data=None,
             bid=None,
             remove=False):
        self._commit_append()
        if remove:
            bid = -1
        if bid is None:
            bid = self.get_bid((block_name, block_val, cb_data))
        x = self.x if x is None else x
        y = self.y if y is None else y
        z = self.z if z is None else z
        ex = self.x if ex is None else ex
        ey = self.y if ey is None else ey
        ez = self.z if ez is None else ez
        x, ex = min(x, ex), max(x, ex)
        y, ey = min(y, ey), max(y, ey)
        z, ez = min(z, ez), max(z, ez)
        lx, ly, lz = ex - x, ey - y, ez - z
        matrix = np.zeros((lx * ly * lz, 4), dtype=np.int32)
        matrix[:, 3] = bid
        matrix_view = matrix.view()
        matrix_view.shape = (lx * lz, ly, 4)
        matrix_view[:, :, 1] = np.arange(y, ey)
        matrix_view.shape = (lz, lx * ly, 4)
        matrix_view[:, :, 0] = np.arange(x, ex).repeat(ly)
        matrix[:, 2] = np.arange(z, ez).repeat(ly * lx)
        self.ir.ir_matrix = np.vstack([self.ir.ir_matrix, matrix])
        self.matrix_changed = True
        return self

    def replace_wordwide(self, ori_block, new_block):
        '''将整个工作区内一种方块替换成另一种'''
        self._commit_append()
        if isinstance(new_block, str):
            new_block = (new_block,)
        if isinstance(ori_block, str):
            ori_block = (ori_block,)
        new_blocks = []
        if isinstance(ori_block, int):
            # 使用bid选择原先方块
            ori_block = self.ir.ir_blocks[ori_block]
        if isinstance(ori_block, tuple):
            # 匹配名称，值和数据，尽量匹配
            for block in self.ir.ir_blocks:
                matched = True
                for _i, v in enumerate(ori_block):
                    if ori_block[_i] != block[_i]:
                        matched = False
                        break
                if matched:
                    _new_block = list(block)
                    for _i, v in enumerate(new_block):
                        _new_block[_i] = v
                    new_blocks.append(tuple(_new_block))
                else:
                    new_blocks.append(block)
        self.ir.rebuild_bid_lookup(new_blocks)
        return self

    def select(self, blocks=None, bids=None,
               sx=None, ex=None,
               sy=None, ey=None,
               sz=None, ez=None):
        '''获得工作区的一个结构切片'''
        self._commit_append()
        in_bids = bids
        in_blocks = blocks
        if bids is None:
            bids = []
        else:
            if isinstance(bids, int):
                bids = [bids]
        if blocks is None:
            blocks = []
        elif not isinstance(blocks, list):
            blocks = [blocks]
        for block in blocks:
            if isinstance(block, str):
                block = (block,)
            for i, ir_block in enumerate(self.ir.ir_blocks):
                matched = True
                for _i, v in enumerate(block):
                    if ir_block[_i] != block[_i]:
                        matched = False
                        break
                if matched:
                    bids.append(i)
        slice = np.ones_like(self.ir.ir_matrix[:, 0], dtype=bool)
        slice = slice if sx is None else slice & (self.ir.ir_matrix[:, 0] > sx)
        slice = slice if ex is None else slice & (self.ir.ir_matrix[:, 0] < ex)
        slice = slice if sy is None else slice & (self.ir.ir_matrix[:, 1] > sy)
        slice = slice if ey is None else slice & (self.ir.ir_matrix[:, 1] < ey)
        slice = slice if sz is None else slice & (self.ir.ir_matrix[:, 2] > sz)
        slice = slice if ez is None else slice & (self.ir.ir_matrix[:, 2] < ez)
        if (in_blocks is not None) or (in_bids is not None):
            matrix_bids = self.ir.ir_matrix[slice, 3]
            matrix_bids_slice = np.zeros_like(matrix_bids, dtype=bool)
            for bid in bids:
                matrix_bids_slice[matrix_bids == bid] = True
            slice[slice] = matrix_bids_slice
        if np.any(slice):
            return slice
        else:
            print('empty selection')
            return None

    def move(self, blocks=None, bids=None,
             sx=None, ex=None,
             sy=None, ey=None,
             sz=None, ez=None,
             offset_x=None, offset_y=None, offset_z=None):
        '''
        move 指令和游戏中的 clone/move 指令不同，指定的是offset，
        根本原因是，游戏使用矩阵表示区块内信息，而这里使用稀疏
        '''
        slice = self.select(blocks, bids, sx, ex, sy, ey, sz, ez)
        if slice is None:
            return self
        self.ir.ir_matrix[slice, :] += [offset_x, offset_y, offset_z, 0]
        return self

    def copy(self, blocks=None, bids=None,
             sx=None, ex=None,
             sy=None, ey=None,
             sz=None, ez=None,
             offset_x=None, offset_y=None, offset_z=None):
        slice = self.select(blocks, bids, sx, ex, sy, ey, sz, ez)
        if slice is None:
            return self
        increasement = self.ir.ir_matrix[slice, :].copy()
        increasement = increasement+[offset_x, offset_y, offset_z, 0]
        self.ir.ir_matrix = np.vstack([self.ir.ir_matrix, increasement])
        return self

    def replace(self, new_block, orig_blocks=None, orig_bids=None,
                sx=None, ex=None,
                sy=None, ey=None,
                sz=None, ez=None):
        '''注意，replace 和 replace wordwide 行为不同，新方块选择更接近游戏里的逻辑'''
        if isinstance(new_block, str):
            new_block = (new_block, 0, None)
        bid = self.get_bid(new_block)
        slice = self.select(orig_blocks, orig_bids, sx, ex, sy, ey, sz, ez)
        if slice is None:
            return self
        self.ir.ir_matrix[slice, 3] = bid
        return self

    def snake_folding_cmds(self, x=None, y=None, z=None,
                           dir1=(1, 0, 0), dir2=(0, 0, 1), dir3=(0, 1, 0),
                           dir1_lim=8, dir2_lim=8, array_is_cond_cb=None, cbs_array=None):
        x = self.x if x is None else x
        y = self.y if y is None else y
        z = self.z if z is None else z
        start_point = np.array([x, y, z])
        if array_is_cond_cb is None:
            array_is_cond_cb = []
            for cb in cbs_array:
                cond = cb.get('conditional')
                if cond is None or not cond:
                    array_is_cond_cb.append(False)
                else:
                    array_is_cond_cb.append(True)
        else:
            assert len(array_is_cond_cb) == len(cbs_array),\
                f'len(array_is_cond_cb)[{len(array_is_cond_cb)}]!=len(cbs_array)[{len(cbs_array)}]'
        dir1_lim, dir2_lim = abs(dir1_lim), abs(dir2_lim)
        dir1, dir2, dir3 = np.array(dir1), np.array(dir2), np.array(dir3)
        sub_arrays = []
        sub_array = []
        for i, cb in enumerate(cbs_array):
            if not array_is_cond_cb[i]:
                sub_arrays.append(sub_array)
                sub_array = []
            sub_array.append(cb)
        sub_arrays.append(sub_array)
        sub_arrays = [arr for arr in sub_arrays if arr != []]
        max_sub_arr = max([len(arr) for arr in sub_arrays])
        assert max_sub_arr < max(
            dir1_lim, dir2_lim) and abs(dir1_lim) != 1 and abs(dir2_lim) != 1, f'dir_lim too small! at least need {max_sub_arr+1} to ensure conditional command block to correctly work!'

        def compute_cmd_pos(block_n):
            num_cbs_in_one_layer = dir1_lim*dir2_lim
            num_layers = block_n//num_cbs_in_one_layer
            num_cbs_in_last_layer = block_n % num_cbs_in_one_layer
            dir3_p = (num_layers)*dir3
            # pos=0 positive, pos=1 negative
            dir2_pos = num_layers % 2
            num_rows = num_cbs_in_last_layer//dir1_lim
            num_cbs_in_last_row = num_cbs_in_last_layer % dir1_lim
            dir2_p = (num_rows)*dir2
            if dir2_pos:
                dir2_p = (dir2_lim-1)*dir2-dir2_p
            if num_rows % 2:
                dir1_p = ((dir1_lim-1)-num_cbs_in_last_row)*dir1
            else:
                dir1_p = (num_cbs_in_last_row)*dir1
            return dir1_p+dir2_p+dir3_p+start_point

        sub_array = sub_arrays.pop(0)
        require_len = len(sub_array)

        real_cbs = []
        last_dir = None
        same_dir_len = 0
        while True:
            this_cb_pos = compute_cmd_pos(len(real_cbs))
            next_cb_pos = compute_cmd_pos(len(real_cbs)+1)
            cb_dir = next_cb_pos-this_cb_pos
            face = {
                (0, 1, 0): self.FACE_UP,
                (0, -1, 0): self.FACE_DOWN,
                (1, 0, 0): self.FACE_XPP,
                (-1, 0, 0): self.FACE_XNN,
                (0, 0, 1): self.FACE_ZPP,
                (0, 0, -1): self.FACE_ZNN,
            }[tuple(cb_dir.astype(int))]
            if last_dir is None:
                last_dir = face
            if last_dir == face:
                same_dir_len += 1
            else:
                same_dir_len = 1
                last_dir = face
            real_cbs.append({
                'x': this_cb_pos[0],
                'y': this_cb_pos[1],
                'z': this_cb_pos[2],
                'facing': face,
                'cb_mode': self.MODE_CHAIN_CB
            })
            if same_dir_len == require_len:
                for sub_i, cb in enumerate(sub_array):
                    real_cbs[-(require_len-sub_i)].update(cb)
                same_dir_len = 0
                if sub_arrays == []:
                    break
                else:
                    sub_array = sub_arrays.pop(0)
                    require_len = len(sub_array)
        for cb in real_cbs:
            self.place_command_block_with_data(**cb)
