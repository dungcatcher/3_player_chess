import pygame
from shapely.geometry import Polygon, Point
from chess_logic.board import Board, STARTING_POSITION, letter_to_colour
from chess_logic.movegen import make_move, get_game_state, get_checkers
from chess_logic.classes import Position
from chess_logic.movegen import piece_movegen
from .polygons import compute_polygons, handle_polygon_resize, draw_thick_aapolygon
from .pieces import Piece
from .buttons import Button


def resize_board(img, section_size, position):
    scale = section_size[0] * 0.95 / img.get_width()
    img = pygame.transform.smoothscale(img, (img.get_width() * scale, img.get_height() * scale))
    rect = img.get_rect()
    rect.center = position

    return [img, rect, scale]


class RenderBoard:
    def __init__(self, screen_size):
        self.board = Board()
        self.outline_rect = pygame.Rect(0, 0, screen_size[0] * 0.7, screen_size[1])
        self.image, self.rect, self.scale = resize_board(
            pygame.image.load('Assets/board.png').convert_alpha(), self.outline_rect.size, self.outline_rect.center)
        self.original_image = self.image
        self.selected_piece = None
        self.polygons = compute_polygons()
        self.polygons = handle_polygon_resize(self.polygons, self.scale, self.rect.topleft)
        self.move_polygon_surface = pygame.Surface(screen_size, pygame.SRCALPHA)
        self.move_indicator_surface = pygame.Surface(screen_size, pygame.SRCALPHA)

        self.promotion_selector_surface = pygame.Surface(self.outline_rect.size, pygame.SRCALPHA)
        self.playing, self.in_promotion_selector, self.in_result_screen = True, False, False
        self.result_screen = None
        self.promotion_selection_list = ['q', 'r', 'b', 'n']
        self.promotion_selection_images = {
            'w': [], 'b': [], 'r': []
        }
        self.promotion_move = None  # Stores the move if a promotion happens
        for colour in self.board.turns:  # Load images for promotion selection
            for piece in self.promotion_selection_list:
                image = pygame.image.load(f'Assets/pieces/{colour}{piece}.png')
                self.promotion_selection_images[colour].append(image)

        self.move_sound = pygame.mixer.Sound("Assets/sfx/move.ogg")
        self.capture_sound = pygame.mixer.Sound("Assets/sfx/capture.ogg")
        self.check_sound = pygame.mixer.Sound("Assets/sfx/check.ogg")  # heheheha
        self.checkmate_sound = pygame.mixer.Sound("Assets/sfx/checkmate.ogg")

        self.dragging = False

    def play_sound(self, move):
        capture = False
        check = False
        checkmate = False

        if self.board.index_position(move.end) is not None or move.move_type == "enpassant":
            capture = True

        piece_colour = self.board.index_position(move.start)[0]
        new_board = make_move(self.board, move)
        for turn in self.board.turns:
            if turn != piece_colour and turn not in self.board.checkmated_players:
                if get_game_state(new_board, turn) == "checkmate":
                    checkmate = True
                elif piece_colour in get_checkers(new_board, turn):
                    check = True

        if capture:
            pygame.mixer.Sound.play(self.capture_sound)
        else:
            pygame.mixer.Sound.play(self.move_sound)

        if check:
            pygame.mixer.Sound.play(self.check_sound)
        if checkmate:
            pygame.mixer.Sound.play(self.checkmate_sound)

    def update_after_move(self, move, move_table):
        self.board.update_castling_rights(move)
        self.board.enpassant_squares[self.selected_piece.colour] = None  # Update en passant squares
        if move.move_type == "double push":
            self.board.enpassant_squares[self.selected_piece.colour] = \
                Position(move.end.segment, (move.end.square.x, move.end.square.y + 1))
        self.selected_piece.moves = []
        self.selected_piece = None
        for turn in self.board.turns:
            if turn not in self.board.checkmated_players:
                game_state = get_game_state(self.board, turn)
                if game_state == "checkmate":
                    self.board.checkmated_players.append(turn)
                elif game_state == "stalemate":
                    self.board.stalemated_players.append(turn)
        self.board.check_winner()
        if self.board.winner is not None:
            self.in_result_screen = True
            self.playing = False
            self.result_screen = ResultScreen(self)
            move_table.result = self.result_screen.get_winner_text()
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

    def reset_board(self, move_table):
        #  Reset board logic
        self.board.position = STARTING_POSITION
        self.board.turn_index = 0
        self.board.turn = self.board.turns[self.board.turn_index]
        self.board.winner = None
        self.board.stalemated_players = []
        self.board.checkmated_players = []
        self.board.castling_rights = {
            'w': {'kingside': True, 'queenside': True},
            'b': {'kingside': True, 'queenside': True},
            'r': {'kingside': True, 'queenside': True}
        }
        self.board.enpassant_squares = {  # Squares that can be taken en passant
            'w': None, 'b': None, 'r': None
        }

        self.refresh_pieces()
        self.playing = True
        self.in_result_screen = False
        move_table.moves = [[]]
        move_table.result = None
        move_table.move = 0

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

    def handle_mouse_events(self, mouse_position, events, move_table):
        left_click = False
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                left_click = True
                self.dragging = True
            if event.type == pygame.MOUSEBUTTONUP:
                self.dragging = False

        if self.selected_piece is not None and self.playing:
            if self.dragging:
                if self.selected_piece.rect.collidepoint(mouse_position):
                    self.selected_piece.rect.center = mouse_position
                    self.selected_piece.image = pygame.transform.smoothscale(self.selected_piece.original_image, (60, 60))
                    self.selected_piece.rect = self.selected_piece.image.get_rect(center=mouse_position)
            else:
                self.selected_piece.rect.center = self.selected_piece.pixel_pos
                self.selected_piece.image = pygame.transform.smoothscale(self.selected_piece.original_image, (40, 40))
                self.selected_piece.rect = self.selected_piece.image.get_rect(center=self.selected_piece.pixel_pos)

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

                    if left_click or not self.dragging:
                        if not move.is_promotion:
                            move_table.add_move(self.board, move)
                            self.play_sound(move)
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
                        self.play_sound(self.promotion_move)
                        self.board.position = make_move(self.board, self.promotion_move).position  # Make the move on the board
                        self.update_after_move(self.promotion_move, move_table)
                        self.in_promotion_selector = False
                        self.playing = True
                        break

        if self.in_result_screen:
            self.result_screen.handle_mouse_events(mouse_position, left_click, move_table)

        for piece in self.pieces:
            if piece.rect.collidepoint(mouse_position) and self.playing:
                if not piece.highlighted and piece.colour == self.board.turn and piece != self.selected_piece:
                    # piece.image = pygame.transform.smoothscale(piece.original_image, (60, 60))
                    # piece.rect = piece.image.get_rect(center=piece.pixel_pos)
                    piece.highlighted = True
                if piece.colour == self.board.turn and left_click:
                    piece.highlighted = False
                    self.selected_piece = piece
                    self.selected_piece.moves = piece_movegen(self.board, piece.position, piece.colour)
            else:
                piece.image = pygame.transform.smoothscale(piece.original_image, (40, 40))
                piece.rect = piece.image.get_rect(center=piece.pixel_pos)
                piece.highlighted = False

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
            self.result_screen.render(surface)


class ResultScreen:
    def __init__(self, render_board):
        self.render_board = render_board
        self.winner_text = self.get_winner_text()
        self.result_surface = pygame.Surface(render_board.outline_rect.size, pygame.SRCALPHA)
        self.result_rect = pygame.Rect(0, 0, render_board.outline_rect.width * 0.4, render_board.outline_rect.width * 0.6)
        self.result_rect.center = render_board.outline_rect.center
        self.result_title_rect = pygame.Rect(self.result_rect.left, self.result_rect.top, self.result_rect.width, self.result_rect.height * 0.15)
        self.title_font = pygame.freetype.Font('Assets/BAHNSCHRIFT.TTF', 36)
        self.restart_button = Button((255, 255, 255),
                                     (self.result_rect.centerx, self.result_rect.top + self.result_rect.height * 0.3),
                                     (self.result_rect.width * 0.6, self.result_rect.height * 0.1),
                                     'Restart?')

    def get_winner_text(self):
        winner_word = letter_to_colour[self.render_board.board.winner]
        winner_text = winner_word.capitalize() + ' wins!'
        return winner_text

    def handle_mouse_events(self, mouse_position, left_click, move_table):
        if self.restart_button.mouse_over(mouse_position) and left_click:
            self.render_board.reset_board(move_table)

    def render(self, surface):
        self.result_surface.fill((0, 0, 0, 50))
        surface.blit(self.result_surface, self.render_board.outline_rect)
        pygame.draw.rect(surface, (200, 200, 220), self.result_rect, border_radius=5)
        pygame.draw.rect(surface, (60, 60, 60), self.result_title_rect, border_top_left_radius=5, border_top_right_radius=5)

        result_title_surface, result_title_rect = self.title_font.render(self.winner_text, (255, 255, 255))
        result_title_rect.center = self.result_title_rect.center
        surface.blit(result_title_surface, result_title_rect)

        self.restart_button.render(surface)
