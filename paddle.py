from color import Color
from observable import Observable

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

    def draw(self, graphics):
        paddle_icon = '=' * self.width
        graphics.draw(self.x, self.y, paddle_icon, Color.YELLOW)
