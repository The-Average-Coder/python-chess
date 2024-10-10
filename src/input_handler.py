import pygame

def handle_input(pygame_events):
    for event in pygame_events:
        if event == pygame.MOUSEBUTTONDOWN:
            mouse_down(pygame.mouse.get_pos())
        elif event == pygame.MOUSEBUTTONUP:
            continue

def mouse_down(position):
    return