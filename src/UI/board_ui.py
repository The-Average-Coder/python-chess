import pygame

chess_board = pygame.image.load("./src/UI/images/chess_board.png")

def render(screen, board):
    screen.blit(chess_board, (400, 50))