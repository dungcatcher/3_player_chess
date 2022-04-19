import pygame
import pygame.freetype
from board import Board
from movetable import MoveTable

pygame.init()
pygame.display.init()
pygame.display.set_caption("3 player chess")

WIDTH, HEIGHT = 1000, 700
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


def main():
    board = Board((WIDTH, HEIGHT))
    board.refresh_pieces()
    move_table = MoveTable((WIDTH, HEIGHT))

    bahnschrift = pygame.freetype.SysFont("bahnschrift", 20)

    left_click = False

    while True:
        clock.tick(60)
        WINDOW.fill((0, 0, 0))
        mouse_x, mouse_y = pygame.mouse.get_pos()

        WINDOW.blit(board.image, board.rect)
        board.render(WINDOW, left_click, (mouse_x, mouse_y), move_table)
        move_table.render(WINDOW)

        left_click = False

        title_surface, title_rect = bahnschrift.render("dungcatcher's 3 Player Chess", (255, 255, 255))
        title_rect.center = (board.outline_rect.centerx, HEIGHT * 0.05)
        WINDOW.blit(title_surface, title_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                left_click = True

        pygame.display.update()


main()
