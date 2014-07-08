from color import Color
from paddle import Paddle, Direction
from ball import Ball
from blocks import Blocks

def beep():
    # god damn that gets annoying - find a better way
    pass
    #print('\a')

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
        self.blocks = Blocks(2, width - 5, height // 2, height // 2 - 2)
        self.blocks.add_border(width, height - 1, Color.GREEN)
        self.blocks.observe('block_hit', self.handle_block_hit)

    def handle_miss(self):
        self.finished = True
        self.in_play = False

    def handle_block_hit(self):
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
            # todo: ball shouldn't really need to know about paddle, blocks - break this up
            self.ball.update(self.paddle, self.blocks, dt)

    def draw(self, graphics):
        graphics.begin_frame()
        if self.finished:
            graphics.display_message('GAME OVER', Color.RED)
        else:
            self.ball.draw(graphics)
            self.paddle.draw(graphics)
            self.blocks.draw(graphics)
        graphics.draw(1, graphics.max_y - 1, str(self.points), Color.RED)
        graphics.end_frame()
