"""TODO: Make vector_to_position code not garbage"""
from position import *


def direction_to_square(position, vector):
    new_square = position.square + Vector2(vector)
    new_segment = position.segment
    if 0 <= new_square.y <= 3:
        if 0 <= new_square.x <= 7:
            return Position(new_segment, new_square)
        else:
            return None
    else:
        if new_square.y < 0:  # Goes above the segment
            if 0 <= new_square.x <= 3:
                new_segment = (position.segment - 1) % 3
                new_square = [7 - position.square.x - vector[0], position.square.y - vector[1] - 1]
                return Position(new_segment, new_square)
            elif 4 <= new_square[0] <= 7:
                new_segment = (position.segment + 1) % 3
                new_square = [7 - position.square.x - vector[0], position.square.y - vector[1] - 1]
                return Position(new_segment, new_square)
            else:
                return None
        else:  # Below the segment (off the board)
            return None


def vector_to_position(position, vector):
    xy_first_position = direction_to_square(position, [vector[0], 0])
    xy_final_position = None
    if xy_first_position:
        xy_final_position = direction_to_square(xy_first_position, [0, vector[1]])

    yx_first_position = direction_to_square(position, [0, vector[1]])
    yx_final_position = None
    if yx_first_position:
        if yx_first_position.segment != position.segment:  # Direction changes with new segment
            yx_final_position = direction_to_square(yx_first_position, [-vector[0], 0])
        else:
            yx_final_position = direction_to_square(yx_first_position, [vector[0], 0])

    if xy_final_position == yx_final_position:
        positions = [xy_final_position]
    else:
        positions = [xy_final_position, yx_final_position]

    return positions


def pawn_movegen(board, position, colour):
    moves = []

    if position.square.y == 2:
        vectors = [[0, -1], [0, -2]]
    else:
        vectors = [[0, -1]]
    capture_vectors = [[-1, -1], [1, -1]]

    for vector in vectors:
        for position_to_check in vector_to_position(position, vector):
            if position_to_check is not None:
                square_occupant = board.position[int(position_to_check.segment)][int(position_to_check.square.y)][int(position_to_check.square.x)]
                if square_occupant is None:
                    moves.append(position_to_check)

    for capture_vector in capture_vectors:
        for position_to_check in vector_to_position(position, capture_vector):
            if position_to_check:
                square_occupant = board.position[int(position_to_check.segment)][int(position_to_check.square.y)][int(position_to_check.square.x)]
                if square_occupant is not None and square_occupant[0] != colour:
                    moves.append(position_to_check)

    return moves


def knight_movegen(board, position, colour):
    moves = []
    vectors = [[-1, -2], [1, -2], [2, -1], [2, 1], [1, 2], [-1, 2], [-2, 1], [-2, -1]]

    for vector in vectors:
        for position_to_check in vector_to_position(position, vector):
            if position_to_check:
                square_occupant = board.position[int(position_to_check.segment)][int(position_to_check.square.y)][int(position_to_check.square.x)]
                if square_occupant is None:
                    moves.append(position_to_check)
                else:
                    if square_occupant[0] != colour:
                        moves.append(position_to_check)

    return moves


# def bishop_movegen(board, square, colour, segment):
#     moves = []
#     vectors = [[-1, -1], [1, -1], [1, 1], [-1, 1]]
#
#     for vector in vectors:
#         new_square = square
#         new_segment = segment
#         while True:
#             for position in vector_to_position(new_square, new_segment, vector):
#                 if position:
#                     new_segment, square_to_check = position
#                     square_occupant = board.position[new_segment][square_to_check[1]][square_to_check[0]]
#                     if square_occupant is None:
#                         moves.append([new_segment, square_to_check])
#                     else:
#                         if square_occupant[0] != colour:
#                             moves.append([new_segment, square_to_check])
#                             break
#                         else:
#                             break
#                 else:
#                     break


def piece_movegen(board, position, colour):
    piece_id = board.position[int(position.segment)][int(position.square.y)][int(position.square.x)][1]
    if piece_id == 'p':
        return pawn_movegen(board, position, colour)
    elif piece_id == 'n':
        return knight_movegen(board, position, colour)
    else:
        return []
