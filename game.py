from color import Color
from block import Block
from paddle import Paddle, Direction
from ball import Ball

def beep():
    print('\a')

def get_border(width, height, color):
    top_left = Block(0, height, '╔', color)
    top_right = Block(width - 1, height, '╗', color)
    top = [Block(x, height, '═', color) for x in range(1, width - 1)]
    left = [Block(0, y, '║', color) for y in range(1, height)]
    right = [Block(width - 1, y, '║', color) for y in range(1, height)]
    blocks = [top_left] + [top_right] + top + left + right
    return {(block.x, block.y):block for block in blocks}

directions_map = {ord('h'):Direction.LEFT,
                  ord('l'):Direction.RIGHT}

class Game:
    def __init__(self, width, height):
        self.in_play = False
        self.finished = False
        self.points = 0
        self.paddle = Paddle(width)
        self.paddle.observe('hit', beep)
        self.ball = Ball(x=width // 2, y=1)
        self.ball.observe('miss', self.handle_miss)
        self.blocks = {(x, y):Block(x, y, '%', Color.YELLOW, self.block_hit, 2)
                       for x in range(2, width - 3, 2)
                       for y in range(height // 2, height - 2)}
        self.blocks.update(get_border(width, height - 1, Color.GREEN))

    def handle_miss(self):
        self.finished = True
        self.in_play = False

    def block_hit(self, coords):
        x, y = coords
        if not self.blocks.pop((x, y), None):
            self.blocks.pop((x - 1, y), None)
        self.points += 50

    def handle_input(self, user_input):
        if user_input == ord(' ') and not self.finished:
            self.in_play = not self.in_play
        if self.in_play:
            if user_input in directions_map:
                self.paddle.move(directions_map[user_input])
            else:
                self.paddle.no_movement()

    def update(self, dt):
        if self.in_play:
            self.paddle.update(dt)
            self.ball.update(self.paddle, self.blocks, dt)

    def draw(self, graphics):
        graphics.begin_frame()
        if self.finished:
            graphics.display_message('GAME OVER', Color.RED)
        else:
            self.ball.draw(graphics)
            self.paddle.draw(graphics)
            for block in self.blocks.values():
                block.draw(graphics)
        graphics.draw(1, graphics.max_y - 1, str(self.points), Color.RED)
        graphics.end_frame()
