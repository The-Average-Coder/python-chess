import pygame
import ctypes

from game import Game

ctypes.windll.user32.SetProcessDPIAware()

pygame.init()

game = Game()

def main():

    running = True
    while running:
        events = pygame.event.get()
        for i in events:
            if i.type == pygame.QUIT:
                running = False
        
        game.handle_input(events)
        game.render()


    pygame.quit()

if __name__ == '__main__':
    main()