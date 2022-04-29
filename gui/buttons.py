import pygame
import pygame.freetype


class Button:
    def __init__(self, colour, pos, size, text, outline=True):
        self.colour = colour
        self.outline_colour = (0, 0, 0)
        self.rect = pygame.Rect(0, 0, size[0], size[1])
        self.rect.center = pos
        self.text = text
        self.font = pygame.freetype.Font('Assets/BAHNSCHRIFT.TTF', 16)
        self.outline = outline

    def mouse_over(self, mouse_position):
        if self.rect.collidepoint(mouse_position):
            return True
        return False

    def render(self, surface):
        pygame.draw.rect(surface, self.colour, self.rect)
        if self.outline:
            pygame.draw.rect(surface, self.colour, self.rect)

        text_surface, text_rect = self.font.render(self.text, (0, 0, 0))
        text_rect.center = self.rect.center
        surface.blit(text_surface, text_rect)
