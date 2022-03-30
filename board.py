import pygame
from config import *
from polygons import *

class Board:
    def __init__(self):
        """
        Board is represented as a list of 2d arrays of the 3 8x4 segments
        """
        self.position = [
            [  # White segment
                [None, None, None, "wb", None, None, None, None],
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

board_img = pygame.image.load('./Assets/board.png').convert_alpha()
board_scale = HEIGHT / board_img.get_height()
board_img = pygame.transform.smoothscale(board_img, (board_img.get_width(
) * board_scale, board_img.get_height() * board_scale))
board_rect = board_img.get_rect()
board_rect.center = WIDTH // 2, HEIGHT // 2
margin = (WIDTH - board_rect.width) / 2

board_polygons = compute_polygons()
board_polygons = handle_polygon_resize(board_polygons, board_scale, margin)