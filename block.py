class Block(object):
    def __init__(self, x, y, sym, color, on_hit=lambda x: None, size=1):
        self.x, self.y = x, y
        self.sym = sym
        self.color = color
        self.on_hit = on_hit
        self.size = size

    def hit(self):
        self.on_hit((self.x, self.y))

    def render(self, renderer):
        renderer.render(self.x, self.y, self.sym * self.size, self.color)
