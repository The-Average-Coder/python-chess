import pygame

from Chess.Board.move_generator import MoveGenerator
from Chess.Board.move import Move
from Chess.Board.pre_computed_data import DISTANCE_TO_EDGE

class InputHandler:
    def __init__(self):
        self.selected_piece = -1
    
    def handle_input(self, pygame_events, renderer, board, chess_bot):
        move_generator = MoveGenerator(board)

        for event in pygame_events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_down(pygame.mouse.get_pos(), renderer, board, move_generator)
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse_up(pygame.mouse.get_pos(), renderer, board, move_generator)
            elif event.type == pygame.KEYUP and event.key == pygame.K_u:
                self.undo_move(board)
  
    def mouse_down(self, position, renderer, board, move_generator):
        clicked_square = renderer.board_ui.get_square_from_screen_position(position)

        if clicked_square == -1:
            return

        clicked_bitboard_position = board.get_bitboard_position_from_index(clicked_square)

        if not board.is_piece(clicked_bitboard_position) or board.is_white(clicked_bitboard_position) != board.white_to_move:
            return
        
        self.selected_piece = clicked_square
        legal_moves = move_generator.get_piece_legal_moves((clicked_square, board.get_bitboard_position_from_index(clicked_square)))
        renderer.board_ui.set_selected_piece(clicked_square, legal_moves, board)

    def mouse_up(self, position, renderer, board, move_generator):
        released_square = renderer.board_ui.get_square_from_screen_position(position)

        if released_square != -1 and self.selected_piece != -1:
            self.make_move(self.selected_piece, released_square, board, move_generator)

        self.selected_piece = -1
        renderer.board_ui.set_selected_piece(-1, [], board)
    
    def make_move(self, start_position, end_position, board, move_generator):
        start_bitboard_position = board.get_bitboard_position_from_index(start_position)

        move = None
        legal_moves = move_generator.get_piece_legal_moves((start_position, start_bitboard_position))

        for legal_move in legal_moves:
            if legal_move.end_position == end_position:
                move = legal_move
                break

        if not move:
            return

        board.make_move(move)
        board.moves.append(move)
    
    def undo_move(self, board):
        if len(board.moves) == 0:
            return
        
        board.undo_move(board.moves.pop(-1))
        
        if len(board.moves) % 2 == 1:
            board.undo_move(board.moves.pop(-1))