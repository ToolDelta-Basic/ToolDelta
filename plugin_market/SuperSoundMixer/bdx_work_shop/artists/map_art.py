from importlib import import_module
from PIL import Image
import numpy as np
from numba import jit
from canvas import Canvas
import json,os

with open(os.path.join(os.path.dirname(__file__), "cmap.json"),'r') as f:
    cmap=json.load(f)
def light_pixel(rgb):
    return [round(255/220*rgb[0]), 255/220*rgb[1], 255/220*rgb[2]]


def darkPixel(rgb):
    return [round(180/220*rgb[0]), 180/220*rgb[1], 180/220*rgb[2]]


color_list = [c[1] for c in cmap]
color_list = np.array(color_list).astype(np.float32)

color_list_d3 = []
block_names = []
for block_def, rgb in cmap:
    color_list_d3.append(rgb)
    color_list_d3.append(darkPixel(rgb))
    color_list_d3.append(light_pixel(rgb))
    block_names.append(block_def)
color_list_d3 = np.clip(np.array(color_list_d3),0,255).astype(np.float32)
# block_name=[c[0] for c in cmap]


@jit(nopython=True)
def closest_color(target_rgb, color_list):
    delta = np.inf
    best_match = None
    target_rgb = np.clip(target_rgb, 0, 255)
    tr, tg, tb = target_rgb
    for i, (r, g, b) in enumerate(color_list):
        if tr+r > 256:
            d = 2*((tr-r)**2)+4*((tg-g)**2)+3*((tb-b)**2)
        else:
            d = 3*((tr-r)**2)+4*((tg-g)**2)+2*((tb-b)**2)
        if d < delta:
            delta = d
            best_match = (i, color_list[i])
    return best_match


overflow_distance_factor = np.array([2, 4, 3], dtype=np.float32)
non_overflow_distance_factor = np.array([3, 4, 2], dtype=np.float32)


@jit(nopython=True)
def closest_color_np(target_rgb, color_list: np.ndarray):
    target_rgb = np.clip(target_rgb, 0, 255)
    diff_rgb = target_rgb-color_list.copy()
    diff_rgb = diff_rgb**2
    overflow_mask = target_rgb[0]+color_list[:, 0]
    diff_rgb[overflow_mask] *= overflow_distance_factor
    diff_rgb[~overflow_mask] *= non_overflow_distance_factor
    i = np.argmin(diff_rgb)
    return (i, color_list[i])


@jit(nopython=True)
def convert_palette(color_list, data: np.ndarray):
    converted_data = data.copy().astype(np.float32)
    block_map = np.zeros(data.shape[:2], dtype=np.uint8)
    flatten_data = converted_data.reshape((-1, 3))
    flatten_block_map = block_map.reshape((-1,))
    converted_data.reshape((-1, 3))
    h, w, _ = converted_data.shape
    for pi, rgb in enumerate(flatten_data):
        mi, mrgb = closest_color(rgb, color_list)
        # mi_,mrgb_ = closest_color_np(rgb,color_list)
        # if mi!=mi_ or mrgb!=mrgb_:
        #     print(f"{pi}")
        # (r,g,b),(mr,mg,mb)=rgb,mrgb
        drgb = rgb-mrgb
        if (pi+1) % w:
            flatten_data[pi+1] += (7/16)*drgb
        elif pi < (h-1)*w:
            pj = pi+w
            flatten_data[pj] += (5/16)*drgb
            if (pi+1) % w:
                pj = pi+w+1
                flatten_data[pj] += (1/16)*drgb
            if pi % w:
                pj = pi+w-1
                flatten_data[pj] += (3/16)*drgb
        flatten_data[pi] = mrgb
        flatten_block_map[pi] = mi
    converted_data = flatten_data.reshape((h, w, 3)).astype(np.uint8)
    block_map = flatten_block_map.reshape((h, w))
    return (block_map, converted_data)


def convert_img(img: Image, level_x=2, level_y=2, d3=False):
    resized_img = img.resize((level_x*128, level_y*128))
    resized_img_np = np.array(resized_img)
    block_map, converted_img = convert_palette(
        color_list_d3 if d3 else color_list, resized_img_np)
    converted_img = Image.fromarray(converted_img)
    return block_map, converted_img, resized_img


@jit(nopython=True)
def split_Y_Map(block_map: np.ndarray):
    ymap = np.zeros_like(block_map)
    h, w = block_map.shape
    yhmap = np.zeros(shape=(h+1,), dtype=np.int32)
    for x in range(w):
        yhmap[0] = 0
        for z in range(h):
            bi = block_map[z, x]
            t = bi % 3
            if t == 0:
                yhmap[z+1] = yhmap[z]
            elif t == 1:
                yhmap[z+1] = yhmap[z]-2
            else:
                yhmap[z+1] = yhmap[z]+2
        yhmap -= np.min(yhmap)
        ymap[:, x] = yhmap[1:]
    return ymap, block_map//3


def write_blocks(canvas: Canvas, block_map: np.ndarray):
    h, w = block_map.shape
    for z in range(h):
        for x in range(w):
            name, val = block_names[block_map[z, x]]
            canvas.setblock(name, val, x, 0, z)
            if name == "sweet_berry_bush":
                canvas.setblock("grass", 0, x, -1, z)
            if name == "leaves":
                canvas.setblock("log", 0, x, -1, z)
            else:
                canvas.setblock("wool",0, x, -1, z)


def write_blocks_3d(canvas: Canvas, ymap: np.ndarray, zx_map: np.ndarray):
    h, w = zx_map.shape
    for z in range(h):
        for x in range(w):
            name, val = block_names[zx_map[z, x]]
            y = ymap[z, x]+1
            canvas.setblock(name, val, x, y, z)
            if name == "sweet_berry_bush":
                canvas.setblock("grass", 0, x, y-1, z)
            if name == "leaves":
                canvas.setblock("log", 0, x, y-1, z)
            else:
                canvas.setblock("wool",0, x, y-1, z)

# to bdx, it's trivial


class Artist(Canvas):
    def __init__(self, canvas: Canvas, x=None, y=None, z=None):
        super().__init__()
        self.target_canvas = canvas
        self.target_xyz = {'ox': x, 'oy': y, 'oz': z}
        self.block_names = block_names

    def to_canvas(self, x=None, y=None, z=None):
        if x:
            self.target_xyz['ox'] = x
        if y:
            self.target_xyz['oy'] = y
        if z:
            self.target_xyz['oz'] = z
        self_host_ir = self.done()
        self.target_canvas.load_ir(self_host_ir, merge=True, **self.target_xyz)
        return self

    def auto_adjust_img(self,img:Image,raito):
        img_np = np.array(img)
        h,w,_=img_np.shape
        if h/w>raito:
            sh=int((h-raito*w)/2)
            img_np=img_np[sh:min(sh+int(raito*w),h),:]
        elif h/w <raito:
            sw=int((w-h/raito)/2)
            img_np=img_np[:,sw:min(sw+int(h/raito),w)]
        return Image.fromarray(img_np)

    def add_img(self, img_path: str, level_x=1, level_y=1, d3=False, save_resized_file_to=None, save_preview_to=None, y_max=100):
        img = Image.open(img_path)
        img= self.auto_adjust_img(img,level_y/level_x)
        if not d3:
            block_map, converted_img, resized_img = convert_img(
                img, level_x, level_y, d3=False)
            write_blocks(self, block_map)
        else:
            block_map, converted_img, resized_img = convert_img(
                img, level_x, level_y, d3=True)
            ymap, zx_map = split_Y_Map(block_map)
            ymap %= y_max
            write_blocks_3d(self, ymap=ymap, zx_map=zx_map)
        if save_resized_file_to is not None:
            resized_img.save(save_resized_file_to)
        if save_preview_to is not None:
            converted_img.save(save_preview_to)
