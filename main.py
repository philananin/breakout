import curses

from datetime import datetime
from time import sleep

from game import Game
from renderer import CursesRenderer

def main(screen):
    screen.nodelay(1) # user input is non-blocking
    curses.curs_set(0) # don't display cursor

    # this has to align with the values in color.py... todo: think of a better way of doing so
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)

    max_y, max_x = screen.getmaxyx()
    renderer = CursesRenderer(screen, max_x, max_y)
    game = Game(max_x, max_y, renderer)

    last_frame_time = datetime.now()
    while True:
        now = datetime.now()
        time_diff = (now - last_frame_time).microseconds / float(1000000)
        last_frame_time = now

        user_input = screen.getch()
        no_user_input = user_input == -1
        if not no_user_input:
            game.handle_input(user_input)

        game.update(time_diff)
        game.render(screen)
        # todo: put fps limit in?
        sleep(0.01)

if __name__ == '__main__':
    curses.wrapper(main)

