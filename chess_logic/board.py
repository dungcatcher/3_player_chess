"""TODO: Clean up handle mouse event code"""

import pygame
import pygame.freetype
from .movegen import piece_movegen, make_move, colour_to_segment
from .classes import Position

STARTING_POSITION = [
    [  # White segment
        [None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None],
        ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
        ["wr", "wn", "wb", 'wq', "wk", "wb", "wn", "wr"]
    ],
    [  # Black segment
        [None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None],
        ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
        ["br", "bn", "bb", "bq", "bk", "bb", "bn", "br"]
    ],
    [  # Red segment
        [None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None],
        ["rp", "rp", "rp", "rp", "rp", "rp", "rp", "rp"],
        ["rr", "rn", "rb", "rq", "rk", "rb", "rn", "rr"]
    ]
]


letter_to_colour = {
    'w': 'white',
    'b': 'black',
    'r': 'red'
}


def test_fastest_checkmate(board, depth):
    moves = 0
    turn_legal_moves = []
    for segment in range(3):
        for y in range(4):
            for x in range(8):
                square_occupant = board.position[segment][y][x]
                if square_occupant is not None and square_occupant[0] == board.turn:
                    turn_legal_moves += piece_movegen(board, Position(segment, (x, y)), square_occupant[0])

    if depth == 0:
        return len(turn_legal_moves)

    for move in turn_legal_moves:
        new_board = make_move(board, move)
        new_board.turn_index = (new_board.turn_index + 1) % len(new_board.turns)
        new_board.turn = new_board.turns[new_board.turn_index]
        moves += test_fastest_checkmate(new_board, depth - 1)

    return moves


class Board:
    def __init__(self):
        """
        Board is represented as a list of 2d arrays of the 3 8x4 segments
        """
        self.position = STARTING_POSITION
        self.turns = ["w", "r", "b"]
        self.turn_index = 0
        self.turn = self.turns[self.turn_index]
        self.winner = None
        self.stalemated_players = []
        self.checkmated_players = []
        self.castling_rights = {
            'w': {'kingside': True, 'queenside': True},
            'b': {'kingside': True, 'queenside': True},
            'r': {'kingside': True, 'queenside': True}
        }
        self.enpassant_squares = {  # Squares that can be taken en passant
            'w': None, 'b': None, 'r': None
        }

    def index_position(self, position):  # Helper function to prevent long indexing code
        return self.position[int(position.segment)][int(position.square.y)][int(position.square.x)]

    def update_castling_rights(self, move):
        piece_colour = self.index_position(move.end)[0]
        king_square = self.index_position(Position(colour_to_segment[piece_colour], (4, 3)))
        if king_square != f'{piece_colour}k':  # If the king is not on its start square it has moved
            self.castling_rights[piece_colour]["queenside"] = False
            self.castling_rights[piece_colour]["kingside"] = False
            print(self.castling_rights[piece_colour])
        kingside_rook_square = self.index_position(Position(colour_to_segment[piece_colour], (7, 3)))
        if kingside_rook_square is None or kingside_rook_square != f'{piece_colour}r':
            self.castling_rights[piece_colour]["kingside"] = False
            print(self.castling_rights[piece_colour])
        queenside_rook_square = self.index_position(Position(colour_to_segment[piece_colour], (0, 3)))
        if queenside_rook_square is None or queenside_rook_square != f'{piece_colour}r':
            self.castling_rights[piece_colour]["queenside"] = False
            print(self.castling_rights[piece_colour])

    def check_winner(self):
        if len(self.checkmated_players) == 2:
            self.winner = self.turn
            print(self.winner)
