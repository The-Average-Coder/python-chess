import pygame

from input_handler import InputHandler
from renderer import Renderer
from Chess.board import Board

class Game:
    def __init__(self):
        self.board = Board()
        self.input_handler = InputHandler()
        self.renderer = Renderer()
    
    def handle_input(self, pygame_events):
        self.input_handler.handle_input(pygame_events, self.renderer, self.board)
    
    def render(self):
        self.renderer.render(self.board)