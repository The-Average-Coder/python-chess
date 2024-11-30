import math, random, time

from Chess import openings_dictionary
from Chess.Board import pieces
from Chess.Board.move_generator import MoveGenerator

from Chess.AI.pre_computed_data import *

class ChessBot:
    def __init__(self, board):
        self.board = board
        self.is_opening_theory = True
        self.current_line = openings_dictionary.openings
    
    def find_move(self):
        move, evaluation = None, 0

        if self.is_opening_theory:
            move = self.get_book_move()
            evaluation = 0
        
        if move is None:
            start_time = time.perf_counter()
            transposition_table = {}
            depth = 3
            evaluation, move, positions_searched = search(self.board, depth, -1_000_000_000, 1_000_000_000, transposition_table)
            print(f"Depth: {depth}, Eval: {evaluation}, Positions Searched: {positions_searched}, Time Taken: {round(time.perf_counter() - start_time, 1)}")

        if move is None:
            move_generator = MoveGenerator(self.board)
            move = move_generator.get_legal_moves()[0]
            evaluation = evaluate(self.board)
        
        return move, evaluation
    
    def get_book_move(self):
        if len(self.board.moves) > 0:
            previous_move_square = move_to_square(self.board.moves[-1], self.board)
            if previous_move_square not in self.current_line:
                self.is_opening_theory = False
                return None
            self.current_line = self.current_line[previous_move_square]
            if len(self.current_line) == 0:
                self.is_opening_theory = False
                return None
            end_square = random.choice(list(self.current_line.keys()))
            self.current_line = self.current_line[end_square]
        else:
            end_square = random.choice(list(self.current_line.keys()))
            self.current_line = self.current_line[end_square]

        return square_to_move(end_square, self.board)


def search(board, depth, alpha, beta, transposition_table):
    if board.previous_positions.count(board.zobrist_key) >= 3:
        return 0, None, 1

    shallow_best_move = None
    if board.zobrist_key in transposition_table:
        if transposition_table[board.zobrist_key][0] >= depth:
            return transposition_table[board.zobrist_key][1], transposition_table[board.zobrist_key][2], 1
        else:
            shallow_best_move = transposition_table[board.zobrist_key][2]

    if depth == 0:
        return search_captures(board, alpha, beta, transposition_table)

    move_generator = MoveGenerator(board)
    legal_moves = move_generator.get_legal_moves()

    if len(legal_moves) == 0:
        if board.white_in_check or board.black_in_check:
            return -1_000_000_000 * depth, None, 1
        else:
            return 0, None, 1

    legal_moves.sort(key=lambda move: -1_000_000 if shallow_best_move is not None and move.start_bitboard_position & shallow_best_move.start_bitboard_position and move.end_bitboard_position & move.end_bitboard_position and not shallow_best_move.is_promotion else -move.capture_value)

    best_move = None

    positions_searched = 0

    for move in legal_moves:
        board.make_move(move)
        move_evaluation, _, new_positions = search(board, depth-1, -beta, -alpha, transposition_table)
        move_evaluation *= -1
        board.undo_move(move)
        positions_searched += new_positions
        if move_evaluation >= beta:
            return beta, move, positions_searched
        if move_evaluation > alpha:
            best_move = move
            alpha = move_evaluation
    
    if best_move != None:
        transposition_table[board.zobrist_key] = (depth, alpha, best_move)

    return alpha, best_move, positions_searched

def search_captures(board, alpha, beta, transposition_table):
    evaluation = evaluate(board)
    if (evaluation >= beta):
        return beta, None, 1
    alpha = max(alpha, evaluation)

    move_generator = MoveGenerator(board)
    legal_moves = move_generator.get_legal_moves()

    if len(legal_moves) == 0:
        if board.white_in_check or board.black_in_check:
            return -1_000_000_000, None, 1
        else:
            return 0, None, 1
    
    legal_captures = [move for move in legal_moves if move.is_capture]

    if len(legal_captures) == 0:
        return alpha, None, 1
    
    legal_captures.sort(key=lambda move: -move.capture_value)

    best_move = legal_moves[0]

    positions_searched = 0

    for move in legal_captures:
        board.make_move(move)
        move_evaluation, _, new_positions = search_captures(board, -beta, -alpha, transposition_table)
        move_evaluation *= -1
        board.undo_move(move)
        positions_searched += new_positions
        if move_evaluation >= beta:
            return beta, move, positions_searched
        if move_evaluation > alpha:
            best_move = move
            alpha = move_evaluation
    
    return alpha, best_move, positions_searched

def evaluate(board):
    evaluation = 0

    white_pieces = board.bitboard_to_bitboard_positions(board.pieces[pieces.WHITE])
    black_pieces = board.bitboard_to_bitboard_positions(board.pieces[pieces.BLACK])
    white_piece_count = bin(board.pieces[pieces.WHITE] & (board.pieces[pieces.KNIGHT] | board.pieces[pieces.BISHOP] | board.pieces[pieces.ROOK] | board.pieces[pieces.QUEEN])).count('1')
    black_piece_count = bin(board.pieces[pieces.BLACK] & (board.pieces[pieces.KNIGHT] | board.pieces[pieces.BISHOP] | board.pieces[pieces.ROOK] | board.pieces[pieces.QUEEN])).count('1')

    for piece in white_pieces:
        position, bitboard_position = piece[0], piece[1]
        if board.is_pawn(bitboard_position):
            if white_piece_count > 3:
                position_evaluation = PAWN_WEIGHTS[position]
            else:
                position_evaluation = PAWN_ENDGAME_WEIGHTS[position]
            evaluation += PAWN_VALUE + position_evaluation
        elif board.is_knight(bitboard_position):
            evaluation += KNIGHT_VALUE + KNIGHT_WEIGHTS[position]
        elif board.is_bishop(bitboard_position):
            evaluation += BISHOP_VALUE + BISHOP_WEIGHTS[position]
        elif board.is_rook(bitboard_position):
            evaluation += ROOK_VALUE + ROOK_WEIGHTS[position]
        elif board.is_queen(bitboard_position):
            evaluation += QUEEN_VALUE + QUEEN_WEIGHTS[position]
        else:
            if white_piece_count > 3:
                evaluation += KING_EARLY_WEIGHTS[position]
            else:
                evaluation += KING_ENDGAME_WEIGHTS[position]
    for piece in black_pieces:
        position, bitboard_position = 63-piece[0], piece[1]
        if board.is_pawn(bitboard_position):
            if black_piece_count > 3:
                position_evaluation = PAWN_WEIGHTS[position]
            else:
                position_evaluation = PAWN_ENDGAME_WEIGHTS[position]
            evaluation -= PAWN_VALUE + position_evaluation
        elif board.is_knight(bitboard_position):
            evaluation -= KNIGHT_VALUE + KNIGHT_WEIGHTS[position]
        elif board.is_bishop(bitboard_position):
            evaluation -= BISHOP_VALUE + BISHOP_WEIGHTS[position]
        elif board.is_rook(bitboard_position):
            evaluation -= ROOK_VALUE + ROOK_WEIGHTS[position]
        elif board.is_queen(bitboard_position):
            evaluation -= QUEEN_VALUE + QUEEN_WEIGHTS[position]
        else:
            if black_piece_count > 3:
                evaluation -= KING_EARLY_WEIGHTS[position]
            else:
                evaluation -= KING_ENDGAME_WEIGHTS[position]

    if not board.white_to_move: evaluation *= -1

    return evaluation

def index_position_to_human_position(position):
    file = 'abcdefgh'[position % 8]
    rank = str((63 - position) // 8 + 1)
    return file + rank

def human_position_to_bitboard_position(square):
    file = 'abcdefgh'.index(square[0])
    rank = 8 - int(square[1])
    return 1 << rank * 8 + file

def get_piece_letter(piece_type):
    if piece_type == pieces.PAWN: return ''
    if piece_type == pieces.KNIGHT: return 'N'
    if piece_type == pieces.BISHOP: return 'B'
    if piece_type == pieces.ROOK: return 'R'
    if piece_type == pieces.QUEEN: return 'Q'
    if piece_type == pieces.KING: return 'K'

def move_to_square(move, board):
    end_square = index_position_to_human_position(move.end_position)
    piece_type = board.get_piece_type(2**move.end_position)
    capture_info = ''
    if move.is_capture:
        if board.is_pawn(2**move.end_position):
            capture_info += index_position_to_human_position(move.start_position)[0]
        capture_info += 'x'
    return get_piece_letter(piece_type) + capture_info + end_square

def square_to_move(square, board):
    end_bitboard_position = human_position_to_bitboard_position(square[-2] + square[-1])
    move_generator = MoveGenerator(board)
    legal_moves = move_generator.get_legal_moves()
    for move in legal_moves:
        if 2**move.end_position == end_bitboard_position:
            piece_letter = get_piece_letter(board.get_piece_type(2**move.start_position))
            if len(square) == 2 and piece_letter == '':
                return move
            if square[0] == piece_letter:
                return move
            
    return None
            