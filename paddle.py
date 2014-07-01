from color import Color

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
