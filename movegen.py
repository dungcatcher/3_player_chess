"""TODO: Make vector_to_position code not garbage"""
import re
from sys import api_version
from typing import List, Union
from position import *


def direction_to_square(position: Position, vector):
    new_square = position.square + Vector2(vector)
    new_segment = position.segment
    if 0 <= new_square.y <= 3:
        if 0 <= new_square.x <= 7:
            return Position(new_segment, new_square)
        else:
            return None
    else:
        if new_square.y < 0:  # Goes above the segment
            if 0 <= new_square.x <= 3:  # Goes to the left upper segment
                new_segment = (position.segment - 1) % 3
                new_square = [7 - position.square.x - vector[0],
                              abs(new_square.y) - 1]
                return Position(new_segment, new_square)
            elif 4 <= new_square.x <= 7:  # Goes to the right upper segment
                new_segment = (position.segment + 1) % 3
                new_square = [7 - position.square.x - vector[0],
                              abs(new_square.y) - 1]
                return Position(new_segment, new_square)
            # Goes past the end of the segment to the right or left (off the board)
            else:
                return None
        else:  # Below the segment (off the board)
            return None


def positions_are_same(p1: Position, p2: Position):
    if p1 and p2\
            and p1.segment == p2.segment\
            and p1.square.x == p2.square.x\
            and p1.square.y == p2.square.y:
        return True
    return False


def vector_to_position(position: Position, vector: List[float]):
    first_pos: List[Union[Position, None]] = [None, None]
    end_pos: List[Union[Position, None]] = [None, None]

    for i in range(2):
        vec_to_check = [0, 0]
        vec_to_check[i] = vector[i]
        first_pos[i] = (direction_to_square(position, vec_to_check))

        if first_pos[i]:
            vec_to_check = [0, 0]
            second_index = (i + 1) % 2
            if position.segment == first_pos[i].segment:
                vec_to_check[second_index] = vector[second_index]
            else:
                vec_to_check[second_index] = -vector[second_index]
            end_pos[i] = (direction_to_square(
                first_pos[i], vec_to_check))

    if positions_are_same(end_pos[0], end_pos[1]):
        return [end_pos[0]]
    else:
        return end_pos

colour_to_segment = {
    "w": 0,
    "b": 1,
    "r": 2
}


def pawn_movegen(board, position, colour):
    moves = []

    capture_vectors = [[-1, -1], [1, -1]]
    if position.square.y == 2 and position.segment == colour_to_segment[colour]:
        vectors = [[0, -1], [0, -2]]
    else:
        if colour_to_segment[colour] == position.segment:
            vectors = [[0, -1]]
        else:
            vectors = [[0, 1]]
            capture_vectors = [[-1, 1], [1, 1]]

    for vector in vectors:
        for position_to_check in vector_to_position(position, vector):
            if position_to_check is not None:
                square_occupant = board.position[int(position_to_check.segment)][int(
                    position_to_check.square.y)][int(position_to_check.square.x)]
                if square_occupant is None:
                    moves.append(position_to_check)

    for capture_vector in capture_vectors:
        for position_to_check in vector_to_position(position, capture_vector):
            if position_to_check:
                square_occupant = board.position[int(position_to_check.segment)][int(
                    position_to_check.square.y)][int(position_to_check.square.x)]
                if square_occupant is not None and square_occupant[0] != colour:
                    moves.append(position_to_check)

    return moves


def knight_movegen(board, position, colour):
    moves = []
    vectors = [[-1, -2], [1, -2], [2, -1], [2, 1],
               [1, 2], [-1, 2], [-2, 1], [-2, -1]]

    for vector in vectors:
        for position_to_check in vector_to_position(position, vector):
            if position_to_check:
                square_occupant = board.position[int(position_to_check.segment)][int(
                    position_to_check.square.y)][int(position_to_check.square.x)]
                if square_occupant is None:
                    moves.append(position_to_check)
                else:
                    if square_occupant[0] != colour:
                        moves.append(position_to_check)
    return moves


def bishop_movegen(board, position, colour):
    moves = []
    vectors = [[-1, -1], [1, -1], [1, 1], [-1, 1]]

    for vector in vectors:
        moves += iterate_move(board, position, vector, colour)
    return moves


def iterate_move(board, position, vector, colour):
    moves = []
    new_positions = vector_to_position(position, vector)
    for position_to_check in new_positions:
        if position_to_check is not None:
            square_occupant = board.position[int(position_to_check.segment)][int(
                position_to_check.square.y)][int(position_to_check.square.x)]
            if square_occupant is None:
                moves.append(position_to_check)
                moves += iterate_move(board, position_to_check, vector if position_to_check.segment ==
                                      position.segment else [-vector[0], -vector[1]], colour)
            elif square_occupant[0] != colour:
                moves.append(position_to_check)
    return moves


def rook_movegen(board, position, colour):
    moves = []
    vectors = [[0, -1], [0, 1], [1, 0], [-1, 0]]

    for vector in vectors:
        valid_move = True
        new_position = position
        new_vector = vector
        while valid_move:
            for position_to_check in vector_to_position(new_position, new_vector):
                if position_to_check:
                    if position_to_check.segment != position.segment:  # Vector changes when segment changes
                        new_vector = [-vector[0], -vector[1]]
                    square_occupant = board.position[int(position_to_check.segment)][int(position_to_check.square.y)][
                        int(position_to_check.square.x)]
                    if square_occupant is None:
                        moves.append(position_to_check)
                        new_position = position_to_check
                    else:
                        if square_occupant[0] != colour:
                            moves.append(position_to_check)
                            valid_move = False
                        else:
                            valid_move = False
                else:
                    valid_move = False

    return moves


def queen_movegen(board, position, colour):
    moves = bishop_movegen(board, position, colour) + \
        rook_movegen(board, position, colour)

    return moves


def king_movegen(board, position, colour):
    moves = []
    vectors = [[-1, -1], [0, -1], [1, -1],
               [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0]]

    for vector in vectors:
        for position_to_check in vector_to_position(position, vector):
            if position_to_check:
                square_occupant = board.position[int(position_to_check.segment)][int(
                    position_to_check.square.y)][int(position_to_check.square.x)]
                if square_occupant is None:
                    moves.append(position_to_check)
                else:
                    if square_occupant[0] != colour:
                        moves.append(position_to_check)

    return moves


def piece_movegen(board, position, colour):
    piece_id = board.position[int(position.segment)][int(
        position.square.y)][int(position.square.x)][1]
    if piece_id == 'p':
        return pawn_movegen(board, position, colour)
    elif piece_id == 'n':
        return knight_movegen(board, position, colour)
    elif piece_id == 'b':
        return bishop_movegen(board, position, colour)
    elif piece_id == 'r':
        return rook_movegen(board, position, colour)
    elif piece_id == 'q':
        return queen_movegen(board, position, colour)
    elif piece_id == 'k':
        return king_movegen(board, position, colour)
