import os
import sys
from canvas import irio
from canvas import Canvas

import_bdx_file1 = 'data/silo.bdx'
import_bdx_file2 = 'data/silo.bdx'
mcstructure_file1 = 'data/27-2x3TrapDoorDoor.mcstructure'
input_schematic_file = 'data/城市书店1.schematic'

canvas_output = 'output/sample04/canvas_output.bdx'
canvas_output_schematic = 'output/sample04/canvas_output_schematic.schematic'
os.makedirs('output/sample04', exist_ok=True)

# 创建一个工作区，可以往工作区中导入多个建筑文件（目前支持：bdx, mcstructure）
# setblock, fill,move,clone replace放置命令块, 清除区域内方块，
# 最后导出一个导入顺序优化过的的bdx文件（参见昨天的部分，check.py）
# 上述命令都支持 相对和绝对位置 当一个xyz内被多次设置方块时，以最后一次为准

# mcstructure 为有限支持，因为其方块表示和 基岩版的 name value 形式不能完全匹配
# 使用时会在屏幕上输出程序推断的格式

canvas = Canvas()
# 坐标，只是为了方便
p = canvas

# 所有操作都有坐标（绝对坐标），留空时以最后一次move的位置为准
# 移动到 ~1 2 ~ 处，和tp指令还是有点像的吧
# 但是实际上有很灵活的操作方式
canvas.move_to(p.x + 1, y=2)
canvas.move_to(5, 5, 5)
canvas.move_to(z=0)
canvas.move_to(y=p.y+3)


# 放置三个命令块 当前位置 ~~~3 处向上叠3个
for i in range(3):
    canvas.place_command_block_with_data(z=p.z + 3,
                                         y=p.y + i,
                                         facing=p.FACE_UP,
                                         cb_mode=p.MODE_CHAIN_CB,
                                         command='kill @e[type=tnt]',
                                         cb_name='kill tnt cb1',
                                         tick_delay=10,
                                         track_output=True)
# 移动
canvas.move_to(10, 5, 5)

# 放置方块，重叠时以最后一次操作为准
canvas.setblock('grass', 0, y=p.y + 10)
canvas.setblock('stone', 0)
canvas.setblock('wool')
canvas.setblock('wool', 2, p.x, p.y, p.z + 1)
canvas.setblock('wool', 3, p.x, p.y, p.z + 5)

# replace wordwide 支持宽泛的格式
# 尝试完全匹配给定的方块，并将目标方块部分替换
# ori_block glass -> match (glass,0,None), (glass,1,None)
# ori_block (glass,1) -> match (glass,1,None) mismatch (glass,2,None)
# new_block wool => (glass,1,None)->(glass,1,None);(glass,2,None)->(glass,2,None)
# new_block (wool,0) => (glass,1,None)->(glass,0,None);(glass,2,None)->(glass,0,None)
canvas.replace_wordwide('glass', ('stained_glass', 0))
canvas.replace_wordwide(('wool', 0), 'quartz_block')
canvas.replace_wordwide(('wool', 2, None), ('quartz_block', 0, None))

# 清除一个小区域
canvas.fill(ex=p.x + 2, ey=p.y + 2, ez=p.z + 2, remove=True)

# 移动
canvas.move_to(p.x + 5)

# 清除一个方块
canvas.setblock(p.x, p.y, p.z + 5, remove=True)

# 放置几个命令块
canvas.setblock('glass', 0, p.x, p.y, p.z + 10)
canvas.fill('quartz_block',
            0,
            x=p.x,
            y=p.y,
            z=p.z,
            ex=p.x + 3,
            ey=p.y + 4,
            ez=p.z + 5)

# 在工作区（画布）上加载一个或者多个文件
# 载入一个 bdx 文件
canvas.load_ir(ir=irio.create_ir_from_mcstructruce(mcstructure_file1, ignore=['air']),
               ox=p.x + 5)
# 载入一个 bdx 文件
canvas.load_ir(ir=irio.create_ir_from_bdx(import_bdx_file1, need_verify=True),
               ox=p.x+10)

canvas.load_ir(ir=irio.create_ir_from_bdx(import_bdx_file1, need_verify=True),
               ox=p.x+10, oy=p.y + 10)

# 载入一个 schematic 文件
canvas.load_ir(ir=irio.create_ir_from_schematic(
    input_schematic_file, ignore=['air']), oz=p.z+20, oy=p.y + 10)

# 基于 selector 实现的复杂操作，建议阅读 selector 实现确定如何使用
# block 和 bid 都会生效，坐标留空时默认为整个工作区的起点/终点
# 注意！copy 和 move 都是基于 offset 的，而不是指定新的起点坐标
canvas.move_to(p.x+20)
indices = canvas.select()
canvas.fill(block_name='glass', x=p.x, y=p.y,
            z=p.z, ex=p.x+5, ey=p.y+5, ez=p.z+5)
canvas.replace(('stained_glass', 1), sx=p.x+1, ex=p.x+4,
               sy=p.y+2, orig_blocks=[('glass', 0), ('stone', 0)])
canvas.copy(sx=p.x, sy=p.y, sz=p.z, ex=p.x+5, ey=p.y+5, ez=p.z+5, offset_x=3,
            offset_y=3, offset_z=3)  # can filter by ,blocks=[('glass',0)])
canvas.move(sx=p.x, ex=p.x+10, ey=p.y+5, offset_y=15, blocks=['stained_block'])

# 将工作区导出为优化导入顺序后的bdx文件
final_ir = canvas.done()
irio.dump_ir_to_bdx(final_ir, canvas_output, need_sign=True, author='2401PT')

# 也可以导出为 schematic 文件，就是命令块数据会丢失
irio.dump_ir_to_schematic(final_ir, canvas_output_schematic)
