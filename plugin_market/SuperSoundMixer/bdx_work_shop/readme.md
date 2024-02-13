# BDXWorkShop: 以稀疏矩阵为核心的 minecraft bdx 文件制作工具

## IR: (Intermediate Represet)

IR (即，中间表示) (ir.py) 是建筑的稀疏矩阵表示, 位于整个项目的中下层  
IR 中的稀疏矩阵为numpy矩阵，这可以实现高效的对方块的操作

``` python
    # 稀疏矩阵表示为：x y z 坐标和表示方块 bid
    # 稀疏矩阵，numpy 格式，4列
    ir.ir_matrix=[
        [x1,y1,z1,bid0],    #第一个方块
        [x2,y1,z2,bid1],    #第二个方块
        [x3,y3,z3,bid0],   
        ...
    ]
    # bid 映射表, 用于表示 bid 对应的方块名，数据值和命令方块数据(tuple)
    # 和 bdx 中的 palette 为类型概念
    ir.ir_blocks=[
        [name,val,cb_data]  # bid 0
        [name,val,cb_data]  # bid 1
    ...
    ]
    # 对于normal block: cb_data=None，对于命令块，请参照ir.py
```

## IRIO: (IR Input/Output)

IR 输入输出，位于系统的下层  
导入 实现 .bdx .schematic .mc_structure 的导入 (导入为IR)  
导出 实现 IR 导出为 .bdx .schematic

>注意! .schmetic 为有限支持，因为其格式不支持新版的方块，也不支持命令块
>新版的一些方块会被替换为 stained_glass，数据值保留
>后缀为 .schme 的也还没有支持，支持的是 .schematic

> 注意！ .mc_structure 也为有限支持，因为不同版本的方块名不完全一样
> 而且其 ‘状态’ 属性并不能完全对应数据值，所以使用模糊匹配算法寻找对应方块

另外，ir 还提供一个rearrange方法,通过重排完成对bdx文件的优化(导入顺序):   
fb 默认移动方式为 Z方向->Y方向->X方向  
其问题是，在Z方向移动过快导致有时区块还未顺利加载即发送包  
rearrange 将稀疏矩阵重排，使顺序变为:  
当生成指令时，移动顺序为:Y->区块内X->区块内Z->X方向下一个区块->Z方向下一区块  
并进行蛇形移动，有助于在当前区块导入时mc有时间准备好下一区块的数据  
区块尺寸可以通过 ir.CHUNK_SIZE 指定，默认为8，即半个mc的区块尺寸

***参考 Sample00 ～ Sample03***

## Canvas: 画布

Canvas 提供了一系列的功能，用以在 IR 中制作不同的结构，位于项目的中层

其支持的指令大概可以分为一下几类：

1. 导入导出：将 ir 一个 ir 导入到 Canvas 中，以及导出一个 ir。通过与 irio 的结合可以实现将多个 
.bdx .schematic .mc_structure 文件导入到 Canvas 的不同位置，并将Canvas的内容导出为 .bdx .schematic

2. move_to(tp), setblock, place_command_block_with_data, fill, replace_wordwide, select, move, copy, replace
这些操作被设计以模仿并提供比原版更强的功能

3. snake_folding_cmds: 堆叠命令块,考虑到需要在有限的空间内放置大量的命令块，需要将命令块折叠，
但是，这可能会影响有条件命令块的正常工作，该命令实现命令块序列堆放算法的实现并保证有条件命令块的正常工作

***1、2 参考 Sample04***  
***3 参考 Sample05***

## Artist: 实现特定高级功能

Artist 的目的是将复杂而高级的操作从 canvas 抽离出来, 属于高级功能
避免 canvas 的成员函数过于复杂
并允许用户自行定义复杂的操作,  
虽然，截止到目前，还没有实现任何高级操作,不过，基本的范式已经定义了(artist/basic.py)
由于 artiset 可能有复杂的依赖，所以默认不 import，而是按需 import

现有 Artist:

- cmd_midi_music: 将音乐转换为midi，再将midi转换为指令，目前为有限支持，仅考虑高音部由 bell， 中音部由 piano(harp)/pling(电子琴) 低音部由 bass 三个构成的组合，参见 Sample07_cmd_music.py

- map_art: 校色+dither算法实现更精准的色彩生成，支持拼接+阴影（需要占用y轴空间) Sample08_map _art.py

 ***Sample07***

## 其他:

canvas/blocks 中的 BLOCKS_DEFINE 拷贝于 MCEdit 2.0 (https://github.com/mcedit/mcedit2)
其协议为 https://github.com/mcedit/mcedit2

另: 本项目受到群友 CL_P 的帮助，并仿写了其一部分代码（已经标记）  

本项目现有代码并未完全测试，如果有发现有问题，欢迎反馈～
