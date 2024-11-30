from input_handler import InputHandler
from renderer import Renderer
from Chess.Board.board import Board
from Chess.Board.move_generator import MoveGenerator
from Chess.AI.chess_bot import ChessBot
from Chess.timer import Timer

COMPUTER_IS_WHITE = False

class Game:
    def __init__(self):
        self.board = Board()
        self.input_handler = InputHandler()
        self.renderer = Renderer()

        self.chess_bot = ChessBot(self.board)

        self.white_timer = Timer()
        self.black_timer = Timer()

        self.white_to_move = self.board.white_to_move
        self.computer_is_white = COMPUTER_IS_WHITE

        self.render()
    
    def handle_input(self, pygame_events):
        self.input_handler.handle_input(pygame_events, self.renderer, self.board, self.chess_bot)
    
    def simulate(self):
        move_generator = MoveGenerator(self.board)
        legal_moves = move_generator.get_legal_moves()

        if len(move_generator.get_legal_moves()) == 0:
            if self.board.previous_positions.count(self.board.zobrist_key) >= 3:
                print("Stalemate.")
            elif self.board.player_in_check:
                print("Checkmate.")
            else:
                print("Stalemate.")
            return
        
        if self.white_timer.time <= 0:
            print("White Timeout. Black win.")
            self.white_timer.stop_timer()
            return
        elif self.black_timer.time <= 0:
            print("Black Timeout. White win.")
            self.black_timer.stop_timer()
            return
        
        if self.white_to_move == self.computer_is_white:
            move, evaluation = self.chess_bot.find_move()
            self.board.make_move(move)
            self.board.moves.append(move)  
        
        if self.white_to_move and not self.board.white_to_move:
            self.white_timer.stop_timer()
            self.black_timer.start_timer()
            self.white_to_move = self.board.white_to_move
        elif not self.white_to_move and self.board.white_to_move:
            self.black_timer.stop_timer()
            self.white_timer.start_timer()
            self.white_to_move = self.board.white_to_move    
    
    def render(self):
        self.renderer.render(self)