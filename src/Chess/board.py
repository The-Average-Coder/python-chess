import string, math

from Chess import pieces
from Chess.move import Move 
from Chess.distance_to_edge import DISTANCE_TO_EDGE
from Chess.knight_moves import KNIGHT_MOVES
from Chess.king_moves import KING_MOVES

STARTING_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
#STARTING_FEN = 'rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8'

SLIDING_PIECE_DIRECTION_OFFSETS = [ 1, -1, 8, -8, 7, -7, 9, -9 ]

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

        self.generate_attack_tables()

    def fen_is_valid(self, FEN):
        return True
    
    def get_bitboard_position_from_index(self, index: int):
        return 2**index

    @property
    def white_move(self):
        return self.game_data & 0b10000000 > 0
    
    @white_move.setter
    def white_move(self, value):
        if value and not self.game_data & 0b10000000:
            self.game_data += 0b10000000
        elif not value and self.game_data & 0b10000000:
            self.game_data -= 0b10000000
    
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

    def is_piece(self, bitboard_position):
        return bitboard_position & (self.white_pieces | self.black_pieces) > 0

    def is_white(self, bitboard_position):
        return self.white_pieces & bitboard_position > 0
    def is_black(self, bitboard_position):
        return self.black_pieces & bitboard_position > 0
    
    def is_pawn(self, bitboard_position):
        return self.pawns & bitboard_position > 0
    def is_knight(self, bitboard_position):
        return self.knights & bitboard_position > 0
    def is_bishop(self, bitboard_position):
        return self.bishops & bitboard_position > 0
    def is_rook(self, bitboard_position):
        return self.rooks & bitboard_position > 0
    def is_queen(self, bitboard_position):
        return self.queens & bitboard_position > 0
    def is_king(self, bitboard_position):
        return self.kings & bitboard_position > 0
    
    def is_move_legal(self, start_bitboard_position, end_bitboard_position):
        if self.is_white(start_bitboard_position) and self.is_white(end_bitboard_position):
            return False
        if self.is_black(start_bitboard_position) and self.is_black(end_bitboard_position):
            return False
        if self.is_pawn(start_bitboard_position):
            if self.is_white(start_bitboard_position):
                if start_bitboard_position >> 8 == end_bitboard_position and self.is_piece(end_bitboard_position):
                    return False
                if start_bitboard_position >> 16 == end_bitboard_position and (self.is_piece(end_bitboard_position) or self.is_piece(start_bitboard_position >> 8)):
                    return False
                if (start_bitboard_position >> 7 == end_bitboard_position or start_bitboard_position >> 9 == end_bitboard_position) and not (self.is_black(end_bitboard_position) or end_bitboard_position == self.en_passant_target):
                    return False
            if self.is_black(start_bitboard_position):
                if start_bitboard_position << 8 == end_bitboard_position and self.is_piece(end_bitboard_position):
                    return False
                if start_bitboard_position << 16 == end_bitboard_position and (self.is_piece(end_bitboard_position) or self.is_piece(start_bitboard_position << 8)):
                    return False
                if (start_bitboard_position << 7 == end_bitboard_position or start_bitboard_position << 9 == end_bitboard_position) and not self.is_piece(end_bitboard_position):
                    return False
        
        return True

    def make_move(self, move):
        if move.is_capture:
            self.capture_piece(move.end_bitboard_position)
        
        elif move.is_en_passant:
            if move.is_white_move:
                self.capture_piece(move.end_bitboard_position << 8)
            else:
                self.capture_piece(move.end_bitboard_position >> 8)

        self.is_en_passant_target = False
        self.en_passant_target = 0

        # Check if pawn double move to add as en passant target
        if self.is_pawn(move.start_bitboard_position) and (move.start_bitboard_position << 16 == move.end_bitboard_position or move.start_bitboard_position >> 16 == move.end_bitboard_position):
            self.is_en_passant_target = True
                
            if move.is_white_move:
                self.en_passant_target = move.start_bitboard_position >> 8
            else:
                self.en_passant_target = move.start_bitboard_position << 8

        # Check if king to disallow castling
        elif move.start_bitboard_position == 0b1000000000000000000000000000000000000000000000000000000000000:
            self.white_can_kingside_castle = False
            self.white_can_queenside_castle = False
        elif move.start_bitboard_position == 0b10000:
            self.black_can_kingside_castle = False
            self.black_can_queenside_castle = False
        
        # Check if rook to disallow castling
        elif (move.start_bitboard_position | move.end_bitboard_position) & 1000000000000000000000000000000000000000000000000000000000000000 > 0:
            self.white_can_kingside_castle = False
        elif (move.start_bitboard_position | move.end_bitboard_position) & 100000000000000000000000000000000000000000000000000000000 > 0:
            self.white_can_queenside_castle = False
        elif (move.start_bitboard_position | move.end_bitboard_position) & 0b10000000 > 0:
            self.black_can_kingside_castle = False
        elif (move.start_bitboard_position | move.end_bitboard_position) & 0b1 > 0:
            self.black_can_queenside_castle = False

        self.update_piece_position(move.start_bitboard_position, move.end_bitboard_position)

        if move.is_promotion:
            self.pawns -= move.end_bitboard_position
            if move.is_promotion_to_knight:
                self.knights |= move.end_bitboard_position
            elif move.is_promotion_to_bishop:
                self.bishops |= move.end_bitboard_position
            elif move.is_promotion_to_rook:
                self.rooks |= move.end_bitboard_position
            elif move.is_promotion_to_queen:
                self.queens |= move.end_bitboard_position

        if move.is_kingside_castle:
            if move.is_white_move:
                self.update_piece_position(2**63, 2**61)
            else:
                self.update_piece_position(2**7, 2**5)
        elif move.is_queenside_castle:
            if move.is_white_move:
                self.update_piece_position(2**56, 2**59)
            else:
                self.update_piece_position(0b1, 0b1000)

        self.update_attack_tables(move)

        #print(f"{[int(math.log2(i)) for i in self.pinning_pieces]} pinning {[int(math.log2(i)) for i in self.pinned_piece_moves]}")

        self.white_move = not self.white_move
    
    def undo_move(self, move):
        if move.is_promotion:
            if move.is_promotion_to_knight:
                self.knights -= move.end_bitboard_position
            elif move.is_promotion_to_bishop:
                self.bishops -= move.end_bitboard_position
            elif move.is_promotion_to_rook:
                self.rooks -= move.end_bitboard_position
            elif move.is_promotion_to_queen:
                self.queens -= move.end_bitboard_position
            self.pawns |= move.end_bitboard_position

        self.update_piece_position(move.end_bitboard_position, move.start_bitboard_position)

        if move.is_kingside_castle:
            if move.is_white_move:
                self.update_piece_position(2**61, 2**63)
            else:
                self.update_piece_position(2**5, 2**7)
        elif move.is_queenside_castle:
            if move.is_white_move:
                self.update_piece_position(2**59, 2**56)
            else:
                self.update_piece_position(0b1000, 0b1)

        self.castling_rules = move.previous_castling_rules
        self.en_passant_target = move.previous_en_passant_target
        self.is_en_passant_target = bool(move.previous_en_passant_target)

        if move.is_capture:
            self.undo_capture(move)
        
        if move.is_en_passant:
            self.undo_en_passant(move)
        
        self.update_attack_tables(move)

        #print(f"{[int(math.log2(i)) for i in self.pinning_pieces]} pinning {[int(math.log2(i)) for i in self.pinned_piece_moves]}")

        self.white_move = not self.white_move

    def update_piece_position(self, start_bitboard_position, end_bitboard_position):
        position_change = end_bitboard_position - start_bitboard_position

        if self.is_white(start_bitboard_position): self.white_pieces += position_change
        else: self.black_pieces += end_bitboard_position - start_bitboard_position
        
        if self.is_pawn(start_bitboard_position): self.pawns += position_change
        elif self.is_knight(start_bitboard_position): self.knights += position_change
        elif self.is_bishop(start_bitboard_position): self.bishops += position_change
        elif self.is_rook(start_bitboard_position): self.rooks += position_change
        elif self.is_queen(start_bitboard_position): self.queens += position_change
        elif self.is_king(start_bitboard_position): self.kings += position_change

    def check_capture(self, end_bitboard_position):        
        capture = 0
        if self.is_white(end_bitboard_position): capture += pieces.WHITE
        elif self.is_black(end_bitboard_position): capture += pieces.BLACK

        if capture == 0:
            return 0
        
        if self.is_pawn(end_bitboard_position): capture += pieces.PAWN
        elif self.is_knight(end_bitboard_position): capture += pieces.KNIGHT
        if self.is_bishop(end_bitboard_position): capture += pieces.BISHOP
        elif self.is_rook(end_bitboard_position): capture += pieces.ROOK
        if self.is_queen(end_bitboard_position): capture += pieces.QUEEN
        elif self.is_king(end_bitboard_position): capture += pieces.KING
        
        return capture

    def check_kingside_castle(self, start_bitboard_position, end_bitboard_position):
        if self.is_white(start_bitboard_position) and self.is_king(start_bitboard_position) and end_bitboard_position == 2**62 and self.white_can_kingside_castle:
                return True
        elif self.is_black(start_bitboard_position) and self.is_king(start_bitboard_position) and end_bitboard_position == 0b1000000 and self.black_can_kingside_castle:
                return True
    
    def check_queenside_castle(self, start_bitboard_position, end_bitboard_position):
        if self.is_white(start_bitboard_position) and self.is_king(start_bitboard_position) and end_bitboard_position == 2**58 and self.white_can_queenside_castle:
                return True
        elif self.is_black(start_bitboard_position) and self.is_king(start_bitboard_position) and end_bitboard_position == 0b100 and self.black_can_queenside_castle:
                return True

    def check_en_passant_available(self):
        return self.is_en_passant_target

    def check_en_passant(self, start_bitboard_position, end_bitboard_position):
        return self.is_pawn(start_bitboard_position) and end_bitboard_position == self.en_passant_target

    def capture_piece(self, bitboard_position):
        if self.is_white(bitboard_position): self.white_pieces -= bitboard_position
        else: self.black_pieces -= bitboard_position
        
        if self.is_pawn(bitboard_position): self.pawns -= bitboard_position
        elif self.is_knight(bitboard_position): self.knights -= bitboard_position
        elif self.is_bishop(bitboard_position): self.bishops -= bitboard_position
        elif self.is_rook(bitboard_position): self.rooks -= bitboard_position
        elif self.is_queen(bitboard_position): self.queens -= bitboard_position
        elif self.is_king(bitboard_position): self.kings -= bitboard_position
    
    def undo_capture(self, move):
        if move.captured_white: self.white_pieces |= move.end_bitboard_position
        else: self.black_pieces |= move.end_bitboard_position

        if move.captured_pawn: self.pawns |= move.end_bitboard_position
        elif move.captured_knight: self.knights |= move.end_bitboard_position
        elif move.captured_bishop: self.bishops |= move.end_bitboard_position
        elif move.captured_rook: self.rooks |= move.end_bitboard_position
        elif move.captured_queen: self.queens |= move.end_bitboard_position
        elif move.captured_king: self.kings |= move.end_bitboard_position
    
    def undo_en_passant(self, move):
        if move.is_white_move:
            pawn_position = move.end_bitboard_position << 8
            self.black_pieces |= pawn_position
        else:
            pawn_position = move.end_bitboard_position >> 8
            self.white_pieces |= pawn_position
        
        self.pawns |= pawn_position
    
    # -------------------------------- MOVE GENERATION --------------------------------

    def get_legal_moves(self):
        moves = []

        pieces = self.bitboard_to_bitboard_positions(self.white_pieces if self.white_move else self.black_pieces)

        for piece in pieces:
            moves += self.get_piece_legal_moves(piece[0], piece[1])

        return moves

    def get_piece_legal_moves(self, position, bitboard_position):
        if self.is_pawn(bitboard_position):
            moves_bitboard = self.get_pawn_legal_moves(position, bitboard_position)

        elif self.is_king(bitboard_position):
            moves_bitboard = self.get_king_legal_moves(bitboard_position)

        else:
            attacks = self.attack_tables[bitboard_position]

            if self.is_white(bitboard_position):
                moves_bitboard = attacks & (~self.white_pieces)
                if self.white_in_check:
                    if len(self.pieces_attacking_white_king) == 1:
                        moves_bitboard &= self.moves_blocking_white_check | self.pieces_attacking_white_king[0]
                    else:
                        moves_bitboard &= self.moves_blocking_white_check
            else:
                moves_bitboard = attacks & (~self.black_pieces)
                if self.black_in_check:
                    if len(self.pieces_attacking_black_king) == 1:
                        moves_bitboard &= self.moves_blocking_black_check | self.pieces_attacking_black_king[0]
                    else:
                        moves_bitboard &= self.moves_blocking_black_check
            
            if self.is_pinned(bitboard_position):
                moves_bitboard &= (self.pinned_piece_moves[bitboard_position] | list(self.pinning_pieces.keys())[list(self.pinning_pieces.values()).index(bitboard_position)])
            
        
        moves = []

        for move in self.bitboard_to_bitboard_positions(moves_bitboard):
            if self.is_pawn(bitboard_position) and ((self.is_white(bitboard_position) and 0 <= move[0] <= 7) or (self.is_black(bitboard_position) and 56 <= move[0] <= 63)):
                for promotion in range(1, 5):
                    moves.append(Move(bitboard_position, move[1], self, promotion))
            else:
                moves.append(Move(bitboard_position, move[1], self))
        
        return moves
    
    def get_pawn_legal_moves(self, position, bitboard_position):
        if self.is_white(bitboard_position):
            moves = ((((bitboard_position >> 7) if DISTANCE_TO_EDGE[position][0] > 0 else 0) | ((bitboard_position >> 9) if DISTANCE_TO_EDGE[position][1] > 0 else 0)) & (self.black_pieces | self.en_passant_target)
                     | bitboard_position >> 8 & ~(self.white_pieces | self.black_pieces))
            
            # Allow Two Squares If First Move
            if 2**48 <= bitboard_position <= 2**55 and bitboard_position >> 8 & ~(self.white_pieces | self.black_pieces):
                moves |= bitboard_position >> 16 & ~(self.white_pieces | self.black_pieces)
            
            if self.white_in_check:
                if len(self.pieces_attacking_white_king) == 1:
                    moves &= self.moves_blocking_white_check | self.pieces_attacking_white_king[0]
                else:
                    moves &= self.moves_blocking_white_check
        else:
            moves = ((((bitboard_position << 7) if DISTANCE_TO_EDGE[position][1] > 0 else 0) | ((bitboard_position << 9) if DISTANCE_TO_EDGE[position][0] > 0 else 0)) & (self.white_pieces | self.en_passant_target)
                     | bitboard_position << 8 & ~(self.white_pieces | self.black_pieces))
            
            # Allow Two Squares If First Move
            if 2**8 <= bitboard_position <= 2**15 and bitboard_position << 8 & ~(self.white_pieces | self.black_pieces):
                moves |= bitboard_position << 16 & ~(self.white_pieces | self.black_pieces)
            
            if self.black_in_check:
                if len(self.pieces_attacking_black_king) == 1:
                    moves &= self.moves_blocking_black_check | self.pieces_attacking_black_king[0]
                else:
                    moves &= self.moves_blocking_black_check

        if self.is_pinned(bitboard_position):
            moves &= (self.pinned_piece_moves[bitboard_position] | list(self.pinning_pieces.keys())[list(self.pinning_pieces.values()).index(bitboard_position)])
        
        return moves

    def get_king_legal_moves(self, bitboard_position):
        attacks = self.attack_tables[bitboard_position]

        if self.is_white(bitboard_position):
            moves_bitboard = attacks & (~self.white_pieces) & (~self.black_pieces_attack_table)
        else:
            moves_bitboard = attacks & (~self.black_pieces) & (~self.white_pieces_attack_table)
        
        if self.is_white(bitboard_position) and not self.white_in_check:
            if self.white_can_kingside_castle and (2**61 | 2**62) & (self.white_pieces | self.black_pieces | self.black_pieces_attack_table) == 0:
                moves_bitboard |= 2**62
            if self.white_can_queenside_castle and (2**57 | 2**58 | 2**59) & (self.white_pieces | self.black_pieces | self.black_pieces_attack_table) == 0:
                moves_bitboard |= 2**58
        elif self.is_black(bitboard_position) and not self.black_in_check:
            if self.black_can_kingside_castle and 0b1100000 & (self.white_pieces | self.black_pieces | self.white_pieces_attack_table) == 0:
                moves_bitboard |= 0b1000000
            if self.black_can_queenside_castle and 0b1110 & (self.white_pieces | self.black_pieces | self.white_pieces_attack_table) == 0:
                moves_bitboard |= 0b100
        
        return moves_bitboard

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
    
    def update_attack_tables(self, move):
        self.moves_blocking_white_check = 2**64 - 1
        self.moves_blocking_black_check = 2**64 - 1
        self.pieces_attacking_white_king = []
        self.pieces_attacking_black_king = []

        if move.start_bitboard_position in self.pinning_pieces:
            self.pinned_piece_moves.pop(self.pinning_pieces.pop(move.start_bitboard_position))
        elif move.end_bitboard_position in self.pinning_pieces:
            self.pinned_piece_moves.pop(self.pinning_pieces.pop(move.end_bitboard_position))
        if move.start_bitboard_position in self.pinned_piece_moves:
            self.pinned_piece_moves.pop(self.pinning_pieces.pop(list(self.pinning_pieces.keys())[list(self.pinning_pieces.values()).index(move.start_bitboard_position)]))
        elif move.end_bitboard_position in self.pinned_piece_moves:
            self.pinned_piece_moves.pop(self.pinning_pieces.pop(list(self.pinning_pieces.keys())[list(self.pinning_pieces.values()).index(move.end_bitboard_position)]))

        self.update_piece_attack_table(int(math.log2(move.start_bitboard_position)), move.start_bitboard_position)
        self.update_piece_attack_table(int(math.log2(move.end_bitboard_position)), move.end_bitboard_position)

        if move.is_kingside_castle:
            if move.is_white_move:
                self.attack_tables[2**63] = 0
                self.update_piece_attack_table(61, 2**61)
            else:
                self.attack_tables[0b10000000] = 0
                self.update_piece_attack_table(5, 0b100000)
        elif move.is_queenside_castle:
            if move.is_white_move:
                self.attack_tables[2**56] = 0
                self.update_piece_attack_table(59, 2**59)
            else:
                self.attack_tables[0b1] = 0
                self.update_piece_attack_table(3, 0b1000)

        if self.kings & (move.start_bitboard_position | move.end_bitboard_position) > 0:
            if self.is_white(self.kings & (move.start_bitboard_position | move.end_bitboard_position)):
                enemy_sliding_pieces = self.black_pieces & (self.bishops | self.rooks | self.queens)
            else:
                enemy_sliding_pieces = self.white_pieces & (self.bishops | self.rooks | self.queens)

            for piece in self.bitboard_to_bitboard_positions(enemy_sliding_pieces):
                if piece[1] in self.pinning_pieces:
                    self.pinned_piece_moves.pop(self.pinning_pieces.pop(piece[1]))
                self.update_piece_attack_table(piece[0], piece[1])

        for piece in self.bitboard_to_bitboard_positions(self.bishops | self.rooks | self.queens):
            if self.attack_tables[piece[1]] & (move.start_bitboard_position | move.end_bitboard_position) == 0:
                continue
            if piece[1] & (move.start_bitboard_position | move.end_bitboard_position) > 0:
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
            
            if self.attack_tables[bitboard_position] & self.black_pieces & self.kings > 0:
                self.moves_blocking_black_check = 0
                self.pieces_attacking_black_king.append(bitboard_position)
        else:
            if DISTANCE_TO_EDGE[position][0] > 0:
                self.attack_tables[bitboard_position] |= bitboard_position << 7
            if DISTANCE_TO_EDGE[position][1] > 0:
                self.attack_tables[bitboard_position] |= bitboard_position << 9
            
            if self.attack_tables[bitboard_position] & self.white_pieces & self.kings > 0:
                self.moves_blocking_white_check = 0
                self.pieces_attacking_white_king.append(bitboard_position)
        
    def update_knight_attack_table(self, position, bitboard_position):
        for move in KNIGHT_MOVES[position]:
            if move > 0:
                target_bitboard_position = bitboard_position << move
            else:
                target_bitboard_position = bitboard_position >> -move
                
            self.attack_tables[bitboard_position] |= target_bitboard_position

        if self.attack_tables[bitboard_position] & self.black_pieces & self.kings and self.is_white(bitboard_position):
            self.moves_blocking_black_check = 0
            self.pieces_attacking_black_king.append(bitboard_position)
        elif self.attack_tables[bitboard_position] & self.white_pieces & self.kings and self.is_black(bitboard_position):
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
                        self.check_pinned(target_bitboard_position, direction_offset_index, bitboard_position)
                    break
    
    def update_king_attack_table(self, position, bitboard_position):
        for move in KING_MOVES[position]:
            if move > 0:
                self.attack_tables[bitboard_position] |= bitboard_position << move
            else:
                self.attack_tables[bitboard_position] |= bitboard_position >> -move

    def check_pinned(self, bitboard_position, direction_offset_index, pinning_piece_bitboard_position):
        direction_offset = SLIDING_PIECE_DIRECTION_OFFSETS[direction_offset_index]
        opposite_direction_offset_index = direction_offset_index + 1 if direction_offset > 0 else direction_offset_index - 1
        for i in range(DISTANCE_TO_EDGE[int(math.log2(bitboard_position))][direction_offset_index]):
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

    def is_pinned(self, bitboard_position):
        return bitboard_position in self.pinned_piece_moves and self.pinned_piece_moves[bitboard_position] & (self.white_pieces | self.black_pieces) == 0

    def bitboard_to_bitboard_positions(self, bitboard):
        bitboard_string = bin(bitboard)[:1:-1]
        i = bitboard_string.find('1')
        while i != -1:
            yield (i, 2**i)
            i = bitboard_string.find('1', i+1)

    @property
    def white_pieces_attack_table(self):
        attacks = 0
        for piece in self.bitboard_to_bitboard_positions(self.white_pieces):
            attacks |= self.attack_tables[piece[1]]
        return attacks
    
    @property
    def black_pieces_attack_table(self):
        attacks = 0
        for piece in self.bitboard_to_bitboard_positions(self.black_pieces):
            attacks |= self.attack_tables[piece[1]]
        return attacks
    
    @property
    def white_in_check(self):
        return self.white_pieces & self.kings & self.black_pieces_attack_table > 0
    
    @property
    def black_in_check(self):
        return self.black_pieces & self.kings & self.white_pieces_attack_table > 0