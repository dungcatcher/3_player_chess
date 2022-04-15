import pygame
import pygame.freetype
from movegen import piece_movegen, get_game_state
from board import Board
from pieces import Piece
from classes import Position, Move
from shapely.geometry import Point, Polygon

pygame.init()
pygame.display.init()

WIDTH, HEIGHT = 1000, 700
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))

clock = pygame.time.Clock()


def refresh_pieces(board, board_polygons):
    pieces = []
    for segment in range(3):
        for y in range(4):
            for x in range(8):
                if board[segment][y][x] is not None:
                    piece_id = board[segment][y][x]
                    piece_polygon = Polygon(board_polygons[segment][y][x])
                    piece_pixel_pos = piece_polygon.centroid.coords[:][0]
                    pieces.append(Piece(piece_id[0], Position(
                        segment, (x, y)), piece_pixel_pos, piece_id[1]))

    return pieces


def main():
    board = Board((WIDTH, HEIGHT), (WIDTH // 2, HEIGHT // 2))
    pieces = refresh_pieces(board.position, board.polygons)

    bahnschrift = pygame.freetype.SysFont("bahnschrift", 20)

    left_click = False
    selected_piece = None
    selected_piece_moves = []
    piece_moved = False

    turns = ["w", "b", "r"]
    turn_index = 0
    current_turn = turns[turn_index]

    while True:
        clock.tick(60)
        WINDOW.fill((255, 255, 255))
        WINDOW.blit(board.image, board.rect)

        mouse_x, mouse_y = pygame.mouse.get_pos()

        if selected_piece is not None:
            for move in selected_piece_moves:
                move_polygon_points = board.polygons[int(
                    move.end.segment)][int(move.end.square.y)][int(move.end.square.x)]
                move_polygon = Polygon(move_polygon_points)
                move_pixel_pos = move_polygon.centroid.coords[:][0]
                pygame.draw.circle(WINDOW, (255, 0, 0), move_pixel_pos, 10)

                point = Point((mouse_x, mouse_y))
                if point.within(move_polygon):
                    pygame.draw.polygon(
                        WINDOW, (255, 255, 255), move_polygon_points, width=5)

                    if left_click:
                        if move.promo_type is None:
                            board.position[int(move.end.segment)][int(move.end.square.y)][int(move.end.square.x)] = \
                                board.position[  # Set move square to selected piece
                                    int(selected_piece.segment)][int(selected_piece.square.y)][
                                    int(selected_piece.square.x)]
                        else:
                            print('l')
                            board.position[int(move.end.segment)][int(move.end.square.y)][int(move.end.square.x)] = \
                                f'{board.position[int(selected_piece.segment)][int(selected_piece.square.y)][int(selected_piece.square.x)][0]}q'
                        board.position[int(selected_piece.segment)][int(selected_piece.square.y)][
                            int(selected_piece.square.x)] = None

                        pieces = refresh_pieces(board.position, board.polygons)
                        selected_piece = None
                        piece_moved = True
                        selected_piece_moves = []
                        turn_index = (turn_index + 1) % 3
                        current_turn = turns[turn_index]

        for piece in pieces:
            WINDOW.blit(piece.image, piece.rect)

            if piece.rect.collidepoint((mouse_x, mouse_y)):
                if not piece.highlighted:
                    piece.image = pygame.transform.smoothscale(piece.image, (60, 60))
                    piece.rect = piece.image.get_rect(center=piece.pixel_pos)
                    piece.highlighted = True

                if left_click and not piece_moved and piece.colour == current_turn:
                    selected_piece = piece.position
                    selected_piece_moves = piece_movegen(board.position, piece.position, piece.colour)
            else:
                piece.image = piece.original_image
                piece.rect = piece.image.get_rect(center=piece.pixel_pos)
                piece.highlighted = False

        left_click = False
        piece_moved = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                left_click = True

        pygame.display.update()


main()
