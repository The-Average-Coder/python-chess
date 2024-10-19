PAWN_VALUE = 100
KNIGHT_VALUE = 300
BISHOP_VALUE = 300
ROOK_VALUE = 500
QUEEN_VALUE = 900

def make_move(board, depth):
    _, move = search(board, depth)
    board.make_move(move)
    board.moves.append(move)

def search(board, depth):
    if depth == 0:
        return evaluate(board), None

    legal_moves = board.get_legal_moves()

    if len(legal_moves) == 0:
        if board.white_in_check and board.white_move or board.black_in_check and not board.white_move:
            return -1_000_000_000, None
        else:
            return 0, None

    best_move = None
    best_evaluation = -1_000_000_000_000

    for move in legal_moves:
        board.make_move(move)
        move_evaluation, _ = search(board, depth-1)
        move_evaluation *= -1
        if move_evaluation > best_evaluation:
            best_move = move
            best_evaluation = move_evaluation
        board.undo_move(move)
    
    return best_evaluation, best_move

def evaluate(board):
    evaluation = 0

    evaluation += PAWN_VALUE * (bin(board.white_pieces & board.pawns).count('1') - bin(board.black_pieces & board.pawns).count('1'))
    evaluation += KNIGHT_VALUE * (bin(board.white_pieces & board.knights).count('1') - bin(board.black_pieces & board.knights).count('1'))
    evaluation += BISHOP_VALUE * (bin(board.white_pieces & board.bishops).count('1') - bin(board.black_pieces & board.bishops).count('1'))
    evaluation += ROOK_VALUE * (bin(board.white_pieces & board.rooks).count('1') - bin(board.black_pieces & board.rooks).count('1'))
    evaluation += QUEEN_VALUE * (bin(board.white_pieces & board.queens).count('1') - bin(board.black_pieces & board.queens).count('1'))

    if not board.white_move: evaluation *= -1

    return evaluation
