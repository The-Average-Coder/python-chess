from Chess import pieces

class Move:
    def __init__(self, start_bitboard_position, end_bitboard_position, board, promotion=0b000):
        self.start_bitboard_position = start_bitboard_position
        self.end_bitboard_position = end_bitboard_position

        self.move_data = 0
        if board.is_white(start_bitboard_position):
            self.move_data |= 0b100000000000

        self.move_data |= board.check_capture(end_bitboard_position) << 6

        if board.check_kingside_castle(start_bitboard_position, end_bitboard_position):
            self.move_data |= 0b100000
        elif board.check_queenside_castle(start_bitboard_position, end_bitboard_position):
            self.move_data |= 0b10000
        elif board.check_en_passant(start_bitboard_position, end_bitboard_position):
            self.move_data |= 0b1
        else:
            self.move_data |= promotion << 1
        
        self.previous_castling_rules = board.castling_rules
        self.previous_en_passant_target = board.en_passant_target
    
    @property
    def is_white_move(self):
        return self.move_data & 0b100000000000 > 0
    
    @property
    def is_capture(self):
        return self.move_data & 0b1111000000 > 0
    
    @property
    def captured_white(self):
        return self.move_data & pieces.WHITE << 6 > 0
    
    @property
    def captured_pawn(self):
        return self.move_data & 0b000111000000 == pieces.PAWN << 6
    
    @property
    def captured_knight(self):
        return self.move_data & 0b000111000000 == pieces.KNIGHT << 6
    
    @property
    def captured_bishop(self):
        return self.move_data & 0b000111000000 == pieces.BISHOP << 6
    
    @property
    def captured_rook(self):
        return self.move_data & 0b000111000000 == pieces.ROOK << 6
    
    @property
    def captured_queen(self):
        return self.move_data & 0b000111000000 == pieces.QUEEN << 6
    
    @property
    def captured_king(self):
        return self.move_data & 0b000111000000 == pieces.KING << 6
    
    @property
    def capture_value(self):
        if self.captured_pawn:
            return 100
        if self.captured_knight:
            return 300
        if self.captured_bishop:
            return 330
        if self.captured_rook:
            return 500
        if self.captured_queen:
            return 900
        return 0
    
    @property
    def is_kingside_castle(self):
        return self.move_data & 0b100000 > 0
    
    @property
    def is_queenside_castle(self):
        return self.move_data & 0b10000 > 0
    
    @property
    def is_promotion(self):
        return self.move_data & 0b1110 > 0
    
    @property
    def is_promotion_to_knight(self):
        return self.move_data & 0b1110 == 0b10
    
    @property
    def is_promotion_to_bishop(self):
        return self.move_data & 0b1110 == 0b100
    
    @property
    def is_promotion_to_rook(self):
        return self.move_data & 0b1110 == 0b110
    
    @property
    def is_promotion_to_queen(self):
        return self.move_data & 0b1110 == 0b1000
    
    @property
    def is_en_passant(self):
        return self.move_data & 0b1 > 0