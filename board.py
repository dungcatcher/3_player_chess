import pygame
from config import WIDTH, HEIGHT
from polygons import compute_polygons, handle_polygon_resize
from movegen import piece_movegen, in_checkmate, make_move
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
    def __init__(self):
        """
        Board is represented as a list of 2d arrays of the 3 8x4 segments
        """
        self.position = [
            [  # White segment
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
                ["wr", "wn", "wb", 'wq', "wk", "wb", "wn", "wr"]
            ],
            [  # Black segment
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                ["bp", "bp", "bp", "bp", "bp", "bp", "wp", "bp"],
                ["br", "bn", "bb", "bq", "bk", "bb", "bn", "br"]
            ],
            [  # Red segment
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                ["rp", "rp", "rp", "rp", "rp", "rp", "rp", "rp"],
                ["rr", "rn", "rb", "rq", "rk", "rb", "rn", "rr"]
            ]
        ]
        self.outline_rect = pygame.Rect(0, 0, WIDTH * 0.7, HEIGHT)
        self.image, self.rect, self.scale = resize_board(
            pygame.image.load('./Assets/board.png'), self.outline_rect.size, self.outline_rect.center)
        self.polygons = compute_polygons()
        self.polygons = handle_polygon_resize(self.polygons, self.scale, self.rect.topleft)
        self.move_polygon_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.move_indicator_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.promotion_selector_surface = pygame.Surface(self.outline_rect.size, pygame.SRCALPHA)
        self.pieces = []
        self.turns = ["w", "b", "r"]
        self.turn_index = 0
        self.turn = self.turns[self.turn_index]
        self.selected_piece = None
        self.castling_rights = {
            'w': {'kingside': True, 'queenside': True},
            'b': {'kingside': True, 'queenside': True},
            'r': {'kingside': True, 'queenside': True}
        }
        self.enpassant_squares = {  # Squares that can be taken en passant
            'w': None, 'b': None, 'r': None
        }
        self.in_promotion_selector = False
        self.promotion_selection_list = ['q', 'r', 'b', 'n']
        self.promotion_selection_images = {
            'w': [], 'b': [], 'r': []
        }
        self.promotion_move = None  #  Stores the move if a promotion happens
        for colour in self.turns:  # Load images for promotion selection
            for piece in self.promotion_selection_list:
                image = pygame.image.load(f'./Assets/pieces/{colour}{piece}.png')
                self.promotion_selection_images[colour].append(image)

    def index_position(self, position):  # Helper function to prevent long indexing code
        return self.position[int(position.segment)][int(position.square.y)][int(position.square.x)]

    def refresh_pieces(self):
        new_pieces = []
        for segment in range(3):
            for y in range(4):
                for x in range(8):
                    if self.position[segment][y][x] is not None:
                        piece_id = self.position[segment][y][x]
                        piece_polygon = Polygon(self.polygons[segment][y][x])
                        piece_pixel_pos = piece_polygon.centroid.coords[:][0]
                        piece_alive = True if piece_id[0] in self.turns else False
                        new_pieces.append(Piece(piece_id[0], Position(
                            segment, (x, y)), piece_pixel_pos, piece_id[1], piece_alive))
        self.pieces = new_pieces

    def update_castling_rights(self, move):
        piece_colour = self.index_position(move.start)[0]

        king_square = self.index_position(Position(move.start.segment, (4, 3)))
        if king_square is None or king_square != f'{piece_colour}k':  # If the king is not on its start square it has moved
            self.castling_rights[piece_colour]['queenside'] = False
            self.castling_rights[piece_colour]['kingside'] = False
        kingside_rook_square = self.index_position(Position(move.start.segment, (7, 3)))
        if kingside_rook_square is None or kingside_rook_square != f'{piece_colour}r':
            self.castling_rights[piece_colour]['kingside'] = False
        queenside_rook_square = self.index_position(Position(move.start.segment, (0, 3)))
        if queenside_rook_square is None or queenside_rook_square != f'{piece_colour}r':
            self.castling_rights[piece_colour]['queenside'] = False

    def handle_mouse_events(self, mouse_position, left_click, move_table):
        if self.selected_piece is not None and not self.in_promotion_selector:
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
                    pygame.draw.polygon(self.move_polygon_surface, (255, 255, 255), move_polygon_points, width=3)

                    if left_click:
                        self.update_castling_rights(move)
                        if not move.is_promotion:
                            move_table.add_move(self, move, self.selected_piece.colour)
                            self.position = make_move(self, move).position  # Make the move on the board
                            self.enpassant_squares[self.selected_piece.colour] = None  # Update en passant squares
                            if move.move_type == "double push":
                                self.enpassant_squares[self.selected_piece.colour] = \
                                    Position(move.end.segment, (move.end.square.x, move.end.square.y + 1))
                            self.selected_piece.moves = []
                            self.selected_piece = None
                            for turn in self.turns:
                                if in_checkmate(self, turn):
                                    self.turns.remove(turn)
                            self.refresh_pieces()
                            self.turn_index = (self.turn_index + 1) % len(self.turns)
                            self.turn = self.turns[self.turn_index]
                        else:
                            self.in_promotion_selector = True
                            self.promotion_move = move
                            left_click = False

        else:
            self.move_indicator_surface.fill((0, 0, 0, 0))
            self.move_polygon_surface.fill((0, 0, 0, 0))  # Fill transparent

        if self.in_promotion_selector:
            self.promotion_selector_surface.fill((0, 0, 0, 50))
            for i in range(4):  # Loop through the four y values from the promotion square in the segment
                selection_polygon_points = self.polygons[int(self.promotion_move.end.segment)][int(self.promotion_move.end.square.y - i)][
                    int(self.promotion_move.end.square.x)]
                pygame.draw.polygon(self.promotion_selector_surface, (0, 0, 0), selection_polygon_points)
                selection_polygon = Polygon(selection_polygon_points)
                selection_polygon_centre = selection_polygon.centroid.coords[:][0]
                selection_image = self.promotion_selection_images[self.selected_piece.colour][i]
                selection_image = pygame.transform.smoothscale(selection_image, (40, 40))
                selection_image_rect = selection_image.get_rect(center=selection_polygon_centre)
                self.promotion_selector_surface.blit(selection_image, selection_image_rect)
                point = Point(mouse_position)

                if point.within(selection_polygon):
                    pygame.draw.polygon(self.promotion_selector_surface, (255, 255, 255), selection_polygon_points, 3)
                    if left_click:
                        self.promotion_move.promo_type = self.promotion_selection_list[i]
                        move_table.add_move(self, self.promotion_move, self.selected_piece.colour)
                        self.position = make_move(self, self.promotion_move).position  # Make the move on the board
                        self.position[int(self.promotion_move.end.segment)][int(self.promotion_move.end.square.y)][
                            int(self.promotion_move.end.square.x)] = self.selected_piece.colour + self.promotion_move.promo_type
                        self.enpassant_squares[self.selected_piece.colour] = None  # Update en passant squares
                        self.selected_piece.moves = []
                        self.selected_piece = None
                        for turn in self.turns:
                            if in_checkmate(self, turn):
                                self.turns.remove(turn)
                        self.refresh_pieces()
                        self.turn_index = (self.turn_index + 1) % len(self.turns)
                        self.turn = self.turns[self.turn_index]
                        self.in_promotion_selector = False
                        break

        for piece in self.pieces:
            if piece.rect.collidepoint(mouse_position) and not self.in_promotion_selector:
                if not piece.highlighted:
                    piece.image = pygame.transform.smoothscale(piece.image, (60, 60))
                    piece.rect = piece.image.get_rect(center=piece.pixel_pos)
                    piece.highlighted = True
                if piece.colour == self.turn and left_click:
                    self.selected_piece = piece
                    self.selected_piece.moves = piece_movegen(self, piece.position, piece.colour)
            else:
                piece.image = piece.original_image
                piece.rect = piece.image.get_rect(center=piece.pixel_pos)
                piece.highlighted = False

    def render(self, surface):
        pygame.draw.rect(surface, (70, 70, 80), self.outline_rect)
        surface.blit(self.image, self.rect)
        for piece in self.pieces:
            surface.blit(piece.image, piece.rect)

        surface.blit(self.move_polygon_surface, (0, 0))
        surface.blit(self.move_indicator_surface, (0, 0))
        if self.in_promotion_selector:
            surface.blit(self.promotion_selector_surface, self.outline_rect.topleft)


