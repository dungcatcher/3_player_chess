from pygame import Vector2


class Position:
    def __init__(self, segment, square):
        self.segment = segment
        self.square = Vector2(square)
