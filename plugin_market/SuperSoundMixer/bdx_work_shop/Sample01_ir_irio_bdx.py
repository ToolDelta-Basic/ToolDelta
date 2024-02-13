import os
import json

from canvas import IR
from canvas import irio

# IR (即，中间表示) (ir.py) 是稀疏矩阵建筑表示
# 其意义是通过这种中间表示，可以脱离指令，以一种更通用/高级的表示操作方块
# 同时，numpy的使用提高了操作效率
# ir 还提供一个rearrange方法,通过重排完成对bdx文件的优化(导入顺序)

# 稀疏矩阵表示为：
# ir.ir_blocks 稀疏矩阵，numpy 格式，4列
# [
#   [x,y,z,bid],    block0, first import/gen
#   [x,y,z,bid],    block1, second import/gen
#   ...
# ]
# bid 映射表
# ir.ir_blocks=[
#   [name,val,cb_data]  # bid 0
#   [name,val,cb_data]  # bid 1
#   ...
# ]
# 对于normal block: cb_data=None，对于命令块，请参照ir.py

# 为了保持 ir 的简洁性，ir 和 ir到其他结构文件的转换被分别放在 ir.py 和 irio.py 中

ir_in_bdx = 'data/silo.bdx'
ir_out_direct_bdx = 'output/sample01/ir_out_bdx[direct].bdx'
ir_out_rearranged_bdx = 'output/sample01/ir_out_bdx[rearranged].bdx'

os.makedirs('output/sample01', exist_ok=True)

# 从 bdx 文件创建
# irio.create_ir_from_cmds(cmds)
ir = irio.create_ir_from_bdx(ir_in_bdx, need_verify=True)
# irio.create_ir_from_mcstructruce(mc_structure_file)

# 导出
# irio.dump_ir_to_schem(ir,our_schem_file,rearrange=False)

# 导出时使用 rearrange 方法并不影响ir中的数据
irio.dump_ir_to_bdx(ir, ir_out_rearranged_bdx, rearrange=True,
                    need_sign=True, author='2401PT', sign_token=None)
# 在不使用 rearrange 时，保证生成的文件和fb完全相同
# irio.dump_ir_to_cmds(ir,rearrange=False)
irio.dump_ir_to_bdx(ir, ir_out_direct_bdx, rearrange=False,
                    need_sign=True, author='2401PT', sign_token=None)


def compare_bytes_array(array_1, array_2):
    ok = True
    if len(array_1) != len(array_2):
        print(f'length_mismathced {len(array_1)} {len(array_2)}')
        ok = False
    for i, (e, d) in enumerate(zip(array_1, array_2)):
        if e != d:
            print(f'error occur at {i}')
            print(f'{array_1[max(0, i - 20):min(len(array_2), i + 10)]}')
            print(f'{array_1[max(0, i - 20):min(len(array_2), i + 10)]}')
            ok = False
            break
    print('pass' if ok else 'fail')


print('check if bdx->ir->no rearrange out bdx has exactly same bytes')
with open(ir_in_bdx, 'rb') as f:
    original_bdx_bytes = f.read()

with open(ir_out_direct_bdx, 'rb') as f:
    ir_directly_ou_bdx_bytes = f.read()

compare_bytes_array(original_bdx_bytes, ir_directly_ou_bdx_bytes)

print('all done')
