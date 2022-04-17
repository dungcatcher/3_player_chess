import pygame
import pygame.freetype

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

title_font = pygame.freetype.Font('./Assets/BAHNSCHRIFT.TTF', 24)
move_font = pygame.freetype.Font('./Assets/BAHNSCHRIFT.TTF', 14)


def move_to_notation(move, board_position):
    notation = ""

    piece_id = board_position[int(move.start.segment)][int(move.start.square.y)][int(move.start.square.x)][1]
    if piece_id != "p":
        notation += piece_id.upper()
    end_square = COORDINATE_TABLE[int(move.end.segment)][int(move.end.square.y)][int(move.end.square.x)]
    notation += end_square

    return notation


class MoveTable:
    def __init__(self, screen_size):
        self.outline_rect = pygame.Rect(screen_size[0] * 0.7, 0, screen_size[0] * 0.3, screen_size[1])
        self.move_table_surface = pygame.Surface((self.outline_rect.width * 0.7, self.outline_rect.height * 0.7))
        self.move_table_rect = self.move_table_surface.get_rect(topleft=(self.outline_rect.width + self.outline_rect.width * 0.15, self.outline_rect.height * 0.15))
        self.moves = [[]]  # [ [ply, ply, ply], ... ]
        self.move = 0

    def add_move(self, move, board_position):
        move_notation = move_to_notation(move, board_position)
        if len(self.moves[self.move]) <= 2:
            self.moves[self.move].append(move_notation)
        else:
            self.move += 1
            self.moves.append([])
            self.moves[self.move].append(move_notation)
        print(self.moves)

    def render(self, surface):
        pygame.draw.rect(surface, (40, 40, 40), self.outline_rect)

        title_surface, title_rect = title_font.render('Moves', (255, 255, 255))
        title_rect.center = (self.outline_rect.centerx, self.outline_rect.height * 0.05)
        surface.blit(title_surface, title_rect)
