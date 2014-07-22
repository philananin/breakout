from enum import Enum
from color import Color
from observable import Observable

ACCELERATION = 4
FRICTION = 0.25

class Direction(Enum):
    LEFT = 0
    RIGHT = 1

class Paddle(Observable):
    def __init__(self, max_x):
        super().__init__()
        self.width = max_x // 5
        self.max_x = max_x - self.width
        self.x = max_x // 2 - self.width // 2
        self.y = 0
        self.direction = None
        self.no_move = True
        self.velocity = 0
        self.move_has_changed = False

    def occupies_cell(self, x, y):
        return self.y == y and x <= self.x + self.width and x >= self.x

    def hit(self):
        self.emit('hit')

    def move(self, direction):
        self.move_has_changed = self.direction != direction
        self.direction = direction
        self.no_move = False

    def no_movement(self):
        self.move_has_changed = not self.no_move
        self.no_move = True

    def update(self, dt):
        if self.no_move:
            self.velocity -= FRICTION * dt
            self.velocity = self.velocity if self.velocity > 0 else 0
        elif self.move_has_changed or self.velocity == 0:
            self.velocity = 0.25
        else:
            self.velocity += self.velocity * ACCELERATION * dt

        if self.direction == Direction.LEFT:
            self.x -= self.velocity
        elif self.direction == Direction.RIGHT:
            self.x += self.velocity

        self.move_has_changed = False
        self.guard_limits()

    def guard_limits(self):
        self.x = self.x if self.x > 0 else 0
        self.x = self.x if self.x <= self.max_x else self.max_x

    def draw(self, graphics):
        paddle_icon = '=' * self.width
        graphics.draw(self.x, self.y, paddle_icon, Color.YELLOW)
