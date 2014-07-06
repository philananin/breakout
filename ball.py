from math import cos, sin, pi, floor
from random import uniform as random_between
from enum import Enum
from color import Color
from observable import Observable

def is_miss(y_pos):
    return y_pos < 0

class Plane(Enum):
    X = 0
    Y = 1

class Ball(Observable):
    def __init__(self, x, y):
        super().__init__()
        self.x, self.y = x, y
        self.angle = pi/2 + random_between(-0.5, 0.5)
        self.speed = 12 # move 12 blocks per second

    def update(self, paddle, blocks, dt):
        def get_new_position():
            scaled_speed = dt * self.speed
            dir_x, dir_y = cos(self.angle), sin(self.angle)
            scaled_x, scaled_y = dir_x * scaled_speed, dir_y * scaled_speed
            return self.x + scaled_x, self.y + scaled_y

        # todo: technically we could cross more than one cell...
        def get_crossed_cell(new_x, new_y):
            new_cell_x = floor(new_x)
            new_cell_y = floor(new_y)
            crossed_x = new_cell_x != floor(self.x)
            crossed_y = new_cell_y != floor(self.y)
            if crossed_y:
                return (new_cell_x, new_cell_y, Plane.X)
            if crossed_x:
                return (new_cell_x, new_cell_y, Plane.Y)

        def get_hit_block(x, y):
            block = blocks.get((x, y), None) or blocks.get((x - 1, y))
            if block:
                return block
            if paddle.occupies_cell(x, y):
                return paddle

        # todo
        def get_time_to_hit(x, y, plane):
            return 0

        new_x, new_y = get_new_position()
        # todo: i don't like hard-coding this here
        if is_miss(new_y):
            self.emit('miss')
        else:
            crossed_cell = get_crossed_cell(new_x, new_y)
            if not crossed_cell:
                self.x, self.y = new_x, new_y
            else:
                crossed_x, crossed_y, crossed_plane = crossed_cell
                hit_block = get_hit_block(crossed_x, crossed_y)
                if not hit_block:
                    self.x, self.y = new_x, new_y
                else:
                    time_to_hit = get_time_to_hit(crossed_x, crossed_y, crossed_plane)
                    time_remaining = dt - time_to_hit
                    self.bounce(crossed_plane)
                    hit_block.hit()
                    self.update(paddle, blocks, time_remaining)

    def bounce(self, plane):
        if plane == Plane.X:
            self.angle = -self.angle
        if plane == Plane.Y:
            if self.angle >= 0:
                self.angle = pi - self.angle
            else:
                self.angle = -pi - self.angle

    def draw(self, graphics):
        graphics.draw(self.x, self.y, 'o', Color.YELLOW)
