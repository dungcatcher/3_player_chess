"""TODO: Clean up handle mouse event code"""

import pygame
from polygons import compute_polygons, handle_polygon_resize, draw_thick_aapolygon
from movegen import piece_movegen, get_game_state, make_move
from shapely.geometry import Polygon, Point
from pieces import Piece
from classes import Position


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
        self.turns = ["w", "b", "r"]
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

    def check_winner(self):
        if len(self.checkmated_players) == 2:
            self.winner = self.turn
            print(self.winner)


class RenderBoard:
    def __init__(self, screen_size):
        self.board = Board()
        self.outline_rect = pygame.Rect(0, 0, screen_size[0] * 0.7, screen_size[1])
        self.image, self.rect, self.scale = resize_board(
            pygame.image.load('./Assets/board.png'), self.outline_rect.size, self.outline_rect.center)
        self.selected_piece = None
        self.polygons = compute_polygons()
        self.polygons = handle_polygon_resize(self.polygons, self.scale, self.rect.topleft)
        self.move_polygon_surface = pygame.Surface(screen_size, pygame.SRCALPHA)
        self.move_indicator_surface = pygame.Surface(screen_size, pygame.SRCALPHA)
        self.result_surface = pygame.Surface(screen_size, pygame.SRCALPHA)
        self.result_rect = pygame.Rect(0, 0, self.outline_rect.width * 0.4, self.outline_rect.width * 0.6)
        self.result_rect.center = self.outline_rect.center

        self.promotion_selector_surface = pygame.Surface(self.outline_rect.size, pygame.SRCALPHA)
        self.playing, self.in_promotion_selector, self.in_result_screen = True, False, False
        self.promotion_selection_list = ['q', 'r', 'b', 'n']
        self.promotion_selection_images = {
            'w': [], 'b': [], 'r': []
        }
        self.promotion_move = None  # Stores the move if a promotion happens
        for colour in self.board.turns:  # Load images for promotion selection
            for piece in self.promotion_selection_list:
                image = pygame.image.load(f'./Assets/pieces/{colour}{piece}.png')
                self.promotion_selection_images[colour].append(image)

    def update_after_move(self, move, move_table):
        self.board.enpassant_squares[self.selected_piece.colour] = None  # Update en passant squares
        if move.move_type == "double push":
            self.board.enpassant_squares[self.selected_piece.colour] = \
                Position(move.end.segment, (move.end.square.x, move.end.square.y + 1))
        self.selected_piece.moves = []
        self.selected_piece = None
        for turn in self.board.turns:
            if turn not in self.board.checkmated_players:
                if get_game_state(self.board, turn) == "checkmate":
                    self.board.checkmated_players.append(turn)
                elif get_game_state(self.board, turn) == "stalemate":
                    self.board.stalemated_players.append(turn)
        self.board.check_winner()
        if self.board.winner is not None:
            self.in_result_screen = True
            move_table.result = f'{letter_to_colour[self.board.winner].capitalize()} wins'
        self.refresh_pieces()
        self.board.turn_index = (self.board.turn_index + 1) % len(self.board.turns)
        self.board.turn = self.board.turns[self.board.turn_index]

        if self.board.turn in self.board.stalemated_players and not self.board.turn in self.board.checkmated_players:  # If the next turn is a stalemated player
            if get_game_state(self, self.board.turn) == "stalemate":  # Check if still in stalemate
                move_table.add_move(self, None)
                self.board.turn_index = (self.board.turn_index + 1) % len(self.board.turns)
                self.board.turn = self.board.turns[self.board.turn_index]
            else:
                self.board.stalemated_players.remove(self.board.turn)
                self.refresh_pieces()
        if self.board.turn in self.board.checkmated_players:  # If the next turn is a checkmated player
            move_table.add_move(self.board, None)  # Skip the turn
            self.board.turn_index = (self.board.turn_index + 1) % len(self.board.turns)
            self.board.turn = self.board.turns[self.board.turn_index]

    def refresh_pieces(self):
        new_pieces = []
        for segment in range(3):
            for y in range(4):
                for x in range(8):
                    if self.board.position[segment][y][x] is not None:
                        piece_id = self.board.position[segment][y][x]
                        piece_polygon = Polygon(self.polygons[segment][y][x])
                        piece_pixel_pos = piece_polygon.centroid.coords[:][0]
                        if piece_id[0] in self.board.stalemated_players or piece_id[0] in self.board.checkmated_players:
                            piece_alive = False
                        else:
                            piece_alive = True
                        new_pieces.append(Piece(piece_id[0], Position(
                            segment, (x, y)), piece_pixel_pos, piece_id[1], piece_alive))
        self.pieces = new_pieces

    def handle_mouse_events(self, mouse_position, left_click, move_table):
        if self.selected_piece is not None and self.playing:
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
                    draw_thick_aapolygon(self.move_polygon_surface, (255, 255, 255), move_polygon_points, width=2)

                    if left_click:
                        self.board.update_castling_rights(move)
                        if not move.is_promotion:
                            move_table.add_move(self.board, move)
                            self.board.position = make_move(self.board, move).position  # Make the move on the board
                            self.update_after_move(move, move_table)
                        else:
                            self.playing = False
                            self.in_promotion_selector = True
                            self.promotion_move = move
                            left_click = False

        else:
            self.move_indicator_surface.fill((0, 0, 0, 0))
            self.move_polygon_surface.fill((0, 0, 0, 0))  # Fill transparent

        if self.in_promotion_selector:
            self.promotion_selector_surface.fill((0, 0, 0, 50))
            for i in range(4):  # Loop through the four y values from the promotion square in the segment
                selection_polygon_points = None
                if self.promotion_move.end.square.y == 3:
                    selection_polygon_points = \
                    self.polygons[int(self.promotion_move.end.segment)][int(self.promotion_move.end.square.y - i)][
                        int(self.promotion_move.end.square.x)]
                else:
                    if self.promotion_move.end.square.x == 7:
                        selection_polygon_points = \
                        self.polygons[int(self.promotion_move.end.segment)][int(self.promotion_move.end.square.y)][
                            int(self.promotion_move.end.square.x - i)]
                    elif self.promotion_move.end.square.x == 0:
                        selection_polygon_points = \
                        self.polygons[int(self.promotion_move.end.segment)][int(self.promotion_move.end.square.y)][
                            int(self.promotion_move.end.square.x + i)]
                pygame.draw.polygon(self.promotion_selector_surface, (100, 100, 100), selection_polygon_points)
                selection_polygon = Polygon(selection_polygon_points)
                selection_polygon_centre = selection_polygon.centroid.coords[:][0]
                selection_image = self.promotion_selection_images[self.selected_piece.colour][i]
                selection_image = pygame.transform.smoothscale(selection_image, (40, 40))
                selection_image_rect = selection_image.get_rect(center=selection_polygon_centre)
                self.promotion_selector_surface.blit(selection_image, selection_image_rect)
                point = Point(mouse_position)

                if point.within(selection_polygon):
                    draw_thick_aapolygon(self.promotion_selector_surface, (255, 255, 255), selection_polygon_points, 3)
                    if left_click:
                        self.promotion_move.promo_type = self.promotion_selection_list[i]
                        move_table.add_move(self.board, self.promotion_move)
                        self.board.position = make_move(self.board, self.promotion_move).position  # Make the move on the board
                        self.board.position[int(self.promotion_move.end.segment)][int(self.promotion_move.end.square.y)][
                            int(self.promotion_move.end.square.x)] = self.selected_piece.colour + self.promotion_move.promo_type
                        self.update_after_move(self.promotion_move, move_table)
                        self.in_promotion_selector = False
                        self.playing = True
                        break

        for piece in self.pieces:
            if piece.rect.collidepoint(mouse_position) and self.playing:
                if not piece.highlighted and piece.colour == self.board.turn:
                    piece.image = pygame.transform.smoothscale(piece.image, (60, 60))
                    piece.rect = piece.image.get_rect(center=piece.pixel_pos)
                    piece.highlighted = True
                if piece.colour == self.board.turn and left_click:
                    self.selected_piece = piece
                    self.selected_piece.moves = piece_movegen(self.board, piece.position, piece.colour)
            else:
                piece.image = piece.original_image
                piece.rect = piece.image.get_rect(center=piece.pixel_pos)
                piece.highlighted = False

        if self.in_result_screen:
            self.result_surface.fill((0, 0, 0, 50))

    def render(self, surface):
        pygame.draw.rect(surface, (70, 70, 80), self.outline_rect)
        surface.blit(self.image, self.rect)
        for piece in self.pieces:
            surface.blit(piece.image, piece.rect)

        surface.blit(self.move_polygon_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        surface.blit(self.move_indicator_surface, (0, 0))
        if self.in_promotion_selector:
            surface.blit(self.promotion_selector_surface, self.outline_rect)
        if self.in_result_screen:
            surface.blit(self.result_surface, self.outline_rect)
            pygame.draw.rect(surface, (255, 255, 255), self.result_rect, border_radius=5)
