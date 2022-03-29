import pygame


class Piece:
    def __init__(self, colour, position, pixel_pos, identifier):
        self.colour = colour
        self.position = position  # Board position
        self.pixel_pos = pixel_pos
        self.image = pygame.image.load(f'./Assets/pieces/{colour}{identifier}.png').convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (45, 45))
        self.original_image = self.image
        self.rect = self.image.get_rect(center=pixel_pos)
        self.highlighted = False
