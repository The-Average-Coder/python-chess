import time, math

from Chess.board import Board

def search(board: Board, depth):

    legal_moves = board.get_legal_moves()

    if depth == 1:
        return len(legal_moves)

    num_positions = 0

    for move in legal_moves:
        #print(f"Depth: {depth} Move: {bitboard_position_to_human_position(move.start_bitboard_position)}{bitboard_position_to_human_position(move.end_bitboard_position)}")
        board.make_move(move)
        new_positions = search(board, depth-1)
        num_positions += new_positions
        #if depth == 2:
        #    print(f"{bitboard_position_to_human_position(move.start_bitboard_position)}{bitboard_position_to_human_position(move.end_bitboard_position)}: {new_positions}")
        board.undo_move(move)
    
    return num_positions

def bitboard_position_to_human_position(bitboard_position):
    index_position = int(math.log2(bitboard_position))
    file = 'abcdefgh'[index_position % 8]
    rank = str((63 - index_position) // 8 + 1)
    return file + rank

def run_perft_test(FEN, depth, expected_num_positions_list):
    board = Board(FEN)
    for i in range(0, depth):
        start_time = time.perf_counter()
        num_positions = search(board, i+1)
        time_elapsed = time.perf_counter() - start_time
        print(f"Depth: {i+1}   Result: {num_positions}   Expected Result: {expected_num_positions_list[i]}   Time: {time_elapsed}")

def run_perft_tests():
    print("-------------------------------- Test 1 --------------------------------")
    run_perft_test('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1 ', 4, [20, 400, 8902, 197281, 4865609])
    print("-------------------------------- Test 2 --------------------------------")
    run_perft_test('rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8 ', 4, [44, 1486, 62379, 2103487, 89941194])
    print("-------------------------------- Test 3 --------------------------------")
    run_perft_test('r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10 ', 4, [46, 2079, 89890, 3894594, 164075551])

if __name__ == "__main__":
    run_perft_tests()