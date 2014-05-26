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

        if self.direction == Direction.UP:
            self.direction = Direction.DOWN
        else:
            self.direction = Direction.UP

    def move(self):
        if self.direction == Direction.UP:
            self.y -= 1
        else:
            self.y += 1

    def check_collision(self, paddle, blocks):
        if self.direction == Direction.UP:
            if (self.x, self.y-1) in blocks:
                self.touching_block = blocks[(self.x, self.y-1)]
            else:
                self.touching_block = None
        else:
            if paddle.touches(self.x, self.y):
                self.touching_paddle = True
            else:
                self.touching_paddle = False

class Paddle:
    def __init__(self, x, y):
        self.width = x # for now cover whole of bottom row
        self.x = 0
        self.y = y

    def touches(self, x, y):
        y+1 == self.y

class Game:
    def __init__(self, x, y):
        self.size = (x, y)
        self.blocks_start_at_row = y // 2
        self.add_blocks(x, self.blocks_start_at_row)
        self.in_play = False
        self.paddle = Paddle(x-1, y-1)

        # ball starts in the middle of the first row up
        self.ball = Ball(x // 2, y-2, Direction.UP)

    def add_blocks(self, cols, rows):
        self.blocks = {}
        for x in range(0, cols - 1):
            for y in range(0, rows):
                self.blocks[(x, y)] = Block()

    def handle_input(self, user_input):
        if user_input == ord(' ') and self.in_play == False:
            self.in_play = True

    def update(self):
        if self.ball.touching_block is not None:
            self.remove_touching_block()
            self.ball.change_direction()

        if self.ball.touching_paddle:
            self.ball.change_direction()

        if self.in_play:
            self.ball.move()
            self.ball.check_collision(self.paddle, self.blocks)

    def remove_touching_block(self):
        self.ball.touching_block.alive = False

    def render(self, screen):
        self.render_ball(screen)
        self.render_blocks(screen)
        screen.refresh()

    def render_ball(self, screen):
        # pretty inefficient for now... just wipe out all non-block cells
        # before drawing the ball
        for row in range(self.blocks_start_at_row, self.size[1]-1):
            for col in range(0, self.size[0]-1):
                screen.addstr(row, col, ' ')
        screen.addstr(self.ball.y, self.ball.x, 'x')

    def render_blocks(self, screen):
        for pos, block in self.blocks.iteritems():
            if block.alive:
                screen.addstr(pos[1], pos[0], '#')
            else:
                screen.addstr(pos[1], pos[0], ' ')

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
