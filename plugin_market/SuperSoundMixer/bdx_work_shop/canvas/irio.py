import numpy as np
from numpy.core.shape_base import block
from .ir import IR
from .decode_bdx import BdxDecoder
from .encode_bdx import BdxEncoder
from .blocks import blocks


def create_ir_from_cmds(cmds):
    '''从decoder的输出中构建ir'''
    ir = IR()
    ir.ir_lookup = {}
    ir.ir_blocks = []
    ir_matrix = []
    ir_x, ir_y, ir_z = 0, 0, 0
    palette = []
    for op_code, op_name, params in cmds:
        if op_code == 1:
            if params in palette:
                print(f'warning! find redundant key {params}')
            palette.append(params)
        elif op_code == 7:
            blk_id, blk_val = params
            blk_name = palette[blk_id]
            bid = ir.get_block_bid((blk_name, blk_val, None))
            ir_matrix.append([ir_x, ir_y, ir_z, bid])
        elif op_code == 8:
            ir_z += 1
        elif op_code == 9:
            pass
        elif op_code == 14:
            ir_x += 1
        elif op_code == 15:
            ir_x -= 1
        elif op_code == 16:
            ir_y += 1
        elif op_code == 17:
            ir_y -= 1
        elif op_code == 18:
            ir_z += 1
        elif op_code == 19:
            ir_z -= 1
        elif op_code in [20, 21, 28]:
            ir_x += params
        elif op_code in [22, 23, 29]:
            ir_y += params
        elif op_code in [6, 12, 24, 25, 30]:
            ir_z += params
        elif op_code == 26:
            assert isinstance(params, tuple)
            cb_data = params
            blk_name, blk_val = None, None
            found_blk = None
            # 搜索究竟给哪个cb block进行赋值
            for x, y, z, bid in ir_matrix[::-1]:
                if (x, y, z) == (ir_x, ir_y, ir_z):
                    found_blk = bid
                    break
            if found_blk is not None:
                blk_name, blk_val, _ = ir.ir_blocks[bid]
            else:
                print(
                    "can't found the block you assign, I sure hope you know what you are doing"
                )
            bid = ir.get_block_bid((blk_name, blk_val, cb_data))
            ir_matrix.append([ir_x, ir_y, ir_z, bid])
        elif op_code == 27:
            assert isinstance(params, tuple)
            cb_data = tuple(params[2:])
            blk_id, blk_val = params[:2]
            blk_name = palette[blk_id]
            bid = ir.get_block_bid((blk_name, blk_val, cb_data))
            ir_matrix.append([ir_x, ir_y, ir_z, bid])
        else:
            raise NotImplementedError(
                f"don't know how to handle {op_name}[{op_code}]")
    ir.ir_matrix = np.array(ir_matrix, dtype=np.int32).conjugate()
    return ir


def create_ir_from_bdx(bdx_file, need_verify=True):
    '''将一个bdx文件加载为 ir'''
    print('decoding bdx...')
    decoder = BdxDecoder(None, need_verify=need_verify)
    decoder.log_nothing()
    with open(bdx_file, 'rb') as f:
        decode_out = decoder.decode(f)
    print('decoding done')
    ir = create_ir_from_cmds(decode_out['cmds'])
    print('ir initialized')
    return ir


def translate_block(block, user_define_mapping=None):
    '''推测一个mcstructure的block在基岩版中的名字和数据值'''
    from thefuzz import fuzz
    from nbtlib import tag

    block_mapping_name_description_val = blocks.name_description_val_mapping
    block_names = blocks.names

    if user_define_mapping is None:
        user_define_mapping = {}
    print(block)
    block_name = block['name']
    block_name = block_name.replace('minecraft:', '')
    status = block['states']
    status = dict(status)

    block_lookup = user_define_mapping.get(block_name)
    if block_lookup is None:
        block_lookup = block_mapping_name_description_val.get(block_name)
    if block_lookup is None:
        score_name_mapping = [(fuzz.ratio(block_name, n), n)
                              for n in block_names]
        score_name_mapping.sort(key=lambda x: x[0], reverse=True)
        block_name = score_name_mapping[0][1]
        print(
            f'!cannot find the actually name mapping of {block["name"]}, I guess it is {block_name}')
        block_lookup = block_mapping_name_description_val.get(block_name)
    # if isinstance(block_lookup,tuple):
    #     print(f'I think it is {block_lookup}')
    #     return block_lookup
    if len(status) == 0:
        print(f'I think it could be {block_name} ({0})')
        return block_name, 0
    if isinstance(block_lookup, int):
        print(f'I think it could be {block_name} ({block_lookup})')
        return block_name, block_lookup
    if isinstance(block_lookup, tuple):
        print(f'I think it could be {block_lookup}')
        return block_lookup

    possible_names = []
    possible_values = []
    occourd_keys = []
    for kvs, block_value in block_lookup.items():
        possible_name = []
        possible_values.append(block_value)
        for kv in kvs:
            possible_name += kv
            occourd_keys.append(kv[1])
        possible_names.append(possible_name)

    has_dir = True
    string_dir_names = ['down', 'up', 'north', 'south', 'west', 'east']
    if 'down' in occourd_keys:
        dir_remapping = {i: string_dir_names[i] for i in range(6)}
    elif 'up' in occourd_keys:
        dir_remapping = {i: string_dir_names[i + 1] for i in range(5)}
    elif 'north' in occourd_keys:
        dir_remapping = {i: string_dir_names[i + 2] for i in range(4)}
    else:
        has_dir = False

    status_fuzzy = []
    for k, v in status.items():
        status_fuzzy.append(k)
        if isinstance(v, tag.String):
            v = str(v)
            if 'north_south' in v:
                status_fuzzy += ['z'] * 3
            if 'west_east' in v:
                status_fuzzy += ['x'] * 3
            if 'top' in v:
                status_fuzzy.append('up')
            if 'default' in v:
                status_fuzzy.append(block['name'])
            status_fuzzy.append(v)
        elif isinstance(v, tag.Byte):
            v = 'true' if v == 1 else 'false'
            status_fuzzy.append(v)
        else:
            try:
                if has_dir and v < len(dir_remapping):
                    status_fuzzy.append(dir_remapping[v])
                v = str(int(v))
                status_fuzzy.append(v)
            except:
                print(f'pass k {k}')
    scores = []
    # print(status_fuzzy)
    for possible_name in possible_names:
        # score=0
        fuzzy_status = '_'.join(status_fuzzy)
        fuzzy_name = '_'.join(possible_name)
        # for status_name in status_fuzzy:
        #     if status_name in possible_names:
        #         score+=1
        # p=possible_name_.find(status_name)
        # if p !=-1:
        #     score+=1
        # possible_name_=possible_name_[p+len(status_name):]

        scores.append(fuzz.ratio(fuzzy_status, fuzzy_name))
        # names.append(possible_name)
    max_s = max(scores)
    # if max_s==0:
    #     print(f'? not find, use: {matchs[0][0]}[{names[0]}')
    #     return matchs[0]
    # else:
    for ib, v in enumerate(scores):
        if v == max_s:
            print(
                f'? possible is: {block_name}{possible_names[ib]} ({possible_values[ib]})')
            return (block_name, possible_values[ib])

    assert False, 'this should not happen, my fault'

    # print(f'? not find excatly match, use: {matchs[0][0]}[{names[0]}')
    # return matchs[0]


def create_ir_from_mcstructruce(mc_structure_file, ignore=None, user_define_mapping=None):
    if ignore is None:
        ignore = []
    if user_define_mapping is None:
        user_define_mapping = {}
    try:
        import nbtlib
        from nbtlib import tag
    except:
        print('Please install nbtlib first (pip install nbtlib) ... load mcstructure require this')
        exit(-1)

    try:
        from thefuzz import fuzz
    except:
        print('Please install thefuzzy first (pip install thefuzzy) ... matching mcstructure blocks require this')
        exit(-1)

    nbt = nbtlib.load(mc_structure_file, byteorder='little')
    try:
        if 'structure' not in nbt.keys():
            nbt = nbt['']
        structure = nbt['structure']
        lx, ly, lz = list(map(int, nbt['size']))
        palette = nbt['structure']["palette"]["default"]["block_palette"]
    except:
        raise ValueError('structure missing')

    blocks = list(map(int, structure["block_indices"][0]))
    matrix = np.zeros((lx * ly * lz, 4), dtype=np.int32)
    matrix[:, 3] = blocks
    matrix_view = matrix.view()
    matrix_view.shape = (lx * ly, lz, 4)
    matrix_view[:, :, 2] = np.arange(lz)
    matrix_view.shape = (lx, ly * lz, 4)
    matrix_view[:, :, 1] = np.arange(ly).repeat(lz)
    matrix[:, 0] = np.arange(lx).repeat(ly * lz)

    def translate_palette(palette, ignore=None, user_define_mapping=None):
        ignored_bids = []
        ir_blocks = []
        if ignore is None:
            ignore = []
        for bid, block in enumerate(palette):
            block_name = block['name']
            new_name, block_val = translate_block(block, user_define_mapping)
            if (new_name in ignore) or (block_name in ignore):
                ignored_bids.append(bid)
            ir_blocks.append((new_name, block_val, None))
        return ignored_bids, ir_blocks

    ignored_bids, ir_blocks = translate_palette(
        palette, ignore, user_define_mapping)
    for ignored_bid in ignored_bids:
        matrix = matrix[matrix[:, 3] != ignored_bid, :]
    ir = IR()
    ir.ir_matrix = matrix
    ir.ir_blocks = ir_blocks
    ir.rebuild_bid_lookup()
    return ir


def create_ir_from_schematic(schematic_file, ignore=None):
    try:
        import nbtlib as nbt
        from nbtlib import tag
    except:
        print('Please install nbtlib first (pip install nbtlib) ... load mcstructure require this')
        exit(-1)
    root_tag = nbt.load(filename=schematic_file, gzipped=True, byteorder='big')
    assert root_tag.root_name == 'Schematic', 'this is not a schematic file!'
    shape = (int(root_tag['Height']), int(
        root_tag['Length']), int(root_tag['Width']))
    ly, lz, lx = shape
    src_blocks = np.asarray(root_tag['Blocks'], order='C',
                            dtype=np.uint8)  # .reshape(shape, order='C')
    src_datas = np.asarray(root_tag['Data'], order='C',
                           dtype=np.uint8)  # .reshape(shape, order='C')
    # schema = {
    #     'Height': nbt.Short,    #y
    #     'Length': nbt.Short,    #z
    #     'Width': nbt.Short,     #x
    #     'Materials': nbt.String,
    #     'Blocks': nbt.ByteArray,
    #     'Data': nbt.ByteArray,
    #     'Entities': nbt.List[Entity],
    #     'TileEntities': nbt.List[BlockEntity]
    # }
    meterials = str(root_tag['Materials'])

    # sparse_matrix=np.zeros((np.product(shape), 4), dtype=np.int32)
    # matrix_view = sparse_matrix.view()
    # matrix_view.shape = (ly * lz,lx , 4)
    # matrix_view[:, :, 0] = np.arange(lx)
    # matrix_view.shape = (ly, lx * lz, 4)
    # matrix_view[:, :, 2] = np.arange(ly).repeat(lx)
    # sparse_matrix[:, 1] = np.arange(ly).repeat(lx * lz)
    # 算了，我还是老实点吧，毕竟求bid还是要遍历的嘛

    blocks_id_name_mapping = blocks.id_name_mapping
    ir = IR()

    if ignore is None:
        ignore = []
    bid_mapping = {}
    ir_matrix = []
    for i, (src_block, src_data) in enumerate(zip(src_blocks, src_datas)):
        bid = bid_mapping.get((src_block, src_data))
        if bid is None:
            block_name = blocks_id_name_mapping[src_block]
            if block_name in ignore or (block_name, src_data) in ignore:
                bid_mapping[(src_block, src_data)] = -1
            bid = ir.get_block_bid((block_name, src_data, None))
            bid_mapping[(src_block, src_data)] = bid
        if bid == -1:
            pass
        else:
            y, z, x = i//(lz*lx), (i % (lz*lx))//lx, i % lx
            ir_matrix.append([x, y, z, bid])
    ir.ir_matrix = np.array(ir_matrix, dtype=np.int32).conjugate()
    return ir


class IR_BDX_Exportor(IR):
    def __init__(self, ir: IR):
        super(IR_BDX_Exportor, self).__init__()
        # data may assigned during exporting, so we do this
        self.ir_blocks = ir.ir_blocks
        self.ir_lookup = ir.ir_lookup
        self.ir_matrix = ir.ir_matrix
        self.CHUNK_SIZE = ir.CHUNK_SIZE

        self.X, self.Y, self.Z = 0, 1, 2
        self.move_keys = {
            # 感谢群友 CL_P 的思路
            # ++, --, addSmall(-128~127), add(-32768~32767), addBig(-2147483648~2147483647)
            self.X: [14, 15, 28, 20, 21],
            self.Y: [16, 17, 29, 22, 23],
            self.Z: [18, 19, 30, 24, 25],
        }
        self.SAME_AS_FB = True

    def move(self, x, y, z, bx, by, bz):
        # op_code,op_name,offset
        move_ops = []
        if x != bx:
            offset = x - bx
            move_ops.append(self.obtain_move_op_code(offset, self.X))
        if y != by:
            offset = y - by
            move_ops.append(self.obtain_move_op_code(offset, self.Y))
        if z != bz:
            offset = z - bz
            move_ops.append(self.obtain_move_op_code(offset, self.Z))
        return move_ops

    def generate_palette(self):
        print('generating palette...')
        palette = []
        cmds = []
        palette_look_up_table = {}
        bid_palette_mapping = {}
        for bid, (name, val, cb_data) in enumerate(self.ir_blocks):
            palette_id = palette_look_up_table.get(name)
            if palette_id is None:
                palette_id = len(palette)
                palette_look_up_table[name] = palette_id
                palette.append(name)
                cmds.append((1, name))
            bid_palette_mapping[bid] = palette_id
        print('palette generated')
        return bid_palette_mapping, cmds, palette

    def obtain_move_op_code(self, offset: int, axis: int):
        """
        感谢群友 CL_P 的思路，这里是用了类似的实现，比较简洁
        ++,--,
        addSmall(-128~127), add(-32768~32767), addBig(-2147483648~2147483647)
        """
        if offset == 1:
            return self.move_keys[axis][0], None
        elif offset == -1:
            return self.move_keys[axis][1], None

        elif axis == self.Y and (offset > 2**15
                                 or offset < 2**15) \
                and self.SAME_AS_FB:
            return 23, offset

        # note: not >= or <=, but > and < though sign is -128~127
        elif offset > -2**7 and offset < 2**7:
            return self.move_keys[axis][2], offset
        elif offset > -2**15 and offset < 2**15:
            return self.move_keys[axis][3], offset
        elif offset > -2**31 and offset < 2**31:
            return self.move_keys[axis][4], offset

    def dump_to_cmds(self):
        print('ir -> cmds, converting... ')
        bid_palette_mapping, cache_cmds, palette = self.generate_palette()
        cmds = cache_cmds
        bx, by, bz = 0, 0, 0
        for x, y, z, bid in self.ir_matrix:
            cmds += self.move(x, y, z, bx, by, bz)
            bx, by, bz = x, y, z
            block_name, val, cb_data = self.ir_blocks[bid]
            palette_id = bid_palette_mapping[bid]
            if cb_data is None:
                cmds.append((7, (palette_id, val)))
            elif block_name is not None:
                cmds.append((27, (palette_id, val, *cb_data)))
            else:
                cmds.append((26, cb_data))
        print('converting done')
        return cmds

    def dump_to_bdx(self,
                    out_bdx_file,
                    need_sign=True,
                    author=None,
                    sign_token=None):

        gen_cmds = self.dump_to_cmds()
        print('encoding...')
        encoder = BdxEncoder(need_sign=need_sign,
                             log_path=None,
                             author=author,
                             sign_token=sign_token)
        encoder.log_nothing()
        encode_out = encoder.encode(cmds=gen_cmds)
        print('encoding done, write file...')
        with open(out_bdx_file, 'wb') as f:
            f.write(encode_out)
        print('finished!')


def dump_ir_to_cmds(ir, rearrange=False):
    exportor = IR_BDX_Exportor(ir)
    if rearrange:
        exportor.rearrange()
    return exportor.dump_to_cmds()


def dump_ir_to_bdx(ir, out_bdx_file, rearrange=False, need_sign=True, author=None, sign_token=None):
    exportor = IR_BDX_Exportor(ir)
    if rearrange:
        exportor.rearrange()
    exportor.dump_to_bdx(out_bdx_file=out_bdx_file,
                         need_sign=need_sign, author=author, sign_token=sign_token)


def dump_ir_to_schematic(ir: IR, out_schem_file):
    try:
        import nbtlib as nbt
        from nbtlib import File
    except:
        print('Please install nbtlib first (pip install nbtlib) ... load mcstructure require this')
        exit(-1)
    matrix = ir.ir_matrix.copy()
    min_x, max_x = np.min(matrix[:, 0]), np.max(matrix[:, 0])
    min_y, max_y = np.min(matrix[:, 1]), np.max(matrix[:, 1])
    min_z, max_z = np.min(matrix[:, 2]), np.max(matrix[:, 2])
    lx, ly, lz = max_x-min_x+1, max_y-min_y+1, max_z-min_z+1
    matrix -= [min_x, min_y, min_z, 0]
    ir_blocks = ir.ir_blocks

    s_blocks = np.zeros((np.product((lx, ly, lz)),), dtype=np.uint8)
    s_datas = np.zeros((np.product((lx, ly, lz)),), dtype=np.uint8)
    blocks_name_id_mapping = blocks.name_id_mapping

    bid_lookup = {}
    for bid, (block_name, block_val, _) in enumerate(ir_blocks):
        block_id = blocks_name_id_mapping.get(block_name)
        if block_id is None:
            print(f'block {block_name} is not supported by schematic file')
            print(f'it will be replaced by stained_glass {block_val}')
            block_id = blocks_name_id_mapping.get('stained_glass')
        bid_lookup[bid] = (block_id, block_val)

    for x, y, z, bid in matrix:
        pos_id = y * lx * lz + z * lx + x
        # -1 为被删除的方块
        if bid == -1:
            s_blocks[pos_id] = 0
            s_datas[pos_id] = 0
        else:
            block_id, block_val = bid_lookup[bid]
            s_blocks[pos_id] = block_id
            s_datas[pos_id] = block_val

    file = File({
        'Height': nbt.Short(ly),
        'Length': nbt.Short(lz),
        'Width': nbt.Short(lx),
        'Materials': nbt.String('Alpha'),
        'Blocks': nbt.ByteArray(s_blocks),
        'Data': nbt.ByteArray(s_datas),
        'Entities': nbt.List[nbt.Compound]([]),
        'TileEntities': nbt.List[nbt.Byte]([])
    }, root_name='Schematic')
    file.save(out_schem_file, gzipped=True, byteorder='big')
