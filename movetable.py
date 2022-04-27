import pygame
import pygame.freetype
from movegen import in_check, get_game_state, make_move, piece_movegen, positions_are_same
from classes import Position
import time

pygame.freetype.init()

COORDINATE_TABLE = [
    [  # Segment 1
        ['a4', 'b4', 'c4', 'd4', 'e4', 'f4', 'g4', 'h4'],
        ['a3', 'b3', 'c3', 'd3', 'e3', 'f3', 'g3', 'h3'],
        ['a2', 'b2', 'c2', 'd2', 'e2', 'f2', 'g2', 'h2'],
        ['a1', 'b1', 'c1', 'd1', 'e1', 'f1', 'g1', 'h1']
    ],
    [  # Segment 2
        ['h9', 'g9', 'f9', 'e9', 'i9', 'j9', 'k9', 'l9'],
        ['h10', 'g10', 'f10', 'e10', 'i10', 'j10', 'k10', 'l10'],
        ['h11', 'g11', 'f11', 'e11', 'i11', 'j11', 'k11', 'l11'],
        ['h12', 'g12', 'f12', 'e12', 'i12', 'j12', 'k12', 'l12']
    ],
    [  # Segment 3
        ['l5', 'k5', 'j5', 'i5', 'd5', 'c5', 'b5', 'a5'],
        ['l6', 'k6', 'j6', 'i6', 'd6', 'c6', 'b6', 'a6'],
        ['l7', 'k7', 'j7', 'i7', 'd7', 'c7', 'b7', 'a7'],
        ['l8', 'k8', 'j8', 'i8', 'd8', 'c8', 'b8', 'a8']
    ]
]

title_font = pygame.freetype.Font('./Assets/BAHNSCHRIFT.TTF', 20)
move_font = pygame.freetype.Font('./Assets/BAHNSCHRIFT.TTF', 14)


def move_to_notation(board, move):
    if move is None:
        notation = "-"
    else:
        notation = ""
        piece_colour, piece_id = board.position[int(move.start.segment)][int(move.start.square.y)][int(move.start.square.x)]

        capture = False
        if board.position[int(move.end.segment)][int(move.end.square.y)][int(move.end.square.x)] is not None \
                and board.position[int(move.end.segment)][int(move.end.square.y)][int(move.end.square.x)][0] != piece_id[0]:  # Capture
            capture = True
        if move.move_type == "enpassant":
            capture = True

        if move.move_type != "kingside castle" and move.move_type != "queenside castle":
            notation += piece_id.upper()

            piece_start_square = COORDINATE_TABLE[int(move.start.segment)][int(move.start.square.y)][int(move.start.square.x)]
            specify_file = False
            specify_rank = False
            #  Search for pieces that can also play that move
            for segment in range(3):
                for y in range(4):
                    for x in range(8):
                        current_position = Position(segment, (x, y))
                        if not positions_are_same(current_position, move.start):  # Don't check itself
                            if board.position[segment][y][x] is not None and board.position[segment][y][x] == f'{piece_colour}{piece_id}':
                                for same_piece_move in piece_movegen(board, Position(segment, (x, y)), piece_colour):
                                    if positions_are_same(same_piece_move.end, move.end):
                                        same_piece_start_square = COORDINATE_TABLE[segment][y][x]
                                        if piece_start_square[0] != same_piece_start_square[0]:
                                            specify_file = True
                                        elif piece_start_square[1] != same_piece_start_square[1]:
                                            specify_rank = True
            if specify_file:
                notation += piece_start_square[0]
            if specify_rank:
                notation += piece_start_square[1]
            if capture:
                notation += 'x'
        elif move.move_type == "kingside castle":
            notation += '0-0'
        elif move.move_type == "queenside castle":
            notation += '0-0-0'

        end_square = COORDINATE_TABLE[int(move.end.segment)][int(move.end.square.y)][int(move.end.square.x)]
        if move.move_type != "kingside castle" and move.move_type != "queenside castle":
            notation += end_square

        if move.is_promotion:
            notation += f'={move.promo_type.upper()}'

        new_position = make_move(board, move)
        for turn in board.turns:
            if turn != piece_colour and turn not in board.checkmated_players:
                if get_game_state(new_position, turn) == "checkmate":
                    notation += '#'
                elif in_check(new_position, turn):  # Check if the resulting position is in check
                    notation += '+'

    return notation


class MoveTable:
    def __init__(self, screen_size):
        self.outline_rect = pygame.Rect(screen_size[0] * 0.7, 0, screen_size[0] * 0.3, screen_size[1])
        self.move_table_surface = pygame.Surface((self.outline_rect.width * 0.7, self.outline_rect.height * 0.7))
        self.move_table_rect = self.move_table_surface.get_rect(topleft=(self.outline_rect.left + self.outline_rect.width * 0.15, self.outline_rect.height * 0.15))
        self.moves = [[]]  # [ [ply, ply, ply], ... ]
        self.result = None
        self.move = 0

    def add_move(self, board, move):
        move_notation = move_to_notation(board, move)
        if len(self.moves[self.move]) <= len(board.turns) - 1:
            self.moves[self.move].append(move_notation)
        else:
            self.move += 1
            self.moves.append([])
            self.moves[self.move].append(move_notation)

    def render(self, surface):
        pygame.draw.rect(surface, (40, 40, 40), self.outline_rect)

        title_surface, title_rect = title_font.render('Moves', (255, 255, 255))
        title_rect.center = (self.outline_rect.centerx, self.outline_rect.height * 0.05)
        surface.blit(title_surface, title_rect)

        for i, move in enumerate(self.moves):
            move_num_container_rect = pygame.Rect(self.move_table_rect.left, self.move_table_rect.top + i * self.move_table_rect.height * 0.07,
                    self.move_table_rect.width * 0.1, self.move_table_rect.height * 0.07)

            move_num_surface, move_num_rect = move_font.render(str(i + 1), (255, 255, 255))
            move_num_rect.center = move_num_container_rect.center
            surface.blit(move_num_surface, move_num_rect)
            pygame.draw.line(surface, (100, 100, 100), move_num_container_rect.topright, move_num_container_rect.bottomright)

            for j, ply in enumerate(move):
                ply_container_rect = pygame.Rect(move_num_container_rect.right + self.move_table_rect.width * 0.3 * j, move_num_container_rect.top,
                        self.move_table_rect.width * 0.3, move_num_container_rect.height)
                ply_text_surface, ply_text_rect = move_font.render(ply, (255, 255, 255))
                ply_text_rect.center = ply_container_rect.center
                surface.blit(ply_text_surface, ply_text_rect)

        if self.result is not None:
            result_rect = pygame.Rect(self.move_table_rect.left + self.move_table_rect.width * 0.1,
                                      self.move_table_rect.top + len(self.moves) * self.move_table_rect.height * 0.07,
                                      self.move_table_rect.width * 0.9, self.move_table_rect.height * 0.07)
            result_text_surface, result_text_rect = move_font.render(self.result, (255, 255, 255))
            result_text_rect.center = result_rect.center
            surface.blit(result_text_surface, result_text_rect)
