import pygame
import pygame.freetype
from board import RenderBoard
from movetable import MoveTable
from pieces import load_piece_images

pygame.init()
pygame.display.init()
pygame.display.set_caption("3 player chess")

WIDTH, HEIGHT = 1000, 700
WINDOW = pygame.display.set_mode((1000, 700))
clock = pygame.time.Clock()


def main():
    load_piece_images()
    render_board = RenderBoard((WIDTH, HEIGHT))
    render_board.refresh_pieces()
    move_table = MoveTable((WIDTH, HEIGHT))

    bahnschrift = pygame.freetype.SysFont("bahnschrift", 20)

    left_click = False

    while True:
        clock.tick(60)
        WINDOW.fill((0, 0, 0))
        mouse_x, mouse_y = pygame.mouse.get_pos()

        render_board.handle_mouse_events((mouse_x, mouse_y), left_click, move_table)
        render_board.render(WINDOW)
        move_table.render(WINDOW)

        left_click = False

        title_surface, title_rect = bahnschrift.render("dungcatcher's 3 Player Chess", (255, 255, 255))
        title_rect.center = (render_board.outline_rect.centerx, HEIGHT * 0.05)
        WINDOW.blit(title_surface, title_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                left_click = True

        pygame.display.update()


if __name__ == "__main__":
    main()
