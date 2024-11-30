import pygame

from UI import colours
from UI.ui_element import UIElement

class TimerUI(UIElement):
    def __init__(self):
        self.font = pygame.font.Font('src/UI/fonts/Roboto-Light.ttf', 150)
    
    def render(self, screen, time, position, active=True):
        color = colours.BLACK if active else colours.DARK_GRAY
        text = self.font.render(f"{time // 60}:{time % 60 :02}", True, color)
        screen.blit(text, self.add_position_tuples(position, (20, 75)))

    def add_position_tuples(self, *tuples):
        return (sum([tuple[0] for tuple in tuples]), sum([tuple[1] for tuple in tuples]))