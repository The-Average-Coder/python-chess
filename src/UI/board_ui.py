import pygame

CHESS_BOARD_POSITION = (400, 50)

chess_board = pygame.image.load("./src/UI/images/chess_board.png")

white_pawn = pygame.image.load("./src/UI/images/white_pawn.png")
white_knight = pygame.image.load("./src/UI/images/white_knight.png")
white_bishop = pygame.image.load("./src/UI/images/white_bishop.png")
white_rook = pygame.image.load("./src/UI/images/white_rook.png")
white_queen = pygame.image.load("./src/UI/images/white_queen.png")
white_king = pygame.image.load("./src/UI/images/white_king.png")

black_pawn = pygame.image.load("./src/UI/images/black_pawn.png")
black_knight = pygame.image.load("./src/UI/images/black_knight.png")
black_bishop = pygame.image.load("./src/UI/images/black_bishop.png")
black_rook = pygame.image.load("./src/UI/images/black_rook.png")
black_queen = pygame.image.load("./src/UI/images/black_queen.png")
black_king = pygame.image.load("./src/UI/images/black_king.png")

def render(screen, board):
    screen.blit(chess_board, CHESS_BOARD_POSITION)

    for position in range(64):
        render_position = (CHESS_BOARD_POSITION[0] + 100 * (position % 8), CHESS_BOARD_POSITION[1] + 100 * (position // 8))
        piece_image = get_piece_image(position, board)

        if not piece_image: continue

        screen.blit(piece_image, render_position)

def get_piece_image(position, board):
    bitboard_position = board.get_bitboard_position_from_index(position)
    
    if board.is_white(bitboard_position):
        if board.is_pawn(bitboard_position): return white_pawn
        if board.is_knight(bitboard_position): return white_knight
        if board.is_bishop(bitboard_position): return white_bishop
        if board.is_rook(bitboard_position): return white_rook
        if board.is_queen(bitboard_position): return white_queen
        if board.is_king(bitboard_position): return white_king
    else:
        if board.is_pawn(bitboard_position): return black_pawn
        if board.is_knight(bitboard_position): return black_knight
        if board.is_bishop(bitboard_position): return black_bishop
        if board.is_rook(bitboard_position): return black_rook
        if board.is_queen(bitboard_position): return black_queen
        if board.is_king(bitboard_position): return black_king