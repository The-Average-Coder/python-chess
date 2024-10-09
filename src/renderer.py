import pygame
from UI import board_ui, colours

def render(screen, board):
    screen.fill(colours.WHITE)

    board_ui.render(screen, board)

    pygame.display.flip()