import pygame
import ctypes

from game import Game

ctypes.windll.user32.SetProcessDPIAware()

pygame.init()

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
WINDOW_TITLE = 'Chess'

game = Game()

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)

    running = True
    while running:
        events = pygame.event.get()
        for i in events:
            if i.type == pygame.QUIT:
                running = False
        
        game.handle_input(events)
        game.render(screen)


    pygame.quit()

if __name__ == '__main__':
    main()