import numpy as np

class IR(object):
    def __init__(self) -> None:
        '''使用稀疏矩阵和映射表表达的建筑结构 [中间表示] IR'''
        # block : [name,val,cb_data]
        # normal block: cb_data=None
        # cb block cb_data=(cb_mode,
        # command='',
        # cb_name='',
        # lastout='',
        # tick_delay=0,
        # first_tick=False,
        # track_out=False,
        # conditional=False,
        # redstone=False)
        # cb_data must be tuple!
        # 给出block描述，搜索block_id (bid)
        self.ir_lookup = {}
        # 给出bid,获得block描述
        self.ir_blocks = []
        # 稀疏矩阵，numpy 格式，4列
        # [
        #   [x,y,z,bid],
        #   [x,y,z,bid]
        # ]
        # 当 bid=-1时，表示这个位置的方块被清除（相当于结构空位）
        self.ir_matrix = np.zeros((0, 4), dtype=int)

        # fb Z方向->Y方向->X方向
        # 当生成指令时，移动顺序为:Y->区块内X->区块内Z->X方向下一个区块->Z方向下一区块
        # 另：蛇形移动，有助于在加载当前区块时已经准备好下一区块的数据
        self.CHUNK_SIZE = 8

    def get_block_bid(self, block):
        '''block can be anything, as long as it can be correctly hashed'''
        bid = self.ir_lookup.get(block)
        if bid is None:
            bid = len(self.ir_blocks)
            self.ir_lookup[block] = bid
            self.ir_blocks.append(block)
            return bid
        else:
            return bid

    def rebuild_bid_lookup(self,blocks=None):
        '''利用映射表 ir_blocks 的信息重构 ir_lookup 查找表, 但是并不重构matrix中的值'''
        if blocks is not None:
            self.ir_blocks=blocks
        self.ir_lookup = {k: i for i, k in enumerate(self.ir_blocks)}
        return self

    def rebuild_bid(self):
        '''如果ir出现了重复的block，可以用这个去除冗余的bid'''
        print('rebuild ir bid ...')
        old_matrix_bid = self.ir_matrix[:, 3].copy()
        new_matrix_bid = self.ir_matrix[:, 3].copy()
        old_blocks=self.ir_blocks
        new_blocks=[]
        new_ir_lookup={}
        for old_bid,block in enumerate(self.ir_blocks):
            index = old_matrix_bid == old_bid
            # remove not use bid key
            if not np.any(index):
                print(f'bid rebuid : ({block}) {old_bid} not use, removed')
                continue
            old_block=old_blocks[old_bid]
            new_bid = new_ir_lookup.get(old_block)
            if new_bid is None:
                new_bid=len(new_blocks)
                new_ir_lookup[block]=new_bid
                new_blocks.append(block)
            if new_bid!=old_bid:
                print(f'bid rebuid : ({block}) {old_bid} -> {new_bid}')
                new_matrix_bid[index]=new_bid
        self.ir_matrix[:,3]=new_matrix_bid
        self.ir_blocks=new_blocks
        self.ir_lookup=new_ir_lookup
        print('rebuild ir bid done')
        return self

    def rearrange(self):
        # 首先，我们对稀疏矩阵中所有方块进行重新排列
        print('rearranging')
        rearranged_blocks = []
        xz_matrix = self.ir_matrix[:, [0, 2]]
        xz_chunk_matrix = xz_matrix // self.CHUNK_SIZE
        # 0:trunk_x,1:trunk_z,2:x,3:y,4:z,5:bid
        operation_order = np.arange(self.ir_matrix.shape[0])
        operation_order = operation_order.reshape((-1, 1))
        matrix_with_trunk = np.concatenate(
            [xz_chunk_matrix, self.ir_matrix, operation_order], axis=1)
        unique_trunk = np.unique(xz_chunk_matrix, axis=0)
        # 我们移动顺序为：
        # Y->区块内X->区块内Z->X方向下一个区块->Z方向下一区块
        # 所以我们选择顺序是它的逆序：
        # Z区块->X区块->Z->X->Y
        unique_trunk_z = np.sort(np.unique(unique_trunk[:, 1]))
        for itz, trunk_z in enumerate(unique_trunk_z):
            # print(f'trunk z @ {trunk_z}')
            trunk_z_matrix = matrix_with_trunk[\
                matrix_with_trunk[:,1] == trunk_z]
            trunk_z_unique_trunk_x = np.sort(np.unique(unique_trunk[\
                unique_trunk[:, 1] == trunk_z][:,0]))
            if itz % 2:
                trunk_z_unique_trunk_x = trunk_z_unique_trunk_x[::-1]
            for itx, trunk_x in enumerate(trunk_z_unique_trunk_x):
                # print(f'\ttrunk x @ {trunk_x} [{trunk_z},{trunk_x}]')
                trunk_matrix=trunk_z_matrix[\
                    trunk_z_matrix[:,0]==trunk_x]
                # 到此为止，我们找出了一个区块的所有方块
                # 如果我们放弃方向性，可以使用多列联合排序
                # 但是我们这里就不这么干了
                trunk_unique_z = np.sort(np.unique(trunk_matrix[:, 4]))
                if itx % 2:
                    trunk_unique_z = trunk_unique_z[::-1]
                for iz, z_at_trunk in enumerate(trunk_unique_z):
                    # print(f'\t\tz @ {z_at_trunk}')
                    xy_matrix_at_trunk = trunk_matrix[\
                        trunk_matrix[:,4] == z_at_trunk]
                    unique_x_at_xy_matrix = np.sort(np.unique(\
                        xy_matrix_at_trunk[:,2]))
                    if iz % 2:
                        unique_x_at_xy_matrix = unique_x_at_xy_matrix[::-1]
                    for ix, x_at_xy_matrix in enumerate(unique_x_at_xy_matrix):
                        # print(f'\t\t\tx@ {x_at_xy_matrix}')
                        y_array_at_xy_matrix=xy_matrix_at_trunk[\
                            xy_matrix_at_trunk[:,2]==x_at_xy_matrix]
                        unique_y = np.sort(
                            np.unique(y_array_at_xy_matrix[:, 3]))
                        if ix % 2:
                            unique_y = unique_y[::-1]
                        for _y in unique_y:
                            # print(f'\t\t\t\ty@ {_y}')
                            blocks_at_cell = y_array_at_xy_matrix[\
                                y_array_at_xy_matrix[:,3]==_y]
                            if blocks_at_cell.shape[0] == 1:
                                # 该位置只有一个方块，没什么好说的
                                block_at_cell = blocks_at_cell[0]
                            else:
                                # 该位置只有多个方块，我们只保留最后一个的
                                block_arg = blocks_at_cell[:, -1].argsort()[-1]
                                block_at_cell = blocks_at_cell[block_arg, :]
                            if block_at_cell[-2] != -1:
                                # 如果值为-1，就认为这个位置的方块已经被删除
                                rearranged_blocks.append(block_at_cell)
        rearranged_blocks = np.vstack(rearranged_blocks)
        rearranged_blocks = rearranged_blocks[:, 2:-1]
        now_blocks = len(rearranged_blocks)
        orig_blocks = len(self.ir_matrix)
        self.ir_matrix = rearranged_blocks
        self.rebuild_bid()
        print(f'rearrange completed! {orig_blocks - now_blocks} duplicated blocks ignored')
        return self

