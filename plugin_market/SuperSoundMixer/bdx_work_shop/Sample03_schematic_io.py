import os
from canvas import IR
from canvas import irio

input_schematic_file = 'data/城市书店1.schematic'
ir_in_bdx = 'data/silo.bdx'
output_bdx_file = 'output/sample03/output.bdx'
output_schematic_file = 'output/sample03/output_schematic.schematic'
output_bdx_file_converted_from_bdx = 'output/sample03/from_bdx.schematic'
os.makedirs('output/sample03', exist_ok=True)

# 先演示 加载 schematic，并保存为 bdx
ir = irio.create_ir_from_schematic(input_schematic_file, ignore=['air'])
irio.dump_ir_to_bdx(ir, out_bdx_file=output_bdx_file, author='2401PT')

# 这个被加载的数据 ir 可以被保存为 schematic
irio.dump_ir_to_schematic(ir, output_schematic_file)

# 当然，也可以先将bdx载入为ir再保存为 schematic
ir = irio.create_ir_from_bdx(ir_in_bdx, need_verify=True)
irio.dump_ir_to_schematic(ir, output_bdx_file_converted_from_bdx)
