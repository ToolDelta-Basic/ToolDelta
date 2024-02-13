import os
from canvas import IR
from canvas import irio

mcstructure_file = 'data/27-2x3TrapDoorDoor.mcstructure'
ir_out_bdx = 'output/sample02/ir_out_bdx[direct].bdx'

os.makedirs('output/sample02', exist_ok=True)


ir = irio.create_ir_from_mcstructruce(mcstructure_file, ignore=['air'],
                                      user_define_mapping={
    'seaLeatern_1': {(('key1'), ('value1')): 1,
                     (('key2'), ('value2')): 2, },
    'some_block': 0
}
)
irio.dump_ir_to_bdx(ir, out_bdx_file=ir_out_bdx, author='2401PT')
