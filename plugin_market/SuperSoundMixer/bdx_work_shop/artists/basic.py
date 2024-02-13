from canvas import Canvas


class Artist(Canvas):
    def __init__(self, canvas: Canvas, x=None, y=None, z=None):
        '''
            Artist 的目的是将复杂而高级的操作从 canvas 抽离出来,
            避免 canvas 的成员函数过于复杂
            并允许用户自行定义复杂的操作
            可以看到Artist关联的canvas有两个，一个是目标工作区的，一个是自己的
            Artist 可以使用也可以不使用自己的画布
            但是，无论如何，都不应该修改工作区 canvas 的坐标
        '''
        super().__init__()
        self.target_canvas = canvas
        self.target_xyz = {'ox': x, 'oy': y, 'oz': z}

    def draw_cubic(self, block_name='air', block_val=0,
                   x=None, y=None, z=None,
                   ex=None, ey=None, ez=None):
        '''一个示例功能，此时是绘制在自己管理的canvas中'''
        self.fill(block_name, block_val, x, y, z, ex, ey, ez)
        return self

    def to_canvas(self):
        '''
        Artist 类应该提供一个 to_canvas 函数作为收尾
        这个函数用于使所有的操作实质性生效
        例如，将自己管理的canvas内容复制到目标canvas中
        '''
        self_host_ir = self.done()
        self.target_canvas.load_ir(self_host_ir, merge=True, **self.target_xyz)
        return self
