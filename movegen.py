from typing import List, Union
from classes import *
from copy import deepcopy


def make_move(board, move: Move):
    new_board = deepcopy(board)
    piece_id = board[int(move.start.segment)][int(move.start.square.y)][int(move.start.square.x)]  # Get piece id of piece
    new_board[int(move.end.segment)][int(move.end.square.y)][int(move.end.square.x)] = piece_id  # Set target square to that id
    new_board[int(move.start.segment)][int(move.start.square.y)][int(move.start.square.x)] = None  # Remove starting piece id

    return new_board


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


def in_check(board, colour):
    king_pos = None
    for segment in range(3):
        for y in range(4):
            for x in range(8):
                #  Find king of specified colour
                if board[segment][y][x] is not None and board[segment][y][x] == f'{colour}k':
                    king_pos = Position(segment, (x, y))

    # Pawn check
    for move in pawn_movegen(board, king_pos, colour, only_captures=True, filter_legal=False):
        move_piece = board[int(move.end.segment)][int(move.end.square.y)][int(move.end.square.x)]
        if move_piece is not None:
            if move_piece[0] != colour and move_piece[1] == "p":
                return True

    # Knight check
    for move in knight_movegen(board, king_pos, colour, filter_legal=False):
        move_piece = board[int(move.end.segment)][int(move.end.square.y)][int(move.end.square.x)]
        if move_piece is not None:
            if move_piece[0] != colour and move_piece[1] == "n":
                return True

    # Bishop check
    for move in bishop_movegen(board, king_pos, colour, filter_legal=False):
        move_piece = board[int(move.end.segment)][int(move.end.square.y)][int(move.end.square.x)]
        if move_piece is not None:
            if move_piece[0] != colour and move_piece[1] == "b":
                return True

    # Rook check
    for move in rook_movegen(board, king_pos, colour, filter_legal=False):
        move_piece = board[int(move.end.segment)][int(move.end.square.y)][int(move.end.square.x)]
        if move_piece is not None:
            if move_piece[0] != colour and move_piece[1] == "r":
                return True

    # Queen check
    for move in queen_movegen(board, king_pos, colour, filter_legal=False):
        move_piece = board[int(move.end.segment)][int(move.end.square.y)][int(move.end.square.x)]
        if move_piece is not None:
            if move_piece[0] != colour and move_piece[1] == "q":
                return True

    # King check
    for move in king_movegen(board, king_pos, colour, filter_legal=False):
        move_piece = board[int(move.end.segment)][int(move.end.square.y)][int(move.end.square.x)]
        if move_piece is not None:
            if move_piece[0] != colour and move_piece[1] == "k":
                return True

    return False


def get_game_state(board, colour):  # Checks for checkmate, stalemate or still playing
    # Search for all pieces of the same colour
    for segment in range(3):
        for y in range(4):
            for x in range(8):
                square_occupant = board[segment][y][x]
                if square_occupant is not None and square_occupant[0] == colour:
                    if piece_movegen(board, Position(segment, (x, y)), colour):  # There is a legal move so not in checkmate
                        return "playing"
                    else:
                        if in_check(board, colour):
                            return "checkmate"
                        else:
                            return "stalemate"


def legal_movegen(board, moves, colour):
    legal_moves = []
    for move in moves:
        new_board = make_move(board, move)
        if not in_check(new_board, colour):
            legal_moves.append(move)

    return legal_moves


colour_to_segment = {
    "w": 0,
    "b": 1,
    "r": 2
}


def pawn_movegen(board, position, colour, only_captures=False, filter_legal=True):
    pseudo_moves = []

    capture_vectors = [[-1, -1], [1, -1]]
    if position.square.y == 2 and position.segment == colour_to_segment[colour]:
        vectors = [[0, -1], [0, -2]]
    else:
        if colour_to_segment[colour] == position.segment:
            vectors = [[0, -1]]
        else:
            vectors = [[0, 1]]
            capture_vectors = [[-1, 1], [1, 1]]

    if not only_captures:
        for vector in vectors:
            for position_to_check in vector_to_position(position, vector):
                if position_to_check is not None:
                    square_occupant = board[int(position_to_check.segment)][int(
                        position_to_check.square.y)][int(position_to_check.square.x)]
                    if square_occupant is None:
                        if colour_to_segment[colour] != position_to_check.segment and position_to_check.square.y == 3:
                            pseudo_moves.append(Move(position, position_to_check, promo_type='q'))
                        else:
                            pseudo_moves.append(Move(position, position_to_check))

    for capture_vector in capture_vectors:
        for position_to_check in vector_to_position(position, capture_vector):
            if position_to_check:
                square_occupant = board[int(position_to_check.segment)][int(
                    position_to_check.square.y)][int(position_to_check.square.x)]
                if square_occupant is not None and square_occupant[0] != colour:
                    if colour_to_segment[colour] != position_to_check.segment and position_to_check.square.y == 3:
                        pseudo_moves.append(Move(position, position_to_check, promo_type='q'))
                    else:
                        pseudo_moves.append(Move(position, position_to_check))

    if filter_legal:
        legal_moves = legal_movegen(board, pseudo_moves, colour)
        return legal_moves

    return pseudo_moves


def knight_movegen(board, position, colour, filter_legal=True):
    pseudo_moves = []
    vectors = [[-1, -2], [1, -2], [2, -1], [2, 1],
               [1, 2], [-1, 2], [-2, 1], [-2, -1]]

    for vector in vectors:
        for position_to_check in vector_to_position(position, vector):
            if position_to_check:
                square_occupant = board[int(position_to_check.segment)][int(
                    position_to_check.square.y)][int(position_to_check.square.x)]
                if square_occupant is None:
                    pseudo_moves.append(Move(position, position_to_check))
                else:
                    if square_occupant[0] != colour:
                        pseudo_moves.append(Move(position, position_to_check))

    if filter_legal:
        legal_moves = legal_movegen(board, pseudo_moves, colour)
        return legal_moves

    return pseudo_moves


def bishop_movegen(board, position, colour, filter_legal=True):
    pseudo_moves = []
    vectors = [[-1, -1], [1, -1], [1, 1], [-1, 1]]

    for vector in vectors:
        for end_position in iterate_move(board, position, vector, colour):
            pseudo_moves.append(Move(position, end_position))

    if filter_legal:
        legal_moves = legal_movegen(board, pseudo_moves, colour)
        return legal_moves

    return pseudo_moves


def iterate_move(board, position, vector, colour):
    end_position = []
    new_positions = vector_to_position(position, vector)
    for position_to_check in new_positions:
        if position_to_check is not None:
            square_occupant = board[int(position_to_check.segment)][int(
                position_to_check.square.y)][int(position_to_check.square.x)]
            if square_occupant is None:
                end_position.append(position_to_check)
                end_position += iterate_move(board, position_to_check, vector if position_to_check.segment ==
                                      position.segment else [-vector[0], -vector[1]], colour)
            elif square_occupant[0] != colour:
                end_position.append(position_to_check)

    return end_position


def rook_movegen(board, position, colour, filter_legal=True):
    pseudo_moves = []
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
                    square_occupant = board[int(position_to_check.segment)][int(position_to_check.square.y)][
                        int(position_to_check.square.x)]
                    if square_occupant is None:
                        pseudo_moves.append(Move(position, position_to_check))
                        new_position = position_to_check
                    else:
                        if square_occupant[0] != colour:
                            pseudo_moves.append(Move(position, position_to_check))
                            valid_move = False
                        else:
                            valid_move = False
                else:
                    valid_move = False

    if filter_legal:
        legal_moves = legal_movegen(board, pseudo_moves, colour)
        return legal_moves

    return pseudo_moves


def queen_movegen(board, position, colour, filter_legal=True):
    pseudo_moves = bishop_movegen(board, position, colour, filter_legal) + rook_movegen(board, position, colour, filter_legal)

    if filter_legal:
        legal_moves = legal_movegen(board, pseudo_moves, colour)
        return legal_moves

    return pseudo_moves


def king_movegen(board, position, colour, filter_legal=True):
    pseudo_moves = []
    vectors = [[-1, -1], [0, -1], [1, -1],
               [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0]]

    for vector in vectors:
        for position_to_check in vector_to_position(position, vector):
            if position_to_check:
                square_occupant = board[int(position_to_check.segment)][int(
                    position_to_check.square.y)][int(position_to_check.square.x)]
                if square_occupant is None:
                    pseudo_moves.append(Move(position, position_to_check))
                else:
                    if square_occupant[0] != colour:
                        pseudo_moves.append(Move(position, position_to_check))

    # if castling_rights[colour]['kingside']:
    #     can_kingside_castle = True
    #     for i in range(3):
    #         if i != 0:  # Don't check own square for blockades
    #             if board[int(position.segment)][int(position.square.y)][int(position.square.x + i)] is not None:
    #                 can_kingside_castle = False
    #                 break
    #         test_move = Move(position, Position(position.segment, (position.square.x + i, position.square.y)))
    #         new_board = make_move(board, test_move)
    #         if in_check(new_board, colour):
    #             can_kingside_castle = False
    #             break
    #     if can_kingside_castle:
    #         castle_move = Move(position, Position(position.segment, (position.square.x + 2, position.square.y)), move_type='kingside castle')
    #         pseudo_moves.append(castle_move)

    if filter_legal:
        legal_moves = legal_movegen(board, pseudo_moves, colour)
        return legal_moves

    return pseudo_moves


def piece_movegen(board, position, colour):
    piece_id = board[int(position.segment)][int(
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
