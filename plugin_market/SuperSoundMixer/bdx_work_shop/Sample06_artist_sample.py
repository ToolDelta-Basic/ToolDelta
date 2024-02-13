import os
from canvas import Canvas
from artists.basic import Artist as BasicArtist
from canvas import irio

canvas_output = 'output/sample06/canvas_output.bdx'
os.makedirs('output/sample06', exist_ok=True)

canvas = Canvas()
p = canvas

# Artist 的目的是将复杂而高级的操作从 canvas 抽离出来,
# 避免 canvas 的成员函数过于复杂
# 并允许用户自行定义复杂的操作
# 初始化时需要告诉 artist 目标工作区，并指定创作空间和 canvas 的偏移
artist = BasicArtist(canvas=canvas, y=p.y+10)

# 通过 artist 将复杂的操作进行封装
artist.draw_cubic(block_name='stained_glass',
                  block_val=0, x=5, ex=15, ey=10, ez=artist.z+10)

# artist 维护一个自己的坐标系，与工作区隔离
artist.move_to(x=artist.x+10)

# 同上
artist.draw_cubic(block_name='stained_glass',
                  block_val=1, x=15, ex=25, ey=10, ez=artist.z+10)

# 所有 artist 都应使用该函数作为收尾工作
artist.to_canvas()

final_ir = canvas.done()
irio.dump_ir_to_bdx(final_ir, canvas_output, need_sign=True, author='2401PT')
