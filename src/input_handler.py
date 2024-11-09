import pygame

import chess_bot
from Chess.move import Move
from Chess.distance_to_edge import DISTANCE_TO_EDGE

class InputHandler:
    def __init__(self):
        self.selected_piece = -1
    
    def handle_input(self, pygame_events, renderer, board):
        legal_moves = board.get_legal_moves()
        if len(legal_moves) > 0 and not board.white_move:
            chess_bot.make_move(board)

        for event in pygame_events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_down(pygame.mouse.get_pos(), renderer, board)
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse_up(pygame.mouse.get_pos(), renderer, board)
            elif event.type == pygame.KEYUP and event.key == pygame.K_u:
                self.undo_move(board)
  
    def mouse_down(self, position, renderer, board):
        clicked_square = renderer.board_ui.get_square_from_screen_position(position)

        if clicked_square == -1:
            return

        clicked_bitboard_position = board.get_bitboard_position_from_index(clicked_square)

        if not board.is_piece(clicked_bitboard_position) or board.is_white(clicked_bitboard_position) != board.white_move:
            return
        
        self.selected_piece = clicked_square
        renderer.board_ui.set_selected_piece(clicked_square, board)

    def mouse_up(self, position, renderer, board):
        released_square = renderer.board_ui.get_square_from_screen_position(position)

        if released_square != -1 and self.selected_piece != -1:
            self.make_move(self.selected_piece, released_square, board)

        self.selected_piece = -1
        renderer.board_ui.set_selected_piece(-1, board)
    
    def make_move(self, start_position, end_position, board):
        start_bitboard_position = board.get_bitboard_position_from_index(start_position)
        end_bitboard_position = board.get_bitboard_position_from_index(end_position)

        move = None
        legal_moves = board.get_piece_legal_moves(start_position, start_bitboard_position)

        for legal_move in legal_moves:
            if legal_move.end_bitboard_position == end_bitboard_position:
                move = legal_move
                continue

        if not move:
            return

        board.make_move(move)
        board.moves.append(move)

        if len(board.get_legal_moves()) == 0:
            if board.white_in_check or board.black_in_check:
                print("Checkmate")
            else:
                print("Stalemate")
    
    def undo_move(self, board):
        if len(board.moves) == 0:
            return
        
        board.undo_move(board.moves.pop(-1))
        
        if len(board.moves) % 2 == 1:
            board.undo_move(board.moves.pop(-1))