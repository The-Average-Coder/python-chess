import pygame

import input_handler
import renderer
from Chess.board import Board

class Game:
    def __init__(self):
        self.board = Board()
    
    def handle_input(self, pygame_events):
        input_handler.handle_input(pygame_events)
    
    def update(self):
        return
    
    def render(self, screen):
        renderer.render(screen, self.board)