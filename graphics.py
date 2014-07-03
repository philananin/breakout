import curses
from math import floor

class CursesGraphics:
    def __init__(self, screen, max_x, max_y):
        self.screen, self.max_x, self.max_y = screen, max_x, max_y

    def begin_frame(self):
        for row in range(0, self.max_y):
            self.draw(0, row, ' ' * self.max_x)

    def end_frame(self):
        self.screen.refresh()

    def draw(self, x, y, string, color=1):
        x = floor(x)
        y = floor(y)
        assert(x + len(string) <= self.max_x)
        assert(y <= self.max_y)

        curses_color = curses.color_pair(color)
        flip_y = self.max_y - 1 - y

        if self.will_draw_last_cell(x, y, string):
            # curses cannot directly output to the last cell
            all_but_first = string[1:]
            self.screen.addstr(flip_y, x, all_but_first, curses_color)
            self.screen.insstr(flip_y, x, string[0], curses_color)
        else:
            self.screen.addstr(flip_y, x, string, curses_color)

    def will_draw_last_cell(self, x, y, string):
        return y == 0 and x + len(string) == self.max_x

    def display_message(self, message, color):
        center_x = self.max_x // 2 - (len(message) // 2)
        center_y = self.max_y // 2
        self.draw(center_x, center_y, message, color)
