"""TODO: Don't use globals in load_piece_images"""

import pygame

piece_image_map = {
    'w': {},
    'b': {},
    'r': {},
    'g': {}
}


def load_piece_images():
    global piece_image_map

    piece_ids = ['p', 'n', 'b', 'r', 'q', 'k']
    for colour in piece_image_map.keys():
        for piece_id in piece_ids:
            image = pygame.image.load(f'./Assets/pieces/{colour + piece_id}.png').convert_alpha()
            image = pygame.transform.smoothscale(image, (40, 40))
            piece_image_map[colour][piece_id] = image


class Piece:
    def __init__(self, colour, position, pixel_pos, identifier, alive=True):
        self.colour = colour
        self.position = position  # Board position
        self.pixel_pos = pixel_pos
        if alive:
            self.image = piece_image_map[colour][identifier]
        else:
            self.image = piece_image_map['g'][identifier]
        self.original_image = self.image
        self.image = pygame.transform.smoothscale(self.image, (40, 40))
        self.rect = self.image.get_rect(center=pixel_pos)
        self.highlighted = False
        self.moves = []
