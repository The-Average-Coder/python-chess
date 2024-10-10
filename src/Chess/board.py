import string

STARTING_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

class Board:
    def __init__(self, FEN = STARTING_FEN):
        self.setup_board(FEN)
    
    def setup_board(self, FEN):
        if not self.fen_is_valid(FEN):
            self.white_pieces = 0
            self.black_pieces = 0
            self.pawns = 0
            self.knights = 0
            self.bishops = 0
            self.rooks = 0
            self.queens = 0
            self.kings = 0
            return
        
        board_data, color_data, castling_data, en_passant_target_data, half_moves, full_moves = FEN.split()

        # Remove slashes and turn numbers into n number of 0s for easier use
        parsed_board_string = ''.join([piece if piece in string.ascii_letters else '0' * int(piece) if piece.isdigit() else '' for piece in board_data])
        
        self.white_pieces = sum([2**position for position, piece in enumerate(parsed_board_string) if piece in string.ascii_uppercase])
        self.black_pieces = sum([2**position for position, piece in enumerate(parsed_board_string) if piece in string.ascii_lowercase])

        self.pawns = sum([2**position for position, piece in enumerate(parsed_board_string) if piece.lower() == 'p'])
        self.knights = sum([2**position for position, piece in enumerate(parsed_board_string) if piece.lower() == 'n'])
        self.bishops = sum([2**position for position, piece in enumerate(parsed_board_string) if piece.lower() == 'b'])
        self.rooks = sum([2**position for position, piece in enumerate(parsed_board_string) if piece.lower() == 'r'])
        self.queens = sum([2**position for position, piece in enumerate(parsed_board_string) if piece.lower() == 'q'])
        self.kings = sum([2**position for position, piece in enumerate(parsed_board_string) if piece.lower() == 'k'])

        # Data such as who's move it is, who is in check, who can castle where
        # and whether an en passant is available is stored in 1 byte
        self.game_data = 0
        self.en_passant_target = 0

        if color_data == 'w':
            self.game_data += 2**8

        # Check whether anyone is in check, bits 6 and 7

        if 'K' in castling_data:
            self.game_data += 2**5
        if 'Q' in castling_data:
            self.game_data += 2**4
        if 'k' in castling_data:
            self.game_data += 2**3
        if 'q' in castling_data:
            self.game_data += 2**2
        
        if en_passant_target_data != '-':
            self.game_data += 2**1
            self.en_passant_target = self.get_bitboard_position_from_square(en_passant_target_data)
        
        self.half_moves = int(half_moves)
        self.full_moves = int(full_moves)

    def fen_is_valid(self, FEN):
        return True
    
    def get_bitboard_position_from_index(self, index: int):
        return 2**index

    @property
    def white_move(self):
        return self.game_data & 2**8
    
    @white_move.setter
    def white_move(self, value):
        if value and not self.game_data & 2**8:
            self.game_data += 2**8
        elif not value and self.game_data & 2**8:
            self.game_data -= 2**8

    def is_white(self, bitboard_position):
        return self.white_pieces & bitboard_position
    def is_black(self, bitboard_position):
        return self.black_pieces & bitboard_position
    
    def is_pawn(self, bitboard_position):
        return self.pawns & bitboard_position
    def is_knight(self, bitboard_position):
        return self.knights & bitboard_position
    def is_bishop(self, bitboard_position):
        return self.bishops & bitboard_position
    def is_rook(self, bitboard_position):
        return self.rooks & bitboard_position
    def is_queen(self, bitboard_position):
        return self.queens & bitboard_position
    def is_king(self, bitboard_position):
        return self.kings & bitboard_position
    
    def make_move(self, start_bitboard_position, end_bitboard_position):
        if self.is_capture(end_bitboard_position):
            self.capture_piece(end_bitboard_position)

        self.update_piece_position(start_bitboard_position, end_bitboard_position)
    
        self.white_move = not self.white_move

    def update_piece_position(self, start_bitboard_position, end_bitboard_position):
        position_change = end_bitboard_position - start_bitboard_position

        if self.white_move: self.white_pieces += position_change
        else: self.black_pieces += end_bitboard_position - start_bitboard_position
        
        if self.pawns & start_bitboard_position: self.pawns += position_change
        elif self.knights & start_bitboard_position: self.knights += position_change
        elif self.bishops & start_bitboard_position: self.bishops += position_change
        elif self.rooks & start_bitboard_position: self.rooks += position_change
        elif self.queens & start_bitboard_position: self.queens += position_change
        elif self.kings & start_bitboard_position: self.kings += position_change
    
    def is_capture(self, end_bitboard_position):
        return end_bitboard_position & (self.black_pieces if self.white_move else self.white_pieces)
    
    def capture_piece(self, bitboard_position):
        if self.white_move: self.black_pieces -= bitboard_position
        else: self.white_pieces -= bitboard_position
        
        if self.pawns & bitboard_position: self.pawns -= bitboard_position
        elif self.knights & bitboard_position: self.knights -= bitboard_position
        elif self.bishops & bitboard_position: self.bishops -= bitboard_position
        elif self.rooks & bitboard_position: self.rooks -= bitboard_position
        elif self.queens & bitboard_position: self.queens -= bitboard_position
        elif self.kings & bitboard_position: self.kings -= bitboard_position