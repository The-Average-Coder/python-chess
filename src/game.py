import pygame

import renderer
from Chess.board import Board

class Game:
    def __init__(self):
        self.board = Board()
    
    def handle_input(self, pygame_events):
        return
    
    def update(self):
        return
    
    def render(self, screen):
        renderer.render(screen, self.board)