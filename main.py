import random
import time
import curses

class Block:
    def __init__(self):
        self.alive = True

class Direction:
    UP = 0
    DOWN = 1

class Ball:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.touching_block = None
        self.touching_paddle = False

    def change_direction(self):
        self.touching_paddle = False
        self.touching_block = None
        self.direction = 1-self.direction

    def update(self, paddle, blocks):
        if self.touching_block is not None and self.touching_block.alive:
            self.remove_touching_block()
            self.change_direction()

        if self.touching_paddle:
            self.change_direction()

        self.move()
        self.check_collision(paddle, blocks)

    def remove_touching_block(self):
        self.touching_block.alive = False

    def move(self):
        if self.direction == Direction.UP:
            self.y -= 1
        else:
            self.y += 1

    def check_collision(self, paddle, blocks):
        if self.direction == Direction.UP:
            self.touching_block = blocks.get((self.x, self.y-1), None)
        else:
            self.touching_paddle = paddle.is_in_contact_with(self.x, self.y)

class Paddle:
    def __init__(self, x, y):
        self.width = x//5
        self.max_x = x
        self.x = x//2-self.width//2
        self.y = y

    def is_in_contact_with(self, x, y):
        return self.y == y+1 and x <= self.x + self.width and x >= self.x

    def move_left(self):
        if self.x > 0:
            self.x -= 1

    def move_right(self):
        if self.x + self.width < self.max_x:
            self.x += 1

class Game:
    def __init__(self, x, y):
        self.size = (x, y)
        self.add_blocks(x, y//2)
        self.in_play = False
        self.paddle = Paddle(x, y-1)
        # ball starts in the middle of the first row up
        self.ball = Ball(x // 2, y-2, Direction.UP)

    def add_blocks(self, cols, rows):
        self.blocks = {}
        for x in range(0, cols):
            for y in range(0, rows):
                self.blocks[(x, y)] = Block()

    def handle_input(self, user_input):
        if user_input == ord(' ') and self.in_play == False:
            self.in_play = True
        if self.in_play:
            if user_input == ord('h'):
                self.paddle.move_left()
            if user_input == ord('l'):
                self.paddle.move_right()

    def update(self):
        # also need to handle touching the edges
        # and resetting if we touch the bottom
        if self.in_play:
            self.ball.update(self.paddle, self.blocks)

    def remove_touching_block(self):
        self.ball.touching_block.alive = False

    def render(self, screen):
        self.clear_screen(screen)
        self.render_blocks(screen)
        self.render_ball(screen)
        self.render_paddle(screen)
        screen.refresh()

    def clear_screen(self, screen):
        for row in range(0, self.size[1]-1):
            screen.addstr(row, 0, ' '*self.size[0])

        # we can't write the last character normally with curses
        screen.addstr(self.size[1]-1, 0, ' '*(self.size[0]-1))
        screen.insstr(self.size[1]-1, self.size[0]-1, ' ')

    def render_ball(self, screen):
        screen.addstr(self.ball.y, self.ball.x, 'x')

    def render_blocks(self, screen):
        for pos, block in self.blocks.iteritems():
            if block.alive:
                screen.addstr(pos[1], pos[0], '#')
            else:
                screen.addstr(pos[1], pos[0], ' ')

    def render_paddle(self, screen):
        if self.paddle.x + self.paddle.width > self.size[0]:
            screen.addstr(self.paddle.y, self.paddle.x, '='*self.paddle.width)
        else:
            # we can't write the last character normally with curses
            screen.addstr(self.paddle.y, self.paddle.x, '='*(self.paddle.width-1))
            screen.insstr(self.paddle.y, self.paddle.x+1, '=')

def main(screen):
    screen.nodelay(1) # user input is non-blocking

    screen_y, screen_x = screen.getmaxyx()
    game = Game(screen_x, screen_y)

    while True:
        user_input = screen.getch()
        if user_input != -1:
            game.handle_input(user_input)

        game.update()
        game.render(screen)
        time.sleep(0.05)

if __name__ == '__main__':
    curses.wrapper(main)
