import time, math

from Chess.Board.board import Board
from Chess.Board.move_generator import MoveGenerator
from Chess.AI import chess_bot

board = Board()
move_generator = MoveGenerator(board)

start_time = time.perf_counter()
for _ in range(10_000):
    move_generator.get_legal_moves()
print(f"Move Generation Test: {time.perf_counter() - start_time}")

test_move = move_generator.get_legal_moves()[0]

start_time = time.perf_counter()
for _ in range(10_000):
    board.make_move(test_move)
    board.undo_move(test_move)
print(f"Move Making Test: {time.perf_counter() - start_time}")

start_time = time.perf_counter()
for _ in range(10_000):
    chess_bot.evaluate(board)
print(f"Evaluation Test: {time.perf_counter() - start_time}")
