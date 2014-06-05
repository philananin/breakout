from datetime import datetime
from enum import Enum
import random
import time
import math
import curses
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('hello.log')
handler.setLevel(logging.INFO)
logger.addHandler(handler)

class Block(object):
    def __init__(self, pos, sym, color, on_hit):
        self.pos = pos
        self.on_hit = on_hit
        self.color = color
        self.sym = sym

    def hit(self):
        self.on_hit((self.pos.x, self.pos.y))

    def render(self, screen):
        max_y, max_x = screen.getmaxyx()
        if self.pos.x == max_x and self.pos.y == max_y:
            char = screen.getch(max_y, max_x - 1)
            screen.addstr(max_y, max_x - 1, self.sym)
            screen.insstr(max_y, max_x - 1, char)
        else:
            screen.addstr(self.pos.y, self.pos.x, self.sym, self.color)

class Vec2(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def translate(self, target):
        return Vec2(self.x + target.x, self.y + target.y)

    def scale(self, scalar):
        return Vec2(self.x * scalar, self.y * scalar)

class Plane(Enum):
    X = 0
    Y = 1
    BOTH = 2

class Ball:
    def __init__(self, pos):
        self.pos = pos
        self.angle = -math.pi/2 + random.uniform(-0.5, 0.5)
        self.direction_vec = Vec2(math.cos(self.angle),
                                  math.sin(self.angle))
        self.speed = 8 # move 8 blocks per second

    def update(self, paddle, blocks, dt):
        def get_new_position():
            logger.info('direction_vec: %f, %f', self.direction_vec.x, self.direction_vec.y)
            scaled = self.direction_vec.scale(dt * self.speed)
            logger.info('scaled: %f, %f', scaled.x, scaled.y)
            return self.pos.translate(scaled)

        # todo: technically we could cross more than one cell...
        def get_crossed_cell(old_pos, new_pos):
            crossed_x = math.floor(new_pos.x) != math.floor(old_pos.x)
            crossed_y = math.floor(new_pos.y) != math.floor(old_pos.y)

            if crossed_x and crossed_y:
                return (Vec2(math.floor(new_pos.x), math.floor(new_pos.y)),
                        Plane.BOTH)
            if crossed_x:
                return (Vec2(math.floor(new_pos.x), math.floor(new_pos.y)),
                        Plane.Y)
            if crossed_y:
                return (Vec2(math.floor(new_pos.x), math.floor(new_pos.y)),
                        Plane.X)

        def get_hit_block_and_crossed_plane(cell):
            logger.info('get_hit_block_and_crossed_plane called')
            block = blocks.get((cell[0].x, cell[0].y), None)
            if block:
                logger.info('block found: %s', block)
                return (block, cell[1])
            if paddle.occupies_cell(cell[0].x, cell[0].y):
                logger.info('paddle touches!')
                return (paddle, Plane.X)

        # todo
        def get_time_to_hit(hit_pos):
            return 0

        logger.info('dt: %d', dt)
        logger.info('old pos: %f, %f', self.pos.x, self.pos.y)
        new_pos = get_new_position()
        logger.info('new pos: %f, %f', new_pos.x, new_pos.y)

        # starting at a floored position makes this inaccurate, but a simple
        # implementation for now
        floored_x = int(math.floor(self.pos.x))
        floored_y = int(math.floor(self.pos.y))
        logger.info('floored_x: %d, floored_y: %d', floored_x, floored_y)
        crossed_cell = get_crossed_cell(self.pos, new_pos)

        if not crossed_cell:
            logger.info('no crossed cells')
            self.pos = new_pos
        else:
            result = get_hit_block_and_crossed_plane(crossed_cell)
            if not result:
                logger.info('no hit block')
                self.pos = new_pos
            else:
                logger.info('HIT BLOCK!')
                hit_block, plane = result
                time_to_hit = 0 # todo - paddle doesn't work with pos: get_time_to_hit(hit_block.pos)
                time_remaining = dt - time_to_hit
                self.bounce(plane)
                hit_block.hit()
                self.update(paddle, blocks, time_remaining)

    def bounce(self, plane):
        logger.info('bouncing! in plane %s', plane)
        logger.info('angle: %f', self.angle)
        logger.info('direction: %f, %f', self.direction_vec.x, self.direction_vec.y)
        if plane == Plane.X or plane == Plane.BOTH:
            self.angle = -self.angle
        if plane == Plane.Y or plane == Plane.BOTH:
            if self.angle >= 0:
                self.angle = math.pi - self.angle
            else:
                self.angle = -math.pi - self.angle
        logger.info('new angle: %f', self.angle)
        self.direction_vec = Vec2(math.cos(self.angle),
                                  math.sin(self.angle))
        logger.info('new direction: %f, %f', self.direction_vec.x, self.direction_vec.y)

class Paddle:
    def __init__(self, x, y):
        self.width = x // 5
        self.max_x = x
        self.x = x // 2 - self.width // 2
        self.y = y

    def occupies_cell(self, x, y):
        return self.y == y and x <= self.x + self.width and x >= self.x

    def hit(self):
        pass

    def move_left(self):
        if self.x > 0:
            self.x -= 1

    def move_right(self):
        if self.x + self.width < self.max_x:
            self.x += 1

class Game(object):
    def __init__(self, width, height):
        self.size = (width, height)
        self.in_play = False
        self.paddle = Paddle(width, height - 1)
        self.ball = Ball(Vec2(width // 2, height - 2))

        self.blocks = {}
        self.add_blocks(width, height)

    def add_blocks(self, width, height):
        self.add_border(width, height)
        yellow = curses.color_pair(1)

        for x in range(2, width - 3):
            for y in range(2, height // 2):
                self.blocks[(x, y)] = Block(Vec2(x, y), '%', yellow, self.blocks.pop)

    def add_border(self, width, height):
        do_nothing = lambda x: None
        green = curses.color_pair(2)

        self.blocks[(0, 0)] = Block(Vec2(0, 0), '╔', green, do_nothing)

        for x in range(1, width - 1):
            self.blocks[(x, 0)] = Block(Vec2(x, 0), '═', green, do_nothing)

        self.blocks[(width - 1, 0)] = Block(Vec2(width - 1, 0), '╗', green, do_nothing)

        for y in range (1, height - 1):
            self.blocks[(0, y)] = Block(Vec2(0, y), '║', green, do_nothing)
            self.blocks[(width - 1, y)] = Block(Vec2(width - 1, y), '║', green, do_nothing)

    def handle_input(self, user_input):
        if user_input == ord(' '):
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
        def clear_screen():
            for row in range(0, self.size[1] - 1):
                screen.addstr(row, 0, ' ' * self.size[0])

            # we can't write the last character normally with curses
            screen.addstr(self.size[1] - 1, 0, ' ' * (self.size[0] - 1))
            screen.insstr(self.size[1] - 1, self.size[0] - 1, ' ')

        clear_screen()
        self.render_blocks(screen)
        self.render_ball(screen)
        self.render_paddle(screen)
        screen.refresh()

    def render_ball(self, screen):
        floored_x = math.floor(self.ball.pos.x)
        floored_y = math.floor(self.ball.pos.y)
        screen.addstr(floored_y, floored_x, 'O')

    def render_blocks(self, screen):
        for pos, block in self.blocks.items():
            block.render(screen)

    def render_paddle(self, screen):
        if self.paddle.x + self.paddle.width > self.size[0]:
            screen.addstr(self.paddle.y, self.paddle.x, '=' * self.paddle.width)
        else:
            # we can't write the last character normally with curses
            screen.addstr(self.paddle.y,
                          self.paddle.x, '=' * (self.paddle.width-1))
            screen.insstr(self.paddle.y, self.paddle.x+1, '=')

def main(screen):
    screen.nodelay(1) # user input is non-blocking
    curses.curs_set(0) # don't display cursor
    curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)

    screen_y, screen_x = screen.getmaxyx()
    game = Game(screen_x, screen_y)

    last_frame_time = datetime.now()
    while True:
        now = datetime.now()
        dt = (now - last_frame_time).microseconds / float(1000000)
        last_frame_time = now

        user_input = screen.getch()
        no_user_input = user_input == -1
        if not no_user_input:
            game.handle_input(user_input)

        game.update(dt)
        game.render(screen)
        # todo: put fps limit in?
        time.sleep(0.01)

if __name__ == '__main__':
    curses.wrapper(main)
