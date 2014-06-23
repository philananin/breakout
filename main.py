from datetime import datetime
from enum import IntEnum, Enum
import random
import time
import math
import curses
import os
import subprocess

class Block(object):
    def __init__(self, x, y, sym, color, on_hit):
        self.x = x
        self.y = y
        self.color = color
        self.sym = sym
        self.on_hit = on_hit

    def hit(self):
        self.on_hit((self.x, self.y))

    def render(self, renderer):
        renderer.render(self.x, self.y, self.sym, self.color)

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
    def __init__(self, width, miss_callback):
        self.pos = Vec2(width // 2, 1)
        self.angle = math.pi/2 + random.uniform(-0.5, 0.5)
        self.direction_vec = Vec2(math.cos(self.angle),
                                  math.sin(self.angle))
        self.speed = 12 # move 12 blocks per second
        self.miss_callback = miss_callback

    def update(self, paddle, blocks, dt):
        def get_new_position():
            scaled_dir = self.direction_vec.scale(dt * self.speed)
            return self.pos.translate(scaled_dir)

        # todo: technically we could cross more than one cell...
        def get_crossed_cell(old_pos, new_pos):
            new_cell_x = math.floor(new_pos.x)
            new_cell_y = math.floor(new_pos.y)
            crossed_x = new_cell_x != math.floor(old_pos.x)
            crossed_y = new_cell_y != math.floor(old_pos.y)
            if crossed_x and crossed_y:
                return (new_cell_x, new_cell_y, Plane.BOTH)
            if crossed_x:
                return (new_cell_x, new_cell_y, Plane.Y)
            if crossed_y:
                return (new_cell_x, new_cell_y, Plane.X)

        def get_hit_block(x, y):
            block = blocks.get((x, y), None)
            if block:
                return block
            if paddle.occupies_cell(x, y):
                return paddle

        # todo
        def get_time_to_hit(x, y, plane):
            return 0

        new_pos = get_new_position()
        # todo: i don't like hard-coding this here
        if new_pos.y < 0:
            self.miss_callback()
        else:
            crossed_cell = get_crossed_cell(self.pos, new_pos)
            if not crossed_cell:
                self.pos = new_pos
            else:
                crossed_x, crossed_y, crossed_plane = crossed_cell
                hit_block = get_hit_block(crossed_x, crossed_y)
                if not hit_block:
                    self.pos = new_pos
                else:
                    time_to_hit = get_time_to_hit(crossed_x, crossed_y, crossed_plane)
                    time_remaining = dt - time_to_hit
                    self.bounce(crossed_plane)
                    hit_block.hit()
                    self.update(paddle, blocks, time_remaining)

    def bounce(self, plane):
        if plane == Plane.X or plane == Plane.BOTH:
            self.angle = -self.angle
        if plane == Plane.Y or plane == Plane.BOTH:
            if self.angle >= 0:
                self.angle = math.pi - self.angle
            else:
                self.angle = -math.pi - self.angle
        self.direction_vec = Vec2(math.cos(self.angle), math.sin(self.angle))

    def render(self, renderer):
        renderer.render(self.pos.x, self.pos.y, 'o', Color.YELLOW)

# todo: this probably isn't a very pythonic way to do this
class Observable:
    def __init__(self):
        self.observers = {}

    def observe(self, event, observer):
        existing = self.observers.get(event, None)
        if existing:
            existing.append(observer)
        else:
            self.observers[event] = [observer]

    def emit(self, event):
        if event in self.observers:
            for observer in self.observers[event]:
                observer()

class Paddle(Observable):
    def __init__(self, max_x):
        super().__init__()
        self.width = max_x // 5
        self.max_x = max_x
        self.x = max_x // 2 - self.width // 2
        self.y = 0

    def occupies_cell(self, x, y):
        return self.y == y and x <= self.x + self.width and x >= self.x

    def hit(self):
        self.emit('hit')

    def move_left(self):
        if self.x > 0:
            self.x -= 1

    def move_right(self):
        if self.x + self.width < self.max_x:
            self.x += 1

    def render(self, renderer):
        paddle_icon = '=' * self.width
        renderer.render(self.x, self.y, paddle_icon, Color.YELLOW)

class Renderer:
    def __init__(self, screen, max_x, max_y):
        self.screen = screen
        self.max_x = max_x
        self.max_y = max_y

    def clear(self):
        for row in range(0, self.max_y):
            self.render(0, row, ' ' * self.max_x)

    def render(self, x, y, string, color = 1):
        x = int(x)
        y = int(y)
        string_len = len(string)
        last_x = x + string_len
        if last_x > self.max_x:
            max_len = string_len - (last_x - self.max_x)
            string = string[:max_len]

        if y > self.max_y:
            y = self.max_y

        curses_color = curses.color_pair(color)
        flip_y = self.max_y - 1 - y

        if y == 0 and x + len(string) == self.max_x:
            # curses cannot directly output to the last cell
            all_but_first = string[1:]
            self.screen.addstr(flip_y, x, all_but_first, curses_color)
            self.screen.insstr(flip_y, x, string[0], curses_color)
        else:
            self.screen.addstr(flip_y, x, string, curses_color)

    def render_points(self, points):
        self.render(1, self.max_y - 1, str(points), Color.RED)

    def render_message(self, message):
        # todo: handle small screen widths
        starting_x = self.max_x // 2 - (len(message) // 2)
        self.render(starting_x, self.max_y // 2, message, Color.YELLOW)

class Color(IntEnum):
    # todo: where would be a more natural place for this logic?
    @classmethod
    def init(cls):
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)

    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4

class Game(object):
    def __init__(self, width, height, renderer):
        self.size = (width, height)
        self.in_play = False
        self.finished = False
        self.renderer = renderer # todo: remove
        self.paddle = Paddle(width)
        self.paddle.observe('hit', self.beep)
        self.ball = Ball(width, self.handle_miss)
        self.blocks = {}
        self.add_blocks(width, height)
        self.points = 0

    def beep(self):
        print('\a')

    def handle_miss(self):
        self.finished = True
        self.in_play = False

    def handle_block_hit(self, coords):
        self.blocks.pop(coords)
        self.points += 50

    def add_blocks(self, width, height):
        self.add_border(width, height)
        for x in range(2, width - 3):
            for y in range(height // 2, height - 2):
                self.blocks[(x, y)] = Block(x, y, '%', Color.YELLOW,
                                            self.handle_block_hit)

    def add_border(self, width, height):
        noop = lambda x: None
        green = Color.GREEN

        self.blocks[(0, height - 1)] = Block(0, height - 1, '╔', green, noop)
        self.blocks[(width - 1, height - 1)] = Block(width - 1, height - 1, '╗', green, noop)

        for x in range(1, width - 1):
            self.blocks[(x, height - 1)] = Block(x, height - 1, '═', green, noop)

        for y in range (1, height - 1):
            self.blocks[(0, y)] = Block(0, y, '║', green, noop)
            self.blocks[(width - 1, y)] = Block(width - 1, y, '║', green, noop)

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

def main(screen):
    screen.nodelay(1) # user input is non-blocking
    curses.curs_set(0) # don't display cursor
    Color.init()

    max_y, max_x = screen.getmaxyx()
    renderer = Renderer(screen, max_x, max_y)
    game = Game(max_x, max_y, renderer)

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

