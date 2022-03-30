from typing import List
import pygame
import pygame.freetype
from movegen import *
from board import *
from polygons import *
from pieces import *
from position import *
from shapely.geometry import Point, Polygon
from config import *

pygame.init()
pygame.display.init()

clock = pygame.time.Clock()


def main():
    board = Board()
    board_img = pygame.image.load('./Assets/board.png').convert_alpha()
    board_scale = HEIGHT / board_img.get_height()
    board_img = pygame.transform.smoothscale(board_img, (board_img.get_width(
    ) * board_scale, board_img.get_height() * board_scale))
    board_rect = board_img.get_rect()
    board_rect.center = WIDTH // 2, HEIGHT // 2
    margin = (WIDTH - board_rect.width) / 2

    board_polygons = compute_polygons()
    board_polygons = handle_polygon_resize(board_polygons, board_scale, margin)

    pieces: List[Piece] = []
    for segment in range(3):
        for y in range(4):
            for x in range(8):
                if board.position[segment][y][x] is not None:
                    piece_id = board.position[segment][y][x]
                    piece_polygon = Polygon(board_polygons[segment][y][x])
                    piece_pixel_pos = piece_polygon.centroid.coords[:][0]
                    pieces.append(Piece(piece_id[0], Position(
                        segment, (x, y)), piece_pixel_pos, piece_id[1]))

    bahnschrift = pygame.freetype.SysFont("bahnschrift", 20)

    left_click = False
    selected_piece = None
    selected_piece_moves = []
    piece_highlighted = False

    while True:
        clock.tick(60)
        WINDOW.fill((255, 255, 255))
        WINDOW.blit(board_img, board_rect)

        mouse_x, mouse_y = pygame.mouse.get_pos()

        piece: Piece
        for piece in pieces:
            WINDOW.blit(piece.image, piece.rect)

            if piece.rect.collidepoint((mouse_x, mouse_y)):
                if not piece.highlighted:
                    piece.image = pygame.transform.smoothscale(
                        piece.image, (60, 60))
                    piece.rect = piece.image.get_rect(center=piece.pixel_pos)
                    piece.highlighted = True

                if left_click:
                    selected_piece = piece.position
                    selected_piece_moves = piece_movegen(
                        board, piece.position, piece.colour)
            else:
                piece.image = piece.original_image
                piece.rect = piece.image.get_rect(center=piece.pixel_pos)
                piece.highlighted = False

        if selected_piece is not None:
            for move in selected_piece_moves:
                move_polygon_points = board_polygons[int(
                    move.segment)][int(move.square.y)][int(move.square.x)]
                move_polygon = Polygon(move_polygon_points)
                move_pixel_pos = move_polygon.centroid.coords[:][0]
                pygame.draw.circle(WINDOW, (255, 0, 0), move_pixel_pos, 10)

                point = Point((mouse_x, mouse_y))
                if point.within(move_polygon):
                    pygame.draw.polygon(
                        WINDOW, (255, 255, 255), move_polygon_points, width=5)

        left_click = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                left_click = True

        pygame.display.update()


main()
