import math, random, time
from Chess import openings_dictionary, pieces

PAWN_VALUE = 100
KNIGHT_VALUE = 300
BISHOP_VALUE = 330
ROOK_VALUE = 500
QUEEN_VALUE = 900

PAWN_WEIGHTS = [
    0, 0, 0, 0, 0, 0, 0, 0,
    5, 5, 5, 5, 5, 5, 5, 5,
    1, 1, 2, 3, 3, 2, 1, 1,
    0.5, 0.5, 1, 2.5, 2.5, 1, 0.5, 0.5,
    0, 0, 0, 2, 2, 0, 0, 0,
    0.5, -0.5, -1, 0, 0, -1, -0.5, 0.5,
    0.5, 1, 1, -2, -2, 1, 1, 0.5,
    0, 0, 0, 0, 0, 0, 0, 0
]

KNIGHT_WEIGHTS = [
    -5, -4, -3, -3, -3, -3, -4, -5,
    -4, -2, 0, 0.5, 0.5, 0, -2, -4,
    -3, 0, 1, 2, 2, 1, 0, -3,
    -3, 0.5, 2, 3, 3, 2, 0.5, -3,
    -3, 0, 2, 3, 3, 2, 0, -3,
    -3, 0.5, 1, 2, 2, 1, 0.5, -3,
    -4, -2, 0, 0.5, 0.5, 0, -2, -4,
    -5, -4, -3, -3, -3, -3, -4, -5
]

BISHOP_WEIGHTS = [
    -2, -1, -1, -1, -1, -1, -1, -2,
    -1, 0, 0, 0, 0, 0, 0, -1,
    -1, 0, 0.5, 1, 1, 0.5, 0, -1,
    -1, 0.5, 0.5, 1, 1, 0.5, 0.5, -1,
    -1, 0, 1, 1, 1, 1, 0, -1,
    -1, 1, 1, 1, 1, 1, 1, -1,
    -1, 0.5, 0, 0, 0, 0, 0.5, -1,
    -2, -1, -1, -1, -1, -1, -1, -2
]

QUEEN_WEIGHTS = [
    -2, -1, -1, -0.5, -0.5, -1, -1, -2,
    -1, 0, 0, 0, 0, 0, 0, -1,
    -1, 0, 0.5, 0.5, 0.5, 0.5, 0, -1,
    -0.5, 0, 0.5, 0.5, 0.5, 0.5, 0, -0.5,
    0, 0, 0.5, 0.5, 0.5, 0.5, 0, -1,
    -1, 0.5, 0.5, 0.5, 0.5, 0.5, 0, -1,
    -1, 0, 0.5, 0, 0, 0, 0, -1,
    -2, -1, -1, -0.5, -0.5, -1, -1, -2
]

KING_EARLY_WEIGHTS = [
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    1, 0, 0, 0, 0, 0, 0, 1,
    2, 1, 0, 0, 0, 0, 1, 2,
    3, 4, 1, 1, 1, 1, 4, 3
]

KING_ENDGAME_WEIGHTS = [
    -5, -4, -3, -2, -2, -3, -4, -5,
    -3, -2, -1, 0, 0, -1, -2, -3,
    -3, -1, 2, 3, 3, 2, -1, -3,
    -3, -1, 3, 5, 5, 3, -1, -3,
    -3, -1, 3, 5, 5, 3, -1, -3,
    -3, -1, 2, 3, 3, 2, -1, -3,
    -3, -3, 0, 0, 0, 0, -3, -3,
    -5, -3, -3, -3, -3, -3, -3, -5
]

is_opening_theory = True
current_line = openings_dictionary.openings

def make_move(board):
    move = None

    if is_opening_theory:
        move = get_book_move(board)
    
    if move is None:
        start_time = time.perf_counter()
        depth = 4
        transposition_table = [{}] * (depth + 1)
        evaluation, move = search(board, depth, -1_000_000_000, 1_000_000_000, transposition_table)
        if time.perf_counter() - start_time < 0.5:
            depth = 6
            transposition_table = [{}] * (depth + 1)
            evaluation, move = search(board, depth, -1_000_000_000, 1_000_000_000, transposition_table)
            if time.perf_counter() - start_time < 2:
                depth = 8
                transposition_table = [{}] * (depth + 1)
                evaluation, move = search(board, depth, -1_000_000_000, 1_000_000_000, transposition_table)
        print(f"Depth: {depth}, Eval: {evaluation}")
    
    board.make_move(move)
    board.moves.append(move)

def get_book_move(board):
    global is_opening_theory
    global current_line

    if len(board.moves) > 0:
        previous_move_square = move_to_square(board.moves[-1], board)
        if previous_move_square not in current_line:
            is_opening_theory = False
            return None
        current_line = current_line[previous_move_square]
        if len(current_line) == 0:
            is_opening_theory = False
            return None
        end_square = random.choice(list(current_line.keys()))
        current_line = current_line[end_square]
    else:
        end_square = random.choices(list(current_line.keys()), weights=[3, 1], k=1)[0]
        current_line = current_line[end_square]

    return square_to_move(end_square, board)

def search(board, depth, alpha, beta, transposition_table):
    #if board.zobrist_key in transposition_table[depth]:
    #    return transposition_table[depth][board.zobrist_key][0], transposition_table[depth][board.zobrist_key][1]

    if depth == 0:
        return search_captures(board, alpha, beta, transposition_table)

    legal_moves = board.get_legal_moves()

    if len(legal_moves) == 0:
        if board.white_in_check or board.black_in_check:
            return -1_000_000_000 * depth, None
        else:
            return 0, None

    legal_moves.sort(key=lambda move: -move.capture_value)

    best_move = legal_moves[0]

    for move in legal_moves:
        board.make_move(move)
        move_evaluation, _ = search(board, depth-1, -beta, -alpha, transposition_table)
        move_evaluation *= -1
        board.undo_move(move)
        if move_evaluation >= beta:
            return beta, move
        if move_evaluation > alpha:
            best_move = move
            alpha = move_evaluation
            if board.zobrist_key in transposition_table[depth] and transposition_table[depth][board.zobrist_key][0] != move_evaluation:
                print("TT Error")
    
    transposition_table[depth][board.zobrist_key] = (alpha, best_move)
    
    return alpha, best_move

def search_captures(board, alpha, beta, transposition_table):
    evaluation = evaluate(board)
    if (evaluation >= beta):
        return beta, None
    alpha = max(alpha, evaluation)

    legal_moves = board.get_legal_moves()

    if len(legal_moves) == 0:
        if board.white_in_check or board.black_in_check:
            return -1_000_000_000, None
        else:
            return 0, None
    
    legal_captures = [move for move in legal_moves if move.is_capture]

    if len(legal_captures) == 0:
        return alpha, None
    
    legal_captures.sort(key=lambda move: -move.capture_value)

    best_move = legal_moves[0]

    for move in legal_captures:
        board.make_move(move)
        move_evaluation, _ = search_captures(board, -beta, -alpha, transposition_table)
        move_evaluation *= -1
        board.undo_move(move)
        if move_evaluation >= beta:
            return beta, move
        if move_evaluation > alpha:
            best_move = move
            alpha = move_evaluation
    
    return alpha, best_move

def evaluate(board):
    evaluation = 0

    evaluation += PAWN_VALUE * (bin(board.white_pieces & board.pawns).count('1') - bin(board.black_pieces & board.pawns).count('1'))
    evaluation += KNIGHT_VALUE * (bin(board.white_pieces & board.knights).count('1') - bin(board.black_pieces & board.knights).count('1'))
    evaluation += BISHOP_VALUE * (bin(board.white_pieces & board.bishops).count('1') - bin(board.black_pieces & board.bishops).count('1'))
    evaluation += ROOK_VALUE * (bin(board.white_pieces & board.rooks).count('1') - bin(board.black_pieces & board.rooks).count('1'))
    evaluation += QUEEN_VALUE * (bin(board.white_pieces & board.queens).count('1') - bin(board.black_pieces & board.queens).count('1'))

    for i in range(64):
        bitboard_position = 2**i
        if not board.is_piece(bitboard_position):
            continue
        if board.is_white(bitboard_position):
            if board.is_pawn(bitboard_position):
                evaluation += PAWN_WEIGHTS[i] * 10
            elif board.is_knight(bitboard_position):
                evaluation += KNIGHT_WEIGHTS[i] * 10
            elif board.is_bishop(bitboard_position):
                evaluation += BISHOP_WEIGHTS[i] * 10
            elif board.is_queen(bitboard_position):
                evaluation += QUEEN_WEIGHTS[i] * 10
            elif board.is_king(bitboard_position):
                if len([j for j in board.bitboard_to_bitboard_positions(board.black_pieces & (board.knights | board.bishops | board.rooks | board.queens))]) > 3:
                    evaluation += KING_EARLY_WEIGHTS[i] * 20
                else:
                    evaluation += KING_ENDGAME_WEIGHTS[i] * 10
        else:
            if board.is_pawn(bitboard_position):
                evaluation -= PAWN_WEIGHTS[63-i] * 10
            elif board.is_knight(bitboard_position):
                evaluation -= KNIGHT_WEIGHTS[i] * 10
            elif board.is_bishop(bitboard_position):
                evaluation -= BISHOP_WEIGHTS[63-i] * 10
            elif board.is_queen(bitboard_position):
                evaluation -= QUEEN_WEIGHTS[i] * 10
            elif board.is_king(bitboard_position):
                if len([j for j in board.bitboard_to_bitboard_positions(board.white_pieces & (board.knights | board.bishops | board.rooks | board.queens))]) > 3:
                    evaluation += KING_EARLY_WEIGHTS[63-i] * 20
                else:
                    evaluation += KING_ENDGAME_WEIGHTS[63-i] * 10

    if not board.white_move: evaluation *= -1

    return evaluation

def bitboard_position_to_human_position(bitboard_position):
    index_position = int(math.log2(bitboard_position))
    file = 'abcdefgh'[index_position % 8]
    rank = str((63 - index_position) // 8 + 1)
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
    end_square = bitboard_position_to_human_position(move.end_bitboard_position)
    piece_type = board.get_piece_type(move.end_bitboard_position)
    capture_info = ''
    if move.is_capture:
        if board.is_pawn(move.end_bitboard_position):
            capture_info += bitboard_position_to_human_position(move.start_bitboard_position)[0]
        capture_info += 'x'
    return get_piece_letter(piece_type) + capture_info + end_square

def square_to_move(square, board):
    end_bitboard_position = human_position_to_bitboard_position(square[-2] + square[-1])
    legal_moves = board.get_legal_moves()
    for move in legal_moves:
        if move.end_bitboard_position == end_bitboard_position:
            piece_letter = get_piece_letter(board.get_piece_type(move.start_bitboard_position))
            if len(square) == 2 and piece_letter == '':
                return move
            if square[0] == piece_letter:
                return move
            
    return None
            