import pygame
from polygons import compute_polygons, handle_polygon_resize
from shapely.geometry import Polygon
from pieces import Piece
from classes import Position


def resize_board(img, section_size, position):
    scale = section_size[0] * 0.95 / img.get_width()
    img = pygame.transform.smoothscale(img, (img.get_width() * scale, img.get_height() * scale))
    rect = img.get_rect()
    rect.center = position

    return [img, rect, scale]


class Board:
    def __init__(self, section_size, position):
        """
        Board is represented as a list of 2d arrays of the 3 8x4 segments
        """
        self.position = [
            [  # White segment
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
                ["wr", "wn", "wb", "wq", "wk", "wb", "wn", "wr"]
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
        self.image, self.rect, self.scale = resize_board(
            pygame.image.load('./Assets/board.png'), section_size, position)
        self.polygons = compute_polygons()
        self.polygons = handle_polygon_resize(self.polygons, self.scale, self.rect.topleft)
        self.turns = ["w", "b", "r"]
        self.turn_index = 0
        self.turn = self.turns[self.turn_index]

    def refresh_pieces(self):
        pieces = []
        for segment in range(3):
            for y in range(4):
                for x in range(8):
                    if self.position[segment][y][x] is not None:
                        piece_id = self.position[segment][y][x]
                        piece_polygon = Polygon(self.polygons[segment][y][x])
                        piece_pixel_pos = piece_polygon.centroid.coords[:][0]
                        pieces.append(Piece(piece_id[0], Position(
                            segment, (x, y)), piece_pixel_pos, piece_id[1]))

        return pieces
