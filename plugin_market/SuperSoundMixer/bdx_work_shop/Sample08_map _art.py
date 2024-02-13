import os
from canvas import Canvas
from canvas import irio
from collections import defaultdict
from artists.map_art import Artist as MapArtArtist

image_input="data\QQ图片20220115231611.jpg"
output_dir= 'output/sample08'
os.makedirs(output_dir,exist_ok=True)

# 2D
canvas = Canvas()
p = canvas
artist = MapArtArtist(canvas=canvas,y=0)

artist.add_img(img_path=image_input,
               level_x=2,level_y=2,  # 希望用几张地图实现呢?
               d3=False, 
               save_resized_file_to=os.path.join(output_dir,'resized_img.png'), #只是缩放了图片
               save_preview_to=os.path.join(output_dir,"preview.png"), # 效果预览图，不出意外导入游戏就是这样的
               )
artist.to_canvas()

final_ir = canvas.done()
irio.dump_ir_to_bdx(final_ir,
                    os.path.join(output_dir,"map.bdx"), # 保存文件路径
                    need_sign=True,
                    author='2401PT')



# 3D, also takes y space
canvas = Canvas()
p = canvas
artist = MapArtArtist(canvas=canvas,y=0)

artist.add_img(img_path=image_input,
               level_x=2,level_y=2,  # 希望用几张地图实现呢?
               d3=True, # 通过利用阴影算法，扩展颜色空间
               save_resized_file_to=os.path.join(output_dir,'resized_img_3d.png'), #只是缩放了图片
               save_preview_to=os.path.join(output_dir,"preview_3d.png"), # 效果预览图，不出意外导入游戏就是这样的
               y_max=200 # 运行使用的最大y空间， 比如说，导入的y高度为20，最大可用到220
               )
artist.to_canvas()

final_ir = canvas.done()
irio.dump_ir_to_bdx(final_ir,
                    os.path.join(output_dir,"map_3d.bdx"), # 保存文件路径
                    need_sign=True,
                    author='2401PT')