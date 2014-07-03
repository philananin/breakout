from math import cos, sin, pi, floor
from random import uniform as random_between
from enum import Enum

from color import Color

class Vec2:
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
        self.angle = pi/2 + random_between(-0.5, 0.5)
        self.direction_vec = Vec2(cos(self.angle), sin(self.angle))
        self.speed = 12 # move 12 blocks per second
        self.miss_callback = miss_callback

    def update(self, paddle, blocks, dt):
        def get_new_position():
            scaled_dir = self.direction_vec.scale(dt * self.speed)
            return self.pos.translate(scaled_dir)

        # todo: technically we could cross more than one cell...
        def get_crossed_cell(old_pos, new_pos):
            new_cell_x = floor(new_pos.x)
            new_cell_y = floor(new_pos.y)
            crossed_x = new_cell_x != floor(old_pos.x)
            crossed_y = new_cell_y != floor(old_pos.y)
            if crossed_x and crossed_y:
                return (new_cell_x, new_cell_y, Plane.BOTH)
            if crossed_x:
                return (new_cell_x, new_cell_y, Plane.Y)
            if crossed_y:
                return (new_cell_x, new_cell_y, Plane.X)

        def get_hit_block(x, y):
            block = blocks.get((x, y), None) or blocks.get((x + 1, y))
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
                self.angle = pi - self.angle
            else:
                self.angle = -pi - self.angle
        self.direction_vec = Vec2(cos(self.angle), sin(self.angle))

    def draw(self, graphics):
        graphics.draw(self.pos.x, self.pos.y, 'o', Color.YELLOW)
