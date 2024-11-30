import pygame

from UI import colours
from UI.board_ui import BoardUI
from UI.timer_ui import TimerUI

SCREEN_SIZE = (1600, 900)
WINDOW_TITLE = 'Chess'

CHESS_BOARD_POSITION = (350, 50)
WHITE_TIMER_POSITION = (1200, 550)
BLACK_TIMER_POSITION = (1200, 50)

class Renderer:
    def __init__(self):
        self.board_ui = BoardUI()
        self.white_timer = TimerUI()
        self.black_timer = TimerUI()
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption(WINDOW_TITLE)

    def render(self, game):
        self.screen.fill(colours.WHITE)

        self.board_ui.render(self.screen, game.board, CHESS_BOARD_POSITION)
        self.white_timer.render(self.screen, game.white_timer.time, WHITE_TIMER_POSITION, game.white_to_move)
        self.black_timer.render(self.screen, game.black_timer.time, BLACK_TIMER_POSITION, not game.white_to_move)

        pygame.display.flip()