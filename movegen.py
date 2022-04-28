from pygame import Vector2
from typing import List, Union
from classes import Move, Position
from copy import copy, deepcopy


def make_move(board, move):
    new_board_position = deepcopy(board.position)
    piece_id = board.index_position(move.start)
    new_board_position[int(move.end.segment)][int(move.end.square.y)][int(move.end.square.x)] = piece_id  # Set target square to that id
    if move.move_type == "kingside castle":
        new_board_position[int(move.start.segment)][3][5] = f'{piece_id[0]}r'  # Move the rook
        new_board_position[int(move.end.segment)][3][7] = None
    elif move.move_type == "queenside castle":
        new_board_position[int(move.start.segment)][3][3] = f'{piece_id[0]}r'
        new_board_position[int(move.end.segment)][3][0] = None
    elif move.move_type == "enpassant":
        new_board_position[int(move.end.segment)][int(move.end.square.y - 1)][int(move.end.square.x)] = None

    new_board_position[int(move.start.segment)][int(move.start.square.y)][int(move.start.square.x)] = None  # Remove starting piece id

    new_board = copy(board)
    new_board.position = new_board_position

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
    if p1 and p2 \
            and p1.segment == p2.segment \
            and p1.square.x == p2.square.x \
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


def get_checkers(board, colour):  # Check for teams checking a colour's king
    checkers = []

    king_pos = None
    for segment in range(3):
        for y in range(4):
            for x in range(8):
                #  Find king of specified colour
                if board.position[segment][y][x] is not None and board.position[segment][y][x] == f'{colour}k':
                    king_pos = Position(segment, (x, y))

    # Pawn check
    for move in pawn_movegen(board, king_pos, colour, only_captures=True, filter_legal=False):
        move_piece = board.position[int(move.end.segment)][int(move.end.square.y)][int(move.end.square.x)]
        if move_piece is not None:
            if move_piece[0] != colour and move_piece[0] not in board.checkmated_players and \
                    move_piece[0] not in board.stalemated_players and move_piece[1] == "p":
                if move_piece[0] not in checkers:
                    checkers.append(move_piece[0])

    # Knight check
    for move in knight_movegen(board, king_pos, colour, filter_legal=False):
        move_piece = board.position[int(move.end.segment)][int(move.end.square.y)][int(move.end.square.x)]
        if move_piece is not None:
            if move_piece[0] != colour and move_piece[0] not in board.checkmated_players and \
                    move_piece[0] not in board.stalemated_players and move_piece[1] == "n":
                if move_piece[0] not in checkers:
                    checkers.append(move_piece[0])

    # Bishop check
    for move in bishop_movegen(board, king_pos, colour, filter_legal=False):
        move_piece = board.position[int(move.end.segment)][int(move.end.square.y)][int(move.end.square.x)]
        if move_piece is not None:
            if move_piece[0] != colour and move_piece[0] not in board.checkmated_players and \
                    move_piece[0] not in board.stalemated_players and move_piece[1] == "b":
                if move_piece[0] not in checkers:
                    checkers.append(move_piece[0])

    # Rook check
    for move in rook_movegen(board, king_pos, colour, filter_legal=False):
        move_piece = board.position[int(move.end.segment)][int(move.end.square.y)][int(move.end.square.x)]
        if move_piece is not None:
            if move_piece[0] != colour and move_piece[0] not in board.checkmated_players and \
                    move_piece[0] not in board.stalemated_players and move_piece[1] == "r":
                if move_piece[0] not in checkers:
                    checkers.append(move_piece[0])

    # Queen check
    for move in queen_movegen(board, king_pos, colour, filter_legal=False):
        move_piece = board.position[int(move.end.segment)][int(move.end.square.y)][int(move.end.square.x)]
        if move_piece is not None:
            if move_piece[0] != colour and move_piece[0] not in board.checkmated_players and \
                    move_piece[0] not in board.stalemated_players and move_piece[1] == "q":
                if move_piece[0] not in checkers:
                    checkers.append(move_piece[0])

    # King check
    for move in king_movegen(board, king_pos, colour, filter_legal=False):
        move_piece = board.position[int(move.end.segment)][int(move.end.square.y)][int(move.end.square.x)]
        if move_piece is not None:
            if move_piece[0] != colour and move_piece[0] not in board.checkmated_players and \
                    move_piece[0] not in board.stalemated_players and move_piece[1] == "k":
                if move_piece[0] not in checkers:
                    checkers.append(move_piece[0])

    return checkers


def get_game_state(board, colour):  # Checks for checkmate, stalemate or still playing
    legal_move_found = False
    # Search for all pieces of the same colour
    for segment in range(3):
        for y in range(4):
            for x in range(8):
                square_occupant = board.position[segment][y][x]
                if square_occupant is not None and square_occupant[0] == colour:
                    if piece_movegen(board, Position(segment, (x, y)), colour):
                        legal_move_found = True
                        break

    checkers = get_checkers(board, colour)
    print(checkers)
    if not legal_move_found:
        if checkers:
            return "checkmate"
        else:
            return "stalemate"
    else:
        # If the next turn can take your king
        if colour != board.turn and board.turns[(board.turn_index + 1) % 3] in checkers:
            return "checkmate"
        else:
            return "playing"


def legal_movegen(board, moves, colour):
    legal_moves = []
    for move in moves:
        new_board = make_move(board, move)
        if not get_checkers(new_board, colour):
            legal_moves.append(move)

    return legal_moves


def check_promotion(pawn_position, colour):
    if pawn_position.segment != colour_to_segment[colour]:
        if pawn_position.square.y == 3:  # Opponent's back rank
            return True
        # Furthest away ranks
        if pawn_position.segment == (colour_to_segment[colour] + 1) % 3 and pawn_position.square.x == 7:
            return True
        if pawn_position.segment == (colour_to_segment[colour] - 1) % 3 and pawn_position.square.x == 0:
            return True

    return False


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
            vectors = [[0, 1], [0, -1], [1, 0], [-1, 0]]
            capture_vectors = [[-1, 1], [1, 1], [1, -1], [-1, -1]]

    if not only_captures:
        for vector in vectors:
            for position_to_check in vector_to_position(position, vector):
                if position_to_check is not None:
                    if not (position_to_check.segment == colour_to_segment[colour] and position.segment != colour_to_segment[colour]):
                        square_occupant = board.position[int(position_to_check.segment)][int(
                            position_to_check.square.y)][int(position_to_check.square.x)]
                        if square_occupant is None:
                            if vector[1] == -2:  # Double pawn pushes
                                #  Check the square in front
                                if board.position[int(position_to_check.segment)][int(position_to_check.square.y + 1)][int(position_to_check.square.x)] is None:
                                    pseudo_moves.append(Move(position, position_to_check, move_type="double push"))
                            #  Promotions
                            elif check_promotion(position_to_check, colour):
                                pseudo_moves.append(Move(position, position_to_check, is_promotion=True))
                            else:
                                pseudo_moves.append(Move(position, position_to_check))

    for capture_vector in capture_vectors:
        for position_to_check in vector_to_position(position, capture_vector):
            if position_to_check:
                if not (position_to_check.segment == colour_to_segment[colour] and position.segment != colour_to_segment[colour]):
                    square_occupant = board.position[int(position_to_check.segment)][int(
                        position_to_check.square.y)][int(position_to_check.square.x)]
                    if square_occupant is not None and square_occupant[0] != colour:
                        if check_promotion(position_to_check, colour):
                            pseudo_moves.append(Move(position, position_to_check, is_promotion=True))
                        else:
                            pseudo_moves.append(Move(position, position_to_check))
                    elif square_occupant is None:
                        for turn in board.turns:
                            if turn != colour:
                                if positions_are_same(position_to_check, board.enpassant_squares[turn]):
                                    pseudo_moves.append(Move(position, position_to_check, move_type="enpassant"))

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
                square_occupant = board.position[int(position_to_check.segment)][int(
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
            square_occupant = board.position[int(position_to_check.segment)][int(
                position_to_check.square.y)][int(position_to_check.square.x)]
            if square_occupant is None:
                end_position.append(position_to_check)
                end_position += iterate_move(board, position_to_check, vector if position_to_check.segment == position.segment
                        else [-vector[0], -vector[1]], colour)
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
                    square_occupant = board.position[int(position_to_check.segment)][int(position_to_check.square.y)][
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
                square_occupant = board.position[int(position_to_check.segment)][int(
                    position_to_check.square.y)][int(position_to_check.square.x)]
                if square_occupant is None:
                    pseudo_moves.append(Move(position, position_to_check))
                else:
                    if square_occupant[0] != colour:
                        pseudo_moves.append(Move(position, position_to_check))

    if filter_legal:
        legal_moves = legal_movegen(board, pseudo_moves, colour)
        #  Check castling
        if board.castling_rights[colour]['kingside']:
            can_kingside_castle = True
            for i in range(3):
                if i != 0:  # Don't check own square for blockades
                    if 0 <= position.square.x + i <= 7: # If the check square is on the board
                        if board.position[int(position.segment)][int(position.square.y)][int(position.square.x + i)] is not None:
                            can_kingside_castle = False
                            break
                        #  Check castling squares for checks
                        test_move = Move(position, Position(position.segment, (position.square.x + i, position.square.y)))
                        new_board = make_move(board, test_move)
                        if get_checkers(new_board, colour):
                            can_kingside_castle = False
                            break
                    else:
                        can_kingside_castle = False
                        break
                if get_checkers(board, colour):  # Check if the king is in check
                    can_kingside_castle = False
                    break
            if can_kingside_castle:
                castle_move = Move(position, Position(position.segment, (position.square.x + 2, position.square.y)),
                                   move_type='kingside castle')
                legal_moves.append(castle_move)
        if board.castling_rights[colour]['queenside']:
            can_queenside_castle = True
            for i in range(4):
                if i != 0:  # Don't check own square for blockades
                    if 0 <= position.square.x - i <= 7:
                        if board.position[int(position.segment)][int(position.square.y)][int(position.square.x - i)] is not None:
                            can_queenside_castle = False
                            break
                        if i != 3:  # Don't check square next to rook for checks
                            test_move = Move(position, Position(position.segment, (position.square.x - i, position.square.y)))
                            new_board = make_move(board, test_move)
                            if get_checkers(new_board, colour):
                                can_queenside_castle = False
                                break
                    else:
                        can_queenside_castle = False
                        break
                if get_checkers(board, colour):
                    can_queenside_castle = False
                    break
            if can_queenside_castle:
                castle_move = Move(position, Position(position.segment, (position.square.x - 2, position.square.y)),
                                   move_type='queenside castle')
                legal_moves.append(castle_move)

        return legal_moves

    return pseudo_moves


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
