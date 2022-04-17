import pygame
import pygame.freetype
from movegen import piece_movegen, get_game_state
from board import Board
from movetable import MoveTable, move_to_notation
from shapely.geometry import Point, Polygon

pygame.init()
pygame.display.init()
pygame.display.set_caption("3 player chess")

WIDTH, HEIGHT = 1000, 700
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


def main():
    board_segment_rect = pygame.Rect(0, 0, WIDTH * 0.7, HEIGHT)
    board = Board(board_segment_rect.size, board_segment_rect.center)
    move_table = MoveTable((WIDTH, HEIGHT))
    pieces = board.refresh_pieces()

    bahnschrift = pygame.freetype.SysFont("bahnschrift", 20)

    left_click = False
    selected_piece = None
    selected_piece_moves = []
    piece_moved = False

    while True:
        clock.tick(60)
        WINDOW.fill((0, 0, 0))
        pygame.draw.rect(WINDOW, (70, 70, 80), board_segment_rect)
        WINDOW.blit(board.image, board.rect)
        move_table.render(WINDOW)

        mouse_x, mouse_y = pygame.mouse.get_pos()

        if selected_piece is not None:
            for move in selected_piece_moves:
                move_polygon_points = board.polygons[int(
                    move.end.segment)][int(move.end.square.y)][int(move.end.square.x)]
                move_polygon = Polygon(move_polygon_points)
                move_pixel_pos = move_polygon.centroid.coords[:][0]
                pygame.draw.circle(WINDOW, (255, 0, 0), move_pixel_pos, 8)

                point = Point((mouse_x, mouse_y))
                if point.within(move_polygon):
                    pygame.draw.polygon(
                        WINDOW, (255, 255, 255), move_polygon_points, width=5)

                    if left_click:
                        move_table.add_move(move, board.position)
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

                        pieces = board.refresh_pieces()
                        selected_piece = None
                        piece_moved = True
                        selected_piece_moves = []
                        board.turn_index = (board.turn_index + 1) % 3
                        board.turn = board.turns[board.turn_index]

        for piece in pieces:
            WINDOW.blit(piece.image, piece.rect)

            if piece.rect.collidepoint((mouse_x, mouse_y)):
                if not piece.highlighted:
                    piece.image = pygame.transform.smoothscale(piece.image, (60, 60))
                    piece.rect = piece.image.get_rect(center=piece.pixel_pos)
                    piece.highlighted = True

                if left_click and not piece_moved and piece.colour == board.turn:
                    selected_piece = piece.position
                    selected_piece_moves = piece_movegen(board.position, piece.position, piece.colour)
            else:
                piece.image = piece.original_image
                piece.rect = piece.image.get_rect(center=piece.pixel_pos)
                piece.highlighted = False

        left_click = False
        piece_moved = False

        title_surface, title_rect = bahnschrift.render("dungcatcher's 3 Player Chess", (255, 255, 255))
        title_rect.center = (board_segment_rect.centerx, HEIGHT * 0.05)
        WINDOW.blit(title_surface, title_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                left_click = True

        pygame.display.update()


main()
