import pygame
from polygons import compute_polygons, handle_polygon_resize
from movegen import piece_movegen
from shapely.geometry import Polygon, Point
from pieces import Piece
from classes import Position


def resize_board(img, section_size, position):
    scale = section_size[0] * 0.95 / img.get_width()
    img = pygame.transform.smoothscale(img, (img.get_width() * scale, img.get_height() * scale))
    rect = img.get_rect()
    rect.center = position

    return [img, rect, scale]


class Board:
    def __init__(self, screen_size):
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
        self.outline_rect = pygame.Rect(0, 0, screen_size[0] * 0.7, screen_size[1])
        self.image, self.rect, self.scale = resize_board(
            pygame.image.load('./Assets/board.png'), self.outline_rect.size, self.outline_rect.center)
        self.polygons = compute_polygons()
        self.polygons = handle_polygon_resize(self.polygons, self.scale, self.rect.topleft)
        self.move_polygon_surface = pygame.Surface(screen_size, pygame.SRCALPHA)
        self.move_indicator_surface = pygame.Surface(screen_size, pygame.SRCALPHA)
        self.pieces = []
        self.turns = ["w", "b", "r"]
        self.turn_index = 0
        self.turn = self.turns[self.turn_index]
        self.selected_piece = None

    def refresh_pieces(self):
        new_pieces = []
        for segment in range(3):
            for y in range(4):
                for x in range(8):
                    if self.position[segment][y][x] is not None:
                        piece_id = self.position[segment][y][x]
                        piece_polygon = Polygon(self.polygons[segment][y][x])
                        piece_pixel_pos = piece_polygon.centroid.coords[:][0]
                        new_pieces.append(Piece(piece_id[0], Position(
                            segment, (x, y)), piece_pixel_pos, piece_id[1]))
        self.pieces = new_pieces

    def handle_mouse_events(self, mouse_position, left_click, move_table):
        if self.selected_piece is not None:
            self.move_indicator_surface.fill((0, 0, 0, 0))
            self.move_polygon_surface.fill((0, 0, 0, 0))  # Fill transparent
            for move in self.selected_piece.moves:
                move_polygon_points = self.polygons[int(
                    move.end.segment)][int(move.end.square.y)][int(move.end.square.x)]
                move_polygon = Polygon(move_polygon_points)
                move_pixel_pos = move_polygon.centroid.coords[:][0]
                pygame.draw.circle(self.move_indicator_surface, (255, 0, 0), move_pixel_pos, 8)

                point = Point(mouse_position)
                if point.within(move_polygon):
                    pygame.draw.polygon(self.move_polygon_surface, (255, 255, 255), move_polygon_points, width=5)

                    if left_click:
                        move_table.add_move(move, self.position)
                        if move.promo_type is None:
                            self.position[int(move.end.segment)][int(move.end.square.y)][int(move.end.square.x)] = \
                                self.position[  # Set move square to selected piece
                                    int(self.selected_piece.position.segment)][int(self.selected_piece.position.square.y)][
                                    int(self.selected_piece.position.square.x)]
                        else:
                            self.position[int(move.end.segment)][int(move.end.square.y)][int(move.end.square.x)] = \
                                f'{self.position[int(self.selected_piece.position.segment)][int(self.selected_piece.position.square.y)][int(self.selected_piece.position.square.x)][0]}q'
                        self.position[int(self.selected_piece.position.segment)][int(self.selected_piece.position.square.y)][
                            int(self.selected_piece.position.square.x)] = None

                        self.refresh_pieces()
                        self.selected_piece.moves = []
                        self.selected_piece = None
                        self.turn_index = (self.turn_index + 1) % 3
                        self.turn = self.turns[self.turn_index]
        else:
            self.move_indicator_surface.fill((0, 0, 0, 0))
            self.move_polygon_surface.fill((0, 0, 0, 0))  # Fill transparent

        for piece in self.pieces:
            if piece.rect.collidepoint(mouse_position):
                if not piece.highlighted:
                    piece.image = pygame.transform.smoothscale(piece.image, (60, 60))
                    piece.rect = piece.image.get_rect(center=piece.pixel_pos)
                    piece.highlighted = True
                if piece.colour == self.turn and left_click:
                    self.selected_piece = piece
                    self.selected_piece.moves = piece_movegen(self.position, piece.position, piece.colour)
            else:
                piece.image = piece.original_image
                piece.rect = piece.image.get_rect(center=piece.pixel_pos)
                piece.highlighted = False

    def render(self, surface, left_click, mouse_position, move_table):
        pygame.draw.rect(surface, (70, 70, 80), self.outline_rect)
        surface.blit(self.image, self.rect)
        surface.blit(self.move_polygon_surface, (0, 0))
        surface.blit(self.move_indicator_surface, (0, 0))

        self.handle_mouse_events(mouse_position, left_click, move_table)
        for piece in self.pieces:
            surface.blit(piece.image, piece.rect)
