from pygame import Vector2


class Position:
    def __init__(self, segment, square):
        self.segment = segment
        self.square = Vector2(square)


class Move:
    def __init__(self, start, end, move_type="normal", is_promotion=False, promo_type=None):
        self.start = start
        self.end = end
        self.move_type = move_type
        self.is_promotion = is_promotion
        self.promo_type = promo_type
