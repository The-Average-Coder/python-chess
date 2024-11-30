from Chess.Board import pieces
from Chess.Board.move import Move

import time

class MoveGenerator:
    def __init__(self, board):
        self.board = board
    
    def get_legal_moves(self):
        if self.board.previous_positions.count(self.board.zobrist_key) >= 3:
            return []

        moves = []

        if self.board.white_to_move:
            pieces_bitboard = self.board.pieces[pieces.WHITE]
        else:
            pieces_bitboard = self.board.pieces[pieces.BLACK]
        
        pieces_list = self.board.bitboard_to_bitboard_positions(pieces_bitboard)

        for piece in pieces_list:
            moves += self.get_piece_legal_moves(piece)

        return moves

    def get_piece_legal_moves(self, piece):
        
        start_time = time.perf_counter()

        if self.board.previous_positions.count(self.board.zobrist_key) >= 3:
            return []

        position, bitboard_position = piece[0], piece[1]

        if self.board.is_pawn(bitboard_position):
            moves_bitboard = self.get_pawn_legal_moves(position, bitboard_position)
            moves = self.moves_bitboard_to_moves(position, bitboard_position, moves_bitboard)
            return moves
        if self.board.is_king(bitboard_position):
            moves_bitboard = self.get_king_legal_moves(bitboard_position)
            moves = self.moves_bitboard_to_moves(position, bitboard_position, moves_bitboard)
            return moves
         
        attacks = self.board.attack_tables[bitboard_position]

        friendly_piece_color = self.board.get_piece_color(bitboard_position)

        moves_bitboard = attacks & (~self.board.pieces[friendly_piece_color])

        if self.board.player_in_check:
            moves_blocking_check = self.board.moves_blocking_white_check & self.board.moves_blocking_black_check

            if len(self.board.pieces_attacking_white_king) == 1:
                moves_blocking_check |= self.board.pieces_attacking_white_king[0]
            if len(self.board.pieces_attacking_black_king) == 1:
                moves_blocking_check |= self.board.pieces_attacking_black_king[0]

            moves_bitboard &= moves_blocking_check
        
        if self.board.is_pinned(bitboard_position):
            moves_bitboard &= (self.board.pinned_piece_moves[bitboard_position] | list(self.board.pinning_pieces.keys())[list(self.board.pinning_pieces.values()).index(bitboard_position)])
        
        moves_list = self.moves_bitboard_to_moves(position, bitboard_position, moves_bitboard)

        return moves_list
   
    def get_pawn_legal_moves(self, position, bitboard_position):
        if self.board.is_white(bitboard_position):
            moves = bitboard_position >> 8 & ~(self.board.pieces[pieces.WHITE] | self.board.pieces[pieces.BLACK])

            moves |= self.board.attack_tables[bitboard_position] & (self.board.pieces[pieces.BLACK] | self.board.en_passant_target)
            
            # Allow Two Squares If First Move
            if 0b1000000000000000000000000000000000000000000000000 <= bitboard_position <= 0b10000000000000000000000000000000000000000000000000000000 and bitboard_position >> 8 & ~(self.board.pieces[pieces.WHITE] | self.board.pieces[pieces.BLACK]):
                moves |= bitboard_position >> 16 & ~(self.board.pieces[pieces.WHITE] | self.board.pieces[pieces.BLACK])
            
            if self.board.white_in_check:
                if len(self.board.pieces_attacking_white_king) == 1:
                    moves &= self.board.moves_blocking_white_check | self.board.pieces_attacking_white_king[0]
                else:
                    moves &= self.board.moves_blocking_white_check
        else:
            moves = bitboard_position << 8 & ~(self.board.pieces[pieces.WHITE] | self.board.pieces[pieces.BLACK])

            moves |= self.board.attack_tables[bitboard_position] & (self.board.pieces[pieces.WHITE] | self.board.en_passant_target)
            
            # Allow Two Squares If First Move
            if 0b100000000 <= bitboard_position <= 0b1000000000000000 and bitboard_position << 8 & ~(self.board.pieces[pieces.WHITE] | self.board.pieces[pieces.BLACK]):
                moves |= bitboard_position << 16 & ~(self.board.pieces[pieces.WHITE] | self.board.pieces[pieces.BLACK])
            
            if self.board.black_in_check:
                if len(self.board.pieces_attacking_black_king) == 1:
                    moves &= self.board.moves_blocking_black_check | self.board.pieces_attacking_black_king[0]
                else:
                    moves &= self.board.moves_blocking_black_check

        if self.board.is_pinned(bitboard_position):
            moves &= (self.board.pinned_piece_moves[bitboard_position] | list(self.board.pinning_pieces.keys())[list(self.board.pinning_pieces.values()).index(bitboard_position)])
        
        return moves

    def get_king_legal_moves(self, bitboard_position):
        attacks = self.board.attack_tables[bitboard_position]

        if self.board.white_to_move:
            moves_bitboard = attacks & ~(self.board.pieces[pieces.WHITE] | self.board.black_pieces_attack_table)
        else:
            moves_bitboard = attacks & ~(self.board.pieces[pieces.BLACK] | self.board.white_pieces_attack_table)
        
        white_can_kingside_castle = self.board.white_to_move and self.board.white_can_kingside_castle and not self.board.white_in_check and 0b110000000000000000000000000000000000000000000000000000000000000 & (self.board.pieces[pieces.WHITE] | self.board.pieces[pieces.BLACK] | self.board.black_pieces_attack_table) == 0
        white_can_queenside_castle = self.board.white_to_move and self.board.white_can_queenside_castle and not self.board.white_in_check and 0b110000000000000000000000000000000000000000000000000000000000 & (self.board.pieces[pieces.WHITE] | self.board.pieces[pieces.BLACK] | self.board.black_pieces_attack_table) == 0
        black_can_kingside_castle = not self.board.white_to_move and self.board.black_can_kingside_castle and not self.board.black_in_check and 0b1100000 & (self.board.pieces[pieces.WHITE] | self.board.pieces[pieces.BLACK] | self.board.white_pieces_attack_table) == 0
        black_can_queenside_castle = not self.board.white_to_move and self.board.black_can_queenside_castle and not self.board.black_in_check and 0b1100 & (self.board.pieces[pieces.WHITE] | self.board.pieces[pieces.BLACK] | self.board.white_pieces_attack_table) == 0

        if white_can_kingside_castle:
            moves_bitboard |= 0b100000000000000000000000000000000000000000000000000000000000000
        if white_can_queenside_castle:
            moves_bitboard |= 0b10000000000000000000000000000000000000000000000000000000000
        if black_can_kingside_castle:
            moves_bitboard |= 0b1000000
        if black_can_queenside_castle:
            moves_bitboard |= 0b100
        
        return moves_bitboard

    def moves_bitboard_to_moves(self, start_position, start_bitboard_position, moves_bitboard):
        moves = []
        
        for end_position in self.moves_bitboard_to_positions(moves_bitboard):
            move_data = self.get_move_data(start_bitboard_position, end_position)
            if self.board.is_pawn(start_bitboard_position) and ((self.board.is_white(start_bitboard_position) and 0 <= end_position <= 7) or (self.board.is_black(start_bitboard_position) and 56 <= end_position <= 63)):
                # Move is promotion
                for promotion in range(1, 5):
                    promotion_move_data = move_data | promotion << 1
                    moves.append(Move(start_position, end_position, promotion_move_data, self.board.castling_rules, self.board.en_passant_target))
            else:
                move_data = self.get_move_data(start_bitboard_position, end_position)
                moves.append(Move(start_position, end_position, move_data, self.board.castling_rules, self.board.en_passant_target))
        
        return moves

    def moves_bitboard_to_positions(self, moves_bitboard):
        while moves_bitboard > 0:
            position = self.ffs(moves_bitboard)
            yield position
            moves_bitboard &= ~(2**position)
   
    def ffs(self, x):
        """Returns the index, counting from 0, of the
        least significant set bit in `x`.
        """
        return (x&-x).bit_length()-1
   
    def get_move_data(self, start_bitboard_position, end_position):
        # Bit 1: white or black move
        # Bits 2-6: capture
        # Bits 7-8: castling
        # Bits 9-11: promotion
        # Bit 12: en passant

        end_bitboard_position = 2**end_position

        move_data = 0
        if self.board.white_to_move:
            move_data |= 0b100000000000
        
        capture_data = 0
        if self.board.is_white(end_bitboard_position): capture_data |= pieces.WHITE
        elif self.board.is_black(end_bitboard_position): capture_data |= pieces.BLACK

        if capture_data != 0:
            if self.board.is_pawn(end_bitboard_position): capture_data |= pieces.PAWN
            elif self.board.is_knight(end_bitboard_position): capture_data |= pieces.KNIGHT
            elif self.board.is_bishop(end_bitboard_position): capture_data |= pieces.BISHOP
            elif self.board.is_rook(end_bitboard_position): capture_data |= pieces.ROOK
            elif self.board.is_queen(end_bitboard_position): capture_data |= pieces.QUEEN
            else: capture_data |= pieces.KING

            move_data |= capture_data << 6
        
        if self.board.is_white(start_bitboard_position) and self.board.is_king(start_bitboard_position) and end_bitboard_position == 0b100000000000000000000000000000000000000000000000000000000000000 and self.board.white_can_kingside_castle:
            move_data |= 0b100000
        elif self.board.is_black(start_bitboard_position) and self.board.is_king(start_bitboard_position) and end_bitboard_position == 0b1000000 and self.board.black_can_kingside_castle:
            move_data |= 0b100000
        
        if self.board.is_white(start_bitboard_position) and self.board.is_king(start_bitboard_position) and end_bitboard_position == 0b10000000000000000000000000000000000000000000000000000000000 and self.board.white_can_queenside_castle:
            move_data |= 0b10000
        elif self.board.is_black(start_bitboard_position) and self.board.is_king(start_bitboard_position) and end_bitboard_position == 0b100 and self.board.black_can_queenside_castle:
            move_data |= 0b10000
        
        if self.board.is_pawn(start_bitboard_position) and end_bitboard_position == self.board.en_passant_target:
            move_data |= 1
        
        return move_data