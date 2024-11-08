import pygame

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

move_overlay = pygame.image.load("./src/UI/images/move_overlay.png")
previous_move_overlay = pygame.image.load("./src/UI/images/previous_move_overlay.png")

class BoardUI():
    def __init__(self, position):
        self.chess_board_position = position
        self.selected_piece = -1
    
    def render(self, screen, board):
        screen.blit(chess_board, self.chess_board_position)

        last_move = board.moves[-1] if len(board.moves) > 0 else None

        for position in range(64):
            if last_move:
                if 2**position & (last_move.start_bitboard_position | last_move.end_bitboard_position):
                    screen.blit(previous_move_overlay, self.get_screen_position_from_square(position))

            # Piece being dragged is rendered on top of other pieces
            if position == self.selected_piece:
                continue

            if self.selected_piece >= 0:
                for move in self.legal_moves:
                    if move.end_bitboard_position == board.get_bitboard_position_from_index(position):
                        screen.blit(move_overlay, self.get_screen_position_from_square(position))
                        break

            piece_image = get_piece_image(position, board)

            if not piece_image: continue
                
            render_position = self.get_screen_position_from_square(position)

            screen.blit(piece_image, render_position)
        
        if self.selected_piece != -1:
            piece_image = get_piece_image(self.selected_piece, board)
            render_position = pygame.mouse.get_pos() - pygame.Vector2(50, 50)
            
            screen.blit(piece_image, render_position)
    
    # Check if a position on the window is a square on the board
    def get_square_from_screen_position(self, position):
        if position[0] < self.chess_board_position[0] or position[0] > self.chess_board_position[0] + 800:
            return -1
        if position[1] < self.chess_board_position[1] or position[1] > self.chess_board_position[1] + 800:
            return -1
        
        square_x = (position[0] - self.chess_board_position[0]) // 100
        square_y = (position[1] - self.chess_board_position[1]) // 100

        return square_y * 8 + square_x
    
    def get_screen_position_from_square(self, position):
        screen_x = self.chess_board_position[0] + 100 * (position % 8)
        screen_y = self.chess_board_position[1] + 100 * (position // 8)

        return (screen_x, screen_y)
    
    def set_selected_piece(self, square, board):
        self.selected_piece = square
        if square == -1:
            self.legal_moves = []
            return
        self.legal_moves = board.get_piece_legal_moves(self.selected_piece, board.get_bitboard_position_from_index(self.selected_piece))

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