import json
import os 
from canvas import irio
from canvas import Canvas

import_json_file = 'data/六分之一的小岛.json'
canvas_output = 'output/sample09/六分之一的小岛.bdx'
os.makedirs('output/sample09', exist_ok=True)

canvas = Canvas()
p = canvas
with open(import_json_file,"r") as f:
    inBlocks=json.load(f)
    print(f"{len(inBlocks)} blocks in total")
    for block in inBlocks:
        name=block["name"][10:]
        x,y,z=block["x"],block["y"],block["z"]
        data=block["aux"]
        if not "command" in name:  
            canvas.setblock(name, data, x,y,z)
        else:
            canvas.place_command_block_with_data(
                x=x, y=y, z=z,
                block_name=name,
                facing=int(block["facing"]),
                cb_mode=None,
                command=block["command"], cb_name=block["name"],
                tick_delay=int(block["tick_delay"]),
                execute_on_first_tick=False, 
                track_output=bool(int(block["track_output"])),
                conditional=bool(int(block["cb_mode"])),
                needRedstone=bool(int(block["need_redstone"])),)
final_ir = canvas.done()
irio.dump_ir_to_bdx(final_ir, canvas_output, need_sign=True, author='2401PT')