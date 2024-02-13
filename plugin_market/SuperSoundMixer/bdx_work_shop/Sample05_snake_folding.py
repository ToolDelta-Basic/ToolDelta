import os
from canvas import irio
from canvas import Canvas

canvas_output = 'output/sample05/canvas_output.bdx'
os.makedirs('output/sample05', exist_ok=True)

canvas = Canvas()
p = canvas
cbs_array = [
    {'cb_mode': p.MODE_REPEAT_CB, 'command': 'cmd',
        'cb_name': f'cb{0}', 'conditional': False}
]
cb_i = 1
for _ in range(10):
    for i in range(2):
        cbs_array.append(
            {'command': 'cmd', 'cb_name': f'cb{cb_i}', 'conditional': True, 'tick_delay': 10})
        cb_i += 1
    for i in range(3):
        cbs_array.append(
            {'command': 'cmd', 'cb_name': f'cb{cb_i}', 'conditional': False, 'tick_delay': 20})
        cb_i += 1


# 现在的问题是，一直线的排列命令块显然是不合适的，
# 我们需要命令块首先在一层堆叠，(dir1,dir2)
# 当堆叠满一层后再移动到下一层 (dir3)
# 第二个问题是，有条件命令块在拐角时无法正常工作，所以需要重排
# 即，适当时插入多个空连锁命令块，直到可以分配位置为止
# x,y,z 代表堆叠的起点位置
canvas.snake_folding_cmds(
    x=0, y=20, z=0,
    dir1=(1, 0, 0), dir1_lim=4,
    dir2=(0, 0, 1), dir2_lim=4,
    dir3=(0, 1, 0),
    cbs_array=cbs_array
)

# 也可以这么指定方向
canvas.snake_folding_cmds(
    x=10, y=20, z=0,
    dir1=(1, 0, 0), dir1_lim=4,
    dir2=(0, 0, -1), dir2_lim=4,
    dir3=(0, -1, 0),
    cbs_array=cbs_array
)

final_ir = canvas.done()
irio.dump_ir_to_bdx(final_ir, canvas_output, need_sign=True, author='2401PT')
