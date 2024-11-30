import string, math, random

from Chess.Board import pieces
from Chess.Board.move import Move 
from Chess.Board.pre_computed_data import DISTANCE_TO_EDGE, KNIGHT_MOVES, KING_MOVES

STARTING_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
#STARTING_FEN = 'rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8'
#STARTING_FEN = 'r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10 '

#STARTING_FEN = '6QR/8/3p1kN1/1P5P/3N1r2/1b4P1/3r4/2K2b2 b - - 13 10'
#STARTING_FEN = '4k3/5ppp/4p3/1p6/8/PP5P/4KPP1/8 w - - 0 1'

#STARTING_FEN = 'rnbqkbnr/ppp1pppp/5n2/3P4/3P4/8/PPP2PPP/RNBQKBNR b KQkq - 0 1'

SLIDING_PIECE_DIRECTION_OFFSETS = [ 1, -1, 8, -8, 7, -7, 9, -9 ]

class Board:
    def __init__(self, FEN = STARTING_FEN):
        self.setup_board(FEN)

    # -------------------------------- SETUP + REPRESENTATION --------------------------------

    def setup_board(self, FEN):
        if not self.fen_is_valid(FEN):
            return
        
        board_data, color_data, castling_data, en_passant_target_data, half_moves, full_moves = FEN.split()

        # Remove slashes and turn numbers into n number of 0s for easier use
        parsed_board_string = ''.join([piece if piece in string.ascii_letters else '0' * int(piece) if piece.isdigit() else '' for piece in board_data])
        
        self.pieces = {}

        self.pieces[pieces.WHITE] = sum([2**position for position, piece in enumerate(parsed_board_string) if piece in string.ascii_uppercase])
        self.pieces[pieces.BLACK] = sum([2**position for position, piece in enumerate(parsed_board_string) if piece in string.ascii_lowercase])

        self.pieces[pieces.PAWN] = sum([2**position for position, piece in enumerate(parsed_board_string) if piece.lower() == 'p'])
        self.pieces[pieces.KNIGHT] = sum([2**position for position, piece in enumerate(parsed_board_string) if piece.lower() == 'n'])
        self.pieces[pieces.BISHOP] = sum([2**position for position, piece in enumerate(parsed_board_string) if piece.lower() == 'b'])
        self.pieces[pieces.ROOK] = sum([2**position for position, piece in enumerate(parsed_board_string) if piece.lower() == 'r'])
        self.pieces[pieces.QUEEN] = sum([2**position for position, piece in enumerate(parsed_board_string) if piece.lower() == 'q'])
        self.pieces[pieces.KING] = sum([2**position for position, piece in enumerate(parsed_board_string) if piece.lower() == 'k'])

        # Data such as who's move it is, who is in check, who can castle where
        # and whether an en passant is available is stored in 1 byte
        self.game_data = 0
        self.en_passant_target = 0

        if color_data == 'w':
            self.game_data += 0b10000000

        # Check whether anyone is in check, bits 6 and 7

        if 'K' in castling_data:
            self.game_data += 0b10000
        if 'Q' in castling_data:
            self.game_data += 0b1000
        if 'k' in castling_data:
            self.game_data += 0b100
        if 'q' in castling_data:
            self.game_data += 0b10
        
        if en_passant_target_data != '-':
            self.game_data += 0b1
            self.en_passant_target = self.get_bitboard_position_from_square(en_passant_target_data)

        self.half_moves = int(half_moves)
        self.full_moves = int(full_moves)

        self.moves = []
        self.previous_positions = []

        self.generate_attack_tables()
        self.generate_zobrist_key()

    def fen_is_valid(self, FEN):
        return True

    def generate_zobrist_key(self):
        # Generate Pseudorandom Numbers

        self.zobrist_piece_numbers = [None] * 33
        for piece in range(1, 7):
            self.zobrist_piece_numbers[pieces.WHITE | piece] = [random.randrange(2**64) for _ in range(64)]
            self.zobrist_piece_numbers[pieces.BLACK | piece] = [random.randrange(2**64) for _ in range(64)]
        
        self.zobrist_castling_numbers = [random.randrange(2**64) for _ in range(4)]
        self.zobrist_en_passant_numbers = [random.randrange(2**64) for _ in range(8)]
        self.zobrist_white_to_move_number = random.randrange(2**64)

        self.zobrist_key = 0

        for piece in self.bitboard_to_bitboard_positions(self.pieces[pieces.WHITE]):
            if self.is_pawn(piece[1]): self.zobrist_key ^= self.zobrist_piece_numbers[pieces.WHITE | pieces.PAWN][piece[0]]
            if self.is_knight(piece[1]): self.zobrist_key ^= self.zobrist_piece_numbers[pieces.WHITE | pieces.KNIGHT][piece[0]]
            if self.is_bishop(piece[1]): self.zobrist_key ^= self.zobrist_piece_numbers[pieces.WHITE | pieces.BISHOP][piece[0]]
            if self.is_rook(piece[1]): self.zobrist_key ^= self.zobrist_piece_numbers[pieces.WHITE | pieces.ROOK][piece[0]]
            if self.is_queen(piece[1]): self.zobrist_key ^= self.zobrist_piece_numbers[pieces.WHITE | pieces.QUEEN][piece[0]]
            if self.is_king(piece[1]): self.zobrist_key ^= self.zobrist_piece_numbers[pieces.WHITE | pieces.KING][piece[0]]
        for piece in self.bitboard_to_bitboard_positions(self.pieces[pieces.BLACK]):
            if self.is_pawn(piece[1]): self.zobrist_key ^= self.zobrist_piece_numbers[pieces.BLACK | pieces.PAWN][piece[0]]
            if self.is_knight(piece[1]): self.zobrist_key ^= self.zobrist_piece_numbers[pieces.BLACK | pieces.KNIGHT][piece[0]]
            if self.is_bishop(piece[1]): self.zobrist_key ^= self.zobrist_piece_numbers[pieces.BLACK | pieces.BISHOP][piece[0]]
            if self.is_rook(piece[1]): self.zobrist_key ^= self.zobrist_piece_numbers[pieces.BLACK | pieces.ROOK][piece[0]]
            if self.is_queen(piece[1]): self.zobrist_key ^= self.zobrist_piece_numbers[pieces.BLACK | pieces.QUEEN][piece[0]]
            if self.is_king(piece[1]): self.zobrist_key ^= self.zobrist_piece_numbers[pieces.BLACK | pieces.KING][piece[0]]
        
        if self.white_can_kingside_castle: self.zobrist_key ^= self.zobrist_castling_numbers[0]
        if self.white_can_queenside_castle: self.zobrist_key ^= self.zobrist_castling_numbers[1]
        if self.black_can_kingside_castle: self.zobrist_key ^= self.zobrist_castling_numbers[2]
        if self.black_can_queenside_castle: self.zobrist_key ^= self.zobrist_castling_numbers[3]

        if self.is_en_passant_target:
            self.zobrist_key ^= self.zobrist_en_passant_numbers[math.log2(self.en_passant_target) % 8]
        
        if self.white_to_move:
            self.zobrist_key ^= self.zobrist_white_to_move_number

    # -------------------------------- MOVE MAKING / UNDOING --------------------------------

    def make_move(self, move):
        start_bitboard_position = 2**move.start_position
        end_bitboard_position = 2**move.end_position

        if move.is_capture:
            self.capture_piece(end_bitboard_position)
        
        elif move.is_en_passant:
            if move.is_white_to_move:
                self.capture_piece(end_bitboard_position << 8)
            else:
                self.capture_piece(end_bitboard_position >> 8)

        self.is_en_passant_target = False
        self.en_passant_target = 0

        # Check if pawn double move to add as en passant target
        if self.is_pawn(start_bitboard_position) and (start_bitboard_position << 16 == end_bitboard_position or start_bitboard_position >> 16 == end_bitboard_position):
            self.is_en_passant_target = True
                
            if move.is_white_to_move:
                self.en_passant_target = start_bitboard_position >> 8
            else:
                self.en_passant_target = start_bitboard_position << 8

        # Check if king to disallow castling
        elif start_bitboard_position == 0b1000000000000000000000000000000000000000000000000000000000000:
            self.white_can_kingside_castle = False
            self.white_can_queenside_castle = False
        elif start_bitboard_position == 0b10000:
            self.black_can_kingside_castle = False
            self.black_can_queenside_castle = False
        
        # Check if rook to disallow castling
        elif (start_bitboard_position | end_bitboard_position) & 0b1000000000000000000000000000000000000000000000000000000000000000 > 0:
            self.white_can_kingside_castle = False
        elif (start_bitboard_position | end_bitboard_position) & 0b100000000000000000000000000000000000000000000000000000000 > 0:
            self.white_can_queenside_castle = False
        elif (start_bitboard_position | end_bitboard_position) & 0b10000000 > 0:
            self.black_can_kingside_castle = False
        elif (start_bitboard_position | end_bitboard_position) & 0b1 > 0:
            self.black_can_queenside_castle = False

        self.update_piece_position(start_bitboard_position, end_bitboard_position)

        if move.is_promotion:
            self.pieces[pieces.PAWN] -= end_bitboard_position
            if move.is_promotion_to_knight:
                self.pieces[pieces.KNIGHT] |= end_bitboard_position
            elif move.is_promotion_to_bishop:
                self.pieces[pieces.BISHOP] |= end_bitboard_position
            elif move.is_promotion_to_rook:
                self.pieces[pieces.ROOK] |= end_bitboard_position
            elif move.is_promotion_to_queen:
                self.pieces[pieces.QUEEN] |= end_bitboard_position

        if move.is_kingside_castle:
            if move.is_white_to_move:
                self.update_piece_position(2**63, 2**61)
            else:
                self.update_piece_position(2**7, 2**5)
        elif move.is_queenside_castle:
            if move.is_white_to_move:
                self.update_piece_position(2**56, 2**59)
            else:
                self.update_piece_position(0b1, 0b1000)

        self.update_attack_tables(move, start_bitboard_position, end_bitboard_position)
        self.update_zobrist_key(move, end_bitboard_position)

        self.previous_positions.append(self.zobrist_key)

        self.white_to_move = not self.white_to_move
    
    def undo_move(self, move):
        start_bitboard_position = 2**move.start_position
        end_bitboard_position = 2**move.end_position

        self.update_zobrist_key(move, end_bitboard_position)

        if move.is_promotion:
            if move.is_promotion_to_knight:
                self.pieces[pieces.KNIGHT] -= end_bitboard_position
            elif move.is_promotion_to_bishop:
                self.pieces[pieces.BISHOP] -= end_bitboard_position
            elif move.is_promotion_to_rook:
                self.pieces[pieces.ROOK] -= end_bitboard_position
            elif move.is_promotion_to_queen:
                self.pieces[pieces.QUEEN] -= end_bitboard_position
            self.pieces[pieces.PAWN] |= end_bitboard_position

        self.update_piece_position(end_bitboard_position, start_bitboard_position)

        if move.is_kingside_castle:
            if move.is_white_to_move:
                self.update_piece_position(2**61, 2**63)
            else:
                self.update_piece_position(2**5, 2**7)
        elif move.is_queenside_castle:
            if move.is_white_to_move:
                self.update_piece_position(2**59, 2**56)
            else:
                self.update_piece_position(0b1000, 0b1)

        self.castling_rules = move.previous_castling_rules
        self.en_passant_target = move.previous_en_passant_target
        self.is_en_passant_target = bool(move.previous_en_passant_target)

        if move.is_capture:
            self.undo_capture(move, end_bitboard_position)
        
        if move.is_en_passant:
            self.undo_en_passant(move, end_bitboard_position)
        
        self.update_attack_tables(move, start_bitboard_position, end_bitboard_position)

        self.previous_positions.pop()

        self.white_to_move = not self.white_to_move

    def update_piece_position(self, start_bitboard_position, end_bitboard_position):
        position_change = end_bitboard_position - start_bitboard_position

        if self.is_white(start_bitboard_position): self.pieces[pieces.WHITE] += position_change
        else: self.pieces[pieces.BLACK] += position_change
        
        if self.is_pawn(start_bitboard_position): self.pieces[pieces.PAWN] += position_change
        elif self.is_knight(start_bitboard_position): self.pieces[pieces.KNIGHT] += position_change
        elif self.is_bishop(start_bitboard_position): self.pieces[pieces.BISHOP] += position_change
        elif self.is_rook(start_bitboard_position): self.pieces[pieces.ROOK] += position_change
        elif self.is_queen(start_bitboard_position): self.pieces[pieces.QUEEN] += position_change
        elif self.is_king(start_bitboard_position): self.pieces[pieces.KING] += position_change

    def update_zobrist_key(self, move, end_bitboard_position):
        piece_color = pieces.WHITE if move.is_white_to_move else pieces.BLACK

        if move.is_promotion:
            self.zobrist_key ^= self.zobrist_piece_numbers[piece_color | pieces.PAWN][move.start_position]
            if move.is_promotion_to_knight:
                self.zobrist_key ^= self.zobrist_piece_numbers[piece_color | pieces.KNIGHT][move.start_position]
            elif move.is_promotion_to_bishop:
                self.zobrist_key ^= self.zobrist_piece_numbers[piece_color | pieces.BISHOP][move.start_position]
            elif move.is_promotion_to_rook:
                self.zobrist_key ^= self.zobrist_piece_numbers[piece_color | pieces.ROOK][move.start_position]
            else:
                self.zobrist_key ^= self.zobrist_piece_numbers[piece_color | pieces.QUEEN][move.start_position]
        elif self.is_pawn(end_bitboard_position):
            self.zobrist_key ^= self.zobrist_piece_numbers[piece_color | pieces.PAWN][move.end_position]
            self.zobrist_key ^= self.zobrist_piece_numbers[piece_color | pieces.PAWN][move.start_position]
        elif self.is_knight(end_bitboard_position):
            self.zobrist_key ^= self.zobrist_piece_numbers[piece_color | pieces.KNIGHT][move.end_position]
            self.zobrist_key ^= self.zobrist_piece_numbers[piece_color | pieces.KNIGHT][move.start_position]
        elif self.is_bishop(end_bitboard_position):
            self.zobrist_key ^= self.zobrist_piece_numbers[piece_color | pieces.BISHOP][move.end_position]
            self.zobrist_key ^= self.zobrist_piece_numbers[piece_color | pieces.BISHOP][move.start_position]
        elif self.is_rook(end_bitboard_position):
            self.zobrist_key ^= self.zobrist_piece_numbers[piece_color | pieces.ROOK][move.end_position]
            self.zobrist_key ^= self.zobrist_piece_numbers[piece_color | pieces.ROOK][move.start_position]
        elif self.is_queen(end_bitboard_position):
            self.zobrist_key ^= self.zobrist_piece_numbers[piece_color | pieces.QUEEN][move.end_position]
            self.zobrist_key ^= self.zobrist_piece_numbers[piece_color | pieces.QUEEN][move.start_position]
        elif self.is_king(end_bitboard_position):
            self.zobrist_key ^= self.zobrist_piece_numbers[piece_color | pieces.KING][move.end_position]
            self.zobrist_key ^= self.zobrist_piece_numbers[piece_color | pieces.KING][move.start_position]
        
        if move.is_capture:
            if move.captured_pawn:
                self.zobrist_key ^= self.zobrist_piece_numbers[(0b11000 ^ piece_color) | pieces.PAWN][move.start_position]
            elif move.captured_knight:
                self.zobrist_key ^= self.zobrist_piece_numbers[(0b11000 ^ piece_color) | pieces.KNIGHT][move.start_position]
            elif move.captured_bishop:
                self.zobrist_key ^= self.zobrist_piece_numbers[(0b11000 ^ piece_color) | pieces.BISHOP][move.start_position]
            elif move.captured_rook:
                self.zobrist_key ^= self.zobrist_piece_numbers[(0b11000 ^ piece_color) | pieces.ROOK][move.start_position]
            elif move.captured_queen:
                self.zobrist_key ^= self.zobrist_piece_numbers[(0b11000 ^ piece_color) | pieces.QUEEN][move.start_position]
        elif move.is_en_passant:
            if move.is_white_to_move:
                self.zobrist_key ^= self.zobrist_piece_numbers[pieces.BLACK | pieces.PAWN][move.end_position + 8]
            else:
                self.zobrist_key ^= self.zobrist_piece_numbers[pieces.WHITE | pieces.PAWN][move.end_position - 8]

        if move.is_kingside_castle:
            if move.is_white_to_move:
                self.zobrist_key ^= self.zobrist_piece_numbers[pieces.WHITE | pieces.ROOK][61]
                self.zobrist_key ^= self.zobrist_piece_numbers[pieces.WHITE | pieces.ROOK][63]
            else:
                self.zobrist_key ^= self.zobrist_piece_numbers[pieces.BLACK | pieces.ROOK][5]
                self.zobrist_key ^= self.zobrist_piece_numbers[pieces.BLACK | pieces.ROOK][7]
        elif move.is_queenside_castle:
            if move.is_white_to_move:
                self.zobrist_key ^= self.zobrist_piece_numbers[pieces.WHITE | pieces.ROOK][56]
                self.zobrist_key ^= self.zobrist_piece_numbers[pieces.WHITE | pieces.ROOK][59]
            else:
                self.zobrist_key ^= self.zobrist_piece_numbers[pieces.BLACK | pieces.ROOK][0]
                self.zobrist_key ^= self.zobrist_piece_numbers[pieces.BLACK | pieces.ROOK][3]

        if move.previous_castling_rules & 0b10000 != self.white_can_kingside_castle:
            self.zobrist_key ^= self.zobrist_castling_numbers[0]
        if move.previous_castling_rules & 0b1000 != self.white_can_queenside_castle:
            self.zobrist_key ^= self.zobrist_castling_numbers[1]
        if move.previous_castling_rules & 0b100 != self.black_can_kingside_castle:
            self.zobrist_key ^= self.zobrist_castling_numbers[2]
        if move.previous_castling_rules & 0b10 != self.black_can_queenside_castle:
            self.zobrist_key ^= self.zobrist_castling_numbers[3]

        if move.previous_en_passant_target != 0:
            self.zobrist_key ^= self.zobrist_en_passant_numbers[int(math.log2(move.previous_en_passant_target) % 8)]
        if self.is_en_passant_target:
            self.zobrist_key ^= self.zobrist_en_passant_numbers[int(math.log2(self.en_passant_target) % 8)]


        self.zobrist_key ^= self.zobrist_white_to_move_number

    def capture_piece(self, bitboard_position):
        if self.is_white(bitboard_position): self.pieces[pieces.WHITE] -= bitboard_position
        else: self.pieces[pieces.BLACK] -= bitboard_position
        
        if self.is_pawn(bitboard_position): self.pieces[pieces.PAWN] -= bitboard_position
        elif self.is_knight(bitboard_position): self.pieces[pieces.KNIGHT] -= bitboard_position
        elif self.is_bishop(bitboard_position): self.pieces[pieces.BISHOP] -= bitboard_position
        elif self.is_rook(bitboard_position): self.pieces[pieces.ROOK] -= bitboard_position
        elif self.is_queen(bitboard_position): self.pieces[pieces.QUEEN] -= bitboard_position
        elif self.is_king(bitboard_position): self.pieces[pieces.KING] -= bitboard_position
    
    def undo_capture(self, move, bitboard_position):
        if move.captured_white: self.pieces[pieces.WHITE] |= bitboard_position
        else: self.pieces[pieces.BLACK] |= bitboard_position

        if move.captured_pawn: self.pieces[pieces.PAWN] |= bitboard_position
        elif move.captured_knight: self.pieces[pieces.KNIGHT] |= bitboard_position
        elif move.captured_bishop: self.pieces[pieces.BISHOP] |= bitboard_position
        elif move.captured_rook: self.pieces[pieces.ROOK] |= bitboard_position
        elif move.captured_queen: self.pieces[pieces.QUEEN] |= bitboard_position
        elif move.captured_king: self.pieces[pieces.KING] |= bitboard_position
    
    def undo_en_passant(self, move, bitboard_position):
        if move.is_white_to_move:
            pawn_position = bitboard_position << 8
            self.pieces[pieces.BLACK] |= pawn_position
        else:
            pawn_position = bitboard_position >> 8
            self.pieces[pieces.WHITE] |= pawn_position
        
        self.pieces[pieces.PAWN] |= pawn_position
    
    # -------------------------------- ATTACK TABLES --------------------------------

    def generate_attack_tables(self):
        self.attack_tables = dict()
        self.moves_blocking_white_check = 2**64 - 1
        self.moves_blocking_black_check = 2**64 - 1
        self.pieces_attacking_white_king = []
        self.pieces_attacking_black_king = []
        self.pinned_piece_moves = dict()
        self.pinning_pieces = dict()
        
        for position in range(64):
            bitboard_position = self.get_bitboard_position_from_index(position)
            self.attack_tables[bitboard_position] = 0
            
            if not self.is_piece(bitboard_position):
                continue

            self.update_piece_attack_table(position, bitboard_position)
    
    def update_attack_tables(self, move, start_bitboard_position, end_bitboard_position):
        self.moves_blocking_white_check = 2**64 - 1
        self.moves_blocking_black_check = 2**64 - 1
        self.pieces_attacking_white_king = []
        self.pieces_attacking_black_king = []

        if start_bitboard_position in self.pinning_pieces:
            self.pinned_piece_moves.pop(self.pinning_pieces.pop(start_bitboard_position))
        elif end_bitboard_position in self.pinning_pieces:
            self.pinned_piece_moves.pop(self.pinning_pieces.pop(end_bitboard_position))
        if start_bitboard_position in self.pinned_piece_moves:
            self.pinned_piece_moves.pop(self.pinning_pieces.pop(list(self.pinning_pieces.keys())[list(self.pinning_pieces.values()).index(start_bitboard_position)]))
        elif end_bitboard_position in self.pinned_piece_moves:
            self.pinned_piece_moves.pop(self.pinning_pieces.pop(list(self.pinning_pieces.keys())[list(self.pinning_pieces.values()).index(end_bitboard_position)]))

        self.update_piece_attack_table(move.start_position, start_bitboard_position)
        self.update_piece_attack_table(move.end_position, end_bitboard_position)

        if move.is_kingside_castle:
            if move.is_white_to_move:
                self.attack_tables[2**63] = 0
                self.update_piece_attack_table(61, 2**61)
            else:
                self.attack_tables[0b10000000] = 0
                self.update_piece_attack_table(5, 0b100000)
        elif move.is_queenside_castle:
            if move.is_white_to_move:
                self.attack_tables[2**56] = 0
                self.update_piece_attack_table(59, 2**59)
            else:
                self.attack_tables[0b1] = 0
                self.update_piece_attack_table(3, 0b1000)

        if self.pieces[pieces.KING] & (start_bitboard_position | end_bitboard_position) > 0:
            if self.is_white(self.pieces[pieces.KING] & (start_bitboard_position | end_bitboard_position)):
                enemy_sliding_pieces = self.pieces[pieces.BLACK] & (self.pieces[pieces.BISHOP] | self.pieces[pieces.ROOK] | self.pieces[pieces.QUEEN])
            else:
                enemy_sliding_pieces = self.pieces[pieces.WHITE] & (self.pieces[pieces.BISHOP] | self.pieces[pieces.ROOK] | self.pieces[pieces.QUEEN])

            for piece in self.bitboard_to_bitboard_positions(enemy_sliding_pieces):
                if piece[1] in self.pinning_pieces:
                    self.pinned_piece_moves.pop(self.pinning_pieces.pop(piece[1]))
                self.update_piece_attack_table(piece[0], piece[1])

        for piece in self.bitboard_to_bitboard_positions(self.pieces[pieces.BISHOP] | self.pieces[pieces.ROOK] | self.pieces[pieces.QUEEN]):
            if self.attack_tables[piece[1]] & (start_bitboard_position | end_bitboard_position) == 0:
                continue
            if piece[1] & (start_bitboard_position | end_bitboard_position) > 0:
                continue
            self.update_piece_attack_table(piece[0], piece[1])

    def update_piece_attack_table(self, position, bitboard_position):
        self.attack_tables[bitboard_position] = 0

        if not self.is_piece(bitboard_position):
            return

        if self.is_pawn(bitboard_position):
            self.update_pawn_attack_table(position, bitboard_position)
        elif self.is_knight(bitboard_position):
            self.update_knight_attack_table(position, bitboard_position)
        elif self.is_bishop(bitboard_position):
            self.update_sliding_piece_attack_table(position, bitboard_position, 4, 8)
        elif self.is_rook(bitboard_position):
            self.update_sliding_piece_attack_table(position, bitboard_position, 0, 4)
        elif self.is_queen(bitboard_position):
            self.update_sliding_piece_attack_table(position, bitboard_position, 0, 8)
        else:
            self.update_king_attack_table(position, bitboard_position)
    
    def update_pawn_attack_table(self, position, bitboard_position):
        if self.is_white(bitboard_position):
            if DISTANCE_TO_EDGE[position][0] > 0:
                self.attack_tables[bitboard_position] |= bitboard_position >> 7
            if DISTANCE_TO_EDGE[position][1] > 0:
                self.attack_tables[bitboard_position] |= bitboard_position >> 9
            
            if self.attack_tables[bitboard_position] & self.pieces[pieces.BLACK] & self.pieces[pieces.KING] > 0:
                self.moves_blocking_black_check = 0
                self.pieces_attacking_black_king.append(bitboard_position)
        else:
            if DISTANCE_TO_EDGE[position][0] > 0:
                self.attack_tables[bitboard_position] |= bitboard_position << 9
            if DISTANCE_TO_EDGE[position][1] > 0:
                self.attack_tables[bitboard_position] |= bitboard_position << 7
            
            if self.attack_tables[bitboard_position] & self.pieces[pieces.WHITE] & self.pieces[pieces.KING] > 0:
                self.moves_blocking_white_check = 0
                self.pieces_attacking_white_king.append(bitboard_position)
    def update_knight_attack_table(self, position, bitboard_position):
        for move in KNIGHT_MOVES[position]:
            if move > 0:
                target_bitboard_position = bitboard_position << move
            else:
                target_bitboard_position = bitboard_position >> -move
                
            self.attack_tables[bitboard_position] |= target_bitboard_position

        if self.attack_tables[bitboard_position] & self.pieces[pieces.BLACK] & self.pieces[pieces.KING] and self.is_white(bitboard_position):
            self.moves_blocking_black_check = 0
            self.pieces_attacking_black_king.append(bitboard_position)
        elif self.attack_tables[bitboard_position] & self.pieces[pieces.WHITE] & self.pieces[pieces.KING] and self.is_black(bitboard_position):
            self.moves_blocking_white_check = 0
            self.pieces_attacking_white_king.append(bitboard_position)         
    def update_sliding_piece_attack_table(self, position, bitboard_position, start_direction_offset_index, end_direction_offset_index):      
        for direction_offset_index in range(start_direction_offset_index, end_direction_offset_index):
            direction_offset = SLIDING_PIECE_DIRECTION_OFFSETS[direction_offset_index]
            for i in range(DISTANCE_TO_EDGE[position][direction_offset_index]):
                if direction_offset > 0:
                    target_bitboard_position = bitboard_position << (direction_offset * (i+1))
                else:
                    target_bitboard_position = bitboard_position >> -(direction_offset * (i+1))

                self.attack_tables[bitboard_position] |= target_bitboard_position

                # If it finds a king, store moves that block the check
                if self.is_king(target_bitboard_position):
                    if self.is_white(bitboard_position) and self.is_black(target_bitboard_position):
                        blocking_moves = 0
                        for j in range(i):
                            if direction_offset > 0:
                                blocking_moves |= bitboard_position << (direction_offset * (j+1))
                            else:
                                blocking_moves |= bitboard_position >> -(direction_offset * (j+1))
                        self.moves_blocking_black_check &= blocking_moves
                        self.pieces_attacking_black_king.append(bitboard_position)
                    elif self.is_black(bitboard_position) and self.is_white(target_bitboard_position):
                        blocking_moves = 0
                        for j in range(i):
                            if direction_offset > 0:
                                blocking_moves |= bitboard_position << (direction_offset * (j+1))
                            else:
                                blocking_moves |= bitboard_position >> -(direction_offset * (j+1))
                        self.moves_blocking_white_check &= blocking_moves
                        self.pieces_attacking_white_king.append(bitboard_position)
                    else:
                        break # Same colour, so can't move through them

                elif self.is_piece(target_bitboard_position):
                    if self.is_white(target_bitboard_position) != self.is_white(bitboard_position):
                        self.check_pinned(position + direction_offset * (i+1), target_bitboard_position, direction_offset_index, bitboard_position)
                    break   
    def update_king_attack_table(self, position, bitboard_position):
        for move in KING_MOVES[position]:
            if move > 0:
                self.attack_tables[bitboard_position] |= bitboard_position << move
            else:
                self.attack_tables[bitboard_position] |= bitboard_position >> -move

    def check_pinned(self, position, bitboard_position, direction_offset_index, pinning_piece_bitboard_position):
        direction_offset = SLIDING_PIECE_DIRECTION_OFFSETS[direction_offset_index]
        opposite_direction_offset_index = direction_offset_index + 1 if direction_offset > 0 else direction_offset_index - 1
        for i in range(DISTANCE_TO_EDGE[position][direction_offset_index]):
            if direction_offset > 0:
                target_bitboard_position = bitboard_position << (direction_offset * (i+1))
            else:
                target_bitboard_position = bitboard_position >> -(direction_offset * (i+1))

            if self.is_king(target_bitboard_position):
                if self.is_white(target_bitboard_position) == self.is_white(bitboard_position):
                    pinned_pieces_moves = 0
                    for j in range(i):
                        if direction_offset > 0:
                            pinned_pieces_moves |= bitboard_position << (direction_offset * (j+1))
                        else:
                            pinned_pieces_moves |= bitboard_position >> -(direction_offset * (j+1))
                    for j in range(DISTANCE_TO_EDGE[int(math.log2(bitboard_position))][opposite_direction_offset_index]):
                        if direction_offset > 0:
                            target_pinned_piece_move = bitboard_position >> (direction_offset * (j+1))
                        else:
                            target_pinned_piece_move = bitboard_position << -(direction_offset * (j+1))
                        
                        if self.is_piece(target_pinned_piece_move):
                            break

                        pinned_pieces_moves |= target_pinned_piece_move

                    if pinning_piece_bitboard_position in self.pinning_pieces:
                        self.pinned_piece_moves.pop(self.pinning_pieces.pop(pinning_piece_bitboard_position))
                    if bitboard_position in self.pinned_piece_moves:
                        self.pinned_piece_moves.pop(self.pinning_pieces.pop(list(self.pinning_pieces.keys())[list(self.pinning_pieces.values()).index(bitboard_position)]))

                    self.pinned_piece_moves[bitboard_position] = pinned_pieces_moves
                    self.pinning_pieces[pinning_piece_bitboard_position] = bitboard_position
                return
    
    # -------------------------------- UTILITES + PROPERTIES --------------------------------

    def get_piece_color(self, bitboard_position):
        if self.is_white(bitboard_position): return pieces.WHITE
        return pieces.BLACK
    def get_piece_type(self, bitboard_position):
        if self.is_pawn(bitboard_position): return pieces.PAWN
        if self.is_knight(bitboard_position): return pieces.KNIGHT
        if self.is_bishop(bitboard_position): return pieces.BISHOP
        if self.is_rook(bitboard_position): return pieces.ROOK
        if self.is_queen(bitboard_position): return pieces.QUEEN
        if self.is_king(bitboard_position): return pieces.KING
    
    def is_piece(self, bitboard_position):
        return bitboard_position & (self.pieces[pieces.WHITE] | self.pieces[pieces.BLACK]) > 0   
    def is_white(self, bitboard_position):
        return self.pieces[pieces.WHITE] & bitboard_position > 0
    def is_black(self, bitboard_position):
        return self.pieces[pieces.BLACK] & bitboard_position > 0
    
    def is_pawn(self, bitboard_position):
        return self.pieces[pieces.PAWN] & bitboard_position > 0
    def is_knight(self, bitboard_position):
        return self.pieces[pieces.KNIGHT] & bitboard_position > 0
    def is_bishop(self, bitboard_position):
        return self.pieces[pieces.BISHOP] & bitboard_position > 0
    def is_rook(self, bitboard_position):
        return self.pieces[pieces.ROOK] & bitboard_position > 0
    def is_queen(self, bitboard_position):
        return self.pieces[pieces.QUEEN] & bitboard_position > 0
    def is_king(self, bitboard_position):
        return self.pieces[pieces.KING] & bitboard_position > 0

    def is_pinned(self, bitboard_position):
        return bitboard_position in self.pinned_piece_moves and self.pinned_piece_moves[bitboard_position] & (self.pieces[pieces.WHITE] | self.pieces[pieces.BLACK]) == 0


    def bitboard_to_bitboard_positions(self, bitboard):
        bitboard_string = bin(bitboard)[:1:-1]
        i = bitboard_string.find('1')
        while i != -1:
            yield (i, 2**i)
            i = bitboard_string.find('1', i+1)

    def get_bitboard_position_from_index(self, index: int):
        return 0b1 << index

    @property
    def white_to_move(self):
        return self.game_data & 0b10000000 > 0
    @white_to_move.setter
    def white_to_move(self, value):
        if value and not self.game_data & 0b10000000:
            self.game_data += 0b10000000
        elif not value and self.game_data & 0b10000000:
            self.game_data -= 0b10000000
    
    @property
    def white_pieces_attack_table(self):
        attacks = 0
        for piece in self.bitboard_to_bitboard_positions(self.pieces[pieces.WHITE]):
            attacks |= self.attack_tables[piece[1]]
        return attacks   
    @property
    def black_pieces_attack_table(self):
        attacks = 0
        for piece in self.bitboard_to_bitboard_positions(self.pieces[pieces.BLACK]):
            attacks |= self.attack_tables[piece[1]]
        return attacks
    
    @property
    def white_in_check(self):
        return self.pieces[pieces.WHITE] & self.pieces[pieces.KING] & self.black_pieces_attack_table > 0     
    @property
    def black_in_check(self):
        return self.pieces[pieces.BLACK] & self.pieces[pieces.KING] & self.white_pieces_attack_table > 0
    @property
    def player_in_check(self):
        return self.white_in_check or self.black_in_check

    @property
    def white_can_kingside_castle(self):
        return self.game_data & 0b10000 > 0 
    @white_can_kingside_castle.setter
    def white_can_kingside_castle(self, value):
        if value and not self.game_data & 0b10000:
            self.game_data += 0b10000
        elif not value and self.game_data & 0b10000:
            self.game_data -= 0b10000 
    
    @property
    def white_can_queenside_castle(self):
        return self.game_data & 0b1000 > 0 
    @white_can_queenside_castle.setter
    def white_can_queenside_castle(self, value):
        if value and not self.game_data & 0b1000:
            self.game_data += 0b1000
        elif not value and self.game_data & 0b1000:
            self.game_data -= 0b1000 
    
    @property
    def black_can_kingside_castle(self):
        return self.game_data & 0b100 > 0   
    @black_can_kingside_castle.setter
    def black_can_kingside_castle(self, value):
        if value and not self.game_data & 0b100:
            self.game_data += 0b100
        elif not value and self.game_data & 0b100:
            self.game_data -= 0b100 
    
    @property
    def black_can_queenside_castle(self):
        return self.game_data & 0b10 > 0 
    @black_can_queenside_castle.setter
    def black_can_queenside_castle(self, value):
        if value and not self.game_data & 0b10:
            self.game_data += 0b10
        elif not value and self.game_data & 0b10:
            self.game_data -= 0b10

    @property
    def castling_rules(self):
        return self.game_data & 0b11110
    @castling_rules.setter
    def castling_rules(self, value):
        self.game_data |= value

    @property
    def is_en_passant_target(self):
        return self.game_data & 0b1 > 0  
    @is_en_passant_target.setter
    def is_en_passant_target(self, value):
        if value and not self.game_data & 0b1:
            self.game_data += 0b1
        elif not value and self.game_data & 0b1:
            self.game_data -= 0b1
    