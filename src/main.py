import pygame, sys, ctypes

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
        game.simulate()
        game.render()


    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()