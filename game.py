from color import Color
from block import Block
from paddle import Paddle
from ball import Ball

class Game(object):
    def __init__(self, width, height, renderer):
        self.in_play = False
        self.finished = False
        self.points = 0
        self.renderer = renderer
        self.paddle = Paddle(width)
        self.paddle.observe('hit', self.beep)
        self.ball = Ball(width, self.handle_miss)
        self.blocks = {(x, y):Block(x, y, '%', Color.YELLOW, self.block_hit, 2)
                       for x in range(2, width - 3, 2)
                       for y in range(height // 2, height - 2)}
        self.add_border(width, height)

    def beep(self):
        print('\a')

    def handle_miss(self):
        self.finished = True
        self.in_play = False

    def block_hit(self, coords):
        x, y = coords
        if not self.blocks.pop((x, y), None):
            self.blocks.pop((x + 1, y), None)
        self.points += 50

    def add_border(self, width, height):
        green = Color.GREEN

        self.blocks[(0, height - 1)] = Block(0, height - 1, '╔', green)
        self.blocks[(width - 1, height - 1)] = Block(width - 1, height - 1, '╗', green)

        for x in range(1, width - 1):
            self.blocks[(x, height - 1)] = Block(x, height - 1, '═', green)

        for y in range (1, height - 1):
            self.blocks[(0, y)] = Block(0, y, '║', green)
            self.blocks[(width - 1, y)] = Block(width - 1, y, '║', green)

    def handle_input(self, user_input):
        if user_input == ord(' ') and not self.finished:
            self.in_play = not self.in_play
        if self.in_play:
            if user_input == ord('h'):
                self.paddle.move_left()
            if user_input == ord('l'):
                self.paddle.move_right()

    def update(self, dt):
        # todo: handle resetting if we touch the bottom
        if self.in_play:
            self.ball.update(self.paddle, self.blocks, dt)

    def render(self, screen):
        self.renderer.clear()
        if self.finished:
            self.renderer.render_message('GAME OVER')
        else:
            self.ball.render(self.renderer)
            self.paddle.render(self.renderer)
            for pos, block in self.blocks.items():
                block.render(self.renderer)
        self.renderer.render_points(self.points)
        screen.refresh()
