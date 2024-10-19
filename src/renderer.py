import pygame

from UI import colours
from UI.board_ui import BoardUI

SCREEN_SIZE = (1600, 900)
WINDOW_TITLE = 'Chess'

CHESS_BOARD_POSITION = (400, 50)

class Renderer:
    def __init__(self):
        self.board_ui = BoardUI(CHESS_BOARD_POSITION)
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption(WINDOW_TITLE)

    def render(self, board):
        self.screen.fill(colours.WHITE)

        self.board_ui.render(self.screen, board)

        pygame.display.flip()