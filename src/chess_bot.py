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

def make_move(board, depth):
    _, move = search(board, depth, -1_000_000_000, 1_000_000_000)
    board.make_move(move)
    board.moves.append(move)

def search(board, depth, alpha, beta):
    if depth == 0:
        return search_captures(board, alpha, beta)

    legal_moves = board.get_legal_moves()

    if len(legal_moves) == 0:
        if board.white_in_check and board.white_move or board.black_in_check and not board.white_move:
            return -1_000_000_000, None
        else:
            return 0, None

    legal_moves.sort(key=lambda move: -move.capture_value)

    best_move = legal_moves[0]

    for move in legal_moves:
        board.make_move(move)
        move_evaluation, _ = search(board, depth-1, -beta, -alpha)
        move_evaluation *= -1
        board.undo_move(move)
        if move_evaluation >= beta:
            return beta, move
        if move_evaluation > alpha:
            best_move = move
            alpha = move_evaluation
    
    return alpha, best_move

def search_captures(board, alpha, beta):
    evaluation = evaluate(board)
    if (evaluation >= beta):
        return beta, None
    alpha = max(alpha, evaluation)

    legal_moves = board.get_legal_moves()

    if len(legal_moves) == 0:
        if board.white_in_check and board.white_move or board.black_in_check and not board.white_move:
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
        move_evaluation, _ = search_captures(board, -beta, -alpha)
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
                if len([i for i in board.bitboard_to_bitboard_positions(board.black_pieces & (board.knights | board.bishops | board.rooks | board.queens))]) > 3:
                    evaluation += KING_EARLY_WEIGHTS[i] * 10
                else:
                    evaluation += KING_ENDGAME_WEIGHTS[i] * 10
        else:
            if board.is_pawn(bitboard_position):
                evaluation -= PAWN_WEIGHTS[63-i] * 10
            elif board.is_knight(bitboard_position):
                evaluation -= KNIGHT_WEIGHTS[i] * 10
            elif board.is_bishop(bitboard_position):
                evaluation -= BISHOP_WEIGHTS[i] * 10
            elif board.is_queen(bitboard_position):
                evaluation -= QUEEN_WEIGHTS[i] * 10
            elif board.is_king(bitboard_position):
                if len([i for i in board.bitboard_to_bitboard_positions(board.white_pieces & (board.knights | board.bishops | board.rooks | board.queens))]) > 3:
                    evaluation += KING_EARLY_WEIGHTS[63-i] * 10
                else:
                    evaluation += KING_ENDGAME_WEIGHTS[63-i] * 10

    if not board.white_move: evaluation *= -1

    return evaluation
