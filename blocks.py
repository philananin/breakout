from observable import Observable
from color import Color
from block import Block
from functools import reduce

BLOCK_SIZE = 2

def get_border(width, height, color):
    top_left = Block(0, height, '╔', color)
    top_right = Block(width - 1, height, '╗', color)
    top = [Block(x, height, '═', color) for x in range(1, width - 1)]
    left = [Block(0, y, '║', color) for y in range(1, height)]
    right = [Block(width - 1, y, '║', color) for y in range(1, height)]
    blocks = [top_left] + [top_right] + top + left + right
    return {(block.x, block.y):block for block in blocks}

class Blocks(Observable):
    def __init__(self, start_x, width, start_y, height):
        super().__init__()
        self.blocks = {(x, y):Block(x, y, '%', Color.YELLOW, self.block_hit, 2)
                       for x in range(start_x, start_x + width, BLOCK_SIZE)
                       for y in range(start_y, start_y + height)}

    # surely this could be in the ctor too
    def add_border(self, width, height, color):
        self.blocks.update(get_border(width, height, color))

    def block_hit(self, coords):
        block = self.get_block(*coords)
        del self.blocks[(block.x, block.y)]
        self.emit('block_hit')

    def get_block(self, x, y):
        candidates = [self.blocks.get((cand_x, y), None)
                      for cand_x in range(x, x - BLOCK_SIZE - 1, -1)]
        block = reduce(lambda x,y: x if x else y, candidates, None)
        # todo: slightly nasty hack to stop incorrectly retrieving border blocks out of position
        if block and (block.x == x or block.size == BLOCK_SIZE):
            return block

    def draw(self, graphics):
        for block in self.blocks.values():
            block.draw(graphics)
