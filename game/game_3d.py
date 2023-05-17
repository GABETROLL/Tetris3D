from numpy import zeros, ndarray, nditer
import random
from game.score import Score
from game.move_data import *

I_3D = zeros(
    (4, 4, 4)
)
I_3D[1] = [
    [0, 0, 0, 0],
    [1, 1, 1, 1],
    [0, 0, 0, 0],
    [0, 0, 0, 0]
]
I_3D = (
    I_3D,
    (0, 255, 255)
)

L_3D = zeros(
    (3, 3, 3)
)
L_3D[1] = [
    [0, 0, 1],
    [1, 1, 1],
    [0, 0, 0]
]
L_3D = (
    L_3D,
    (0, 0, 255)
)

J_3D = zeros(
    (3, 3, 3)
)
J_3D[1] = [
    [1, 0, 0],
    [1, 1, 1],
    [0, 0, 0]
]
J_3D = (
    J_3D,
    (255, 128, 0)
)

O_3D = zeros(
    (2, 2, 2)
)
O_3D[0] = [
    [1, 1],
    [1, 1]
]
O_3D = (
    O_3D,
    (255, 255, 0)
)

S_3D = zeros(
    (3, 3, 3)
)
S_3D[1] = [
    [0, 1, 1],
    [1, 1, 0],
    [0, 0, 0]
]
S_3D = (
    S_3D,
    (0, 255, 0)
)

T_3D = zeros(
    (3, 3, 3)
)
T_3D[1] = [
    [0, 1, 0],
    [1, 1, 1],
    [0, 0, 0]
]
T_3D = (
    T_3D,
    (128, 0, 255)
)

Z_3D = zeros(
    (3, 3, 3)
)
Z_3D[1] = [
    [1, 1, 0],
    [0, 1, 1],
    [0, 0, 0]
]
Z_3D = (
    Z_3D,
    (255, 0, 0)
)

PIECES_3D = [I_3D, L_3D, J_3D, O_3D, S_3D, T_3D, Z_3D]
"""
All of the classic 2D Tetrominos, but padded to be 3D boxes.
-AKA-
3D boxes with only a middle slice of it being occupied by the classic
2D Tetrominos
"""

BOARD_WIDTH_DEPTH = 10
FLOORS = 20


class Piece3D:
    def __init__(self, blocks: ndarray, color: tuple[int, int, int]) -> None:
        self.pos = [3, 3, 0]
        """top-left-front"""
        self.blocks = blocks
        self.color = color
    
    def block_positions(self):
        """
        Returns all of the blocks' positions
        relative to the board.
        (aka: 'self.pos' + block_pos, as 3D vectors)
        """
        positions = []

        for (x_pos, y_pos, z_pos), block in nditer(self.blocks, flags=['multi_index']):
            if block:
                positions.append(
                    (x_pos + self.pos[0], y_pos + self.pos[1], z_pos + self.pos[2])
                )
        return positions

    def relative_block_positions(self):
        """
        Returns all of the block's positions relative
        to the PIECE position, AKA the top-left-front position
        """
        positions = []
        for block_position, block in nditer(self.blocks, flags=['multi_index']):
            if block:
                positions.append(block_position)
        return positions


class Game3D:
    def __init__(self):
        self.piece = Piece3D(*random.choice(PIECES_3D))
        self.next_piece = Piece3D(*random.choice(PIECES_3D))

        self.score_manager = Score()

        self.board = {}
        # {3D_pos: color}
    
    def init_random_piece(self):
        self.piece = self.next_piece
        self.next_piece = Piece3D(*random.choice(PIECES_3D))
    
    def move_piece_down(self):
        self.piece.pos[1] += 1
    
    def try_move(self, move: str):
        if move == LEFT:
            for x_pos, y_pos, z_pos in self.piece.block_positions():
                if self.board.get((x_pos - 1, y_pos, z_pos)) or \
                        x_pos == 0:
                    return False
            self.piece.pos[0] -= 1
            return True

        if move == RIGHT:
            for x_pos, y_pos, z_pos in self.piece.block_positions():
                if self.board.get((x_pos + 1, y_pos, z_pos)) or \
                        x_pos == BOARD_WIDTH_DEPTH - 1:
                    return False
            self.piece.pos[0] += 1
            return True

        if move == BACK:
            for x_pos, y_pos, z_pos in self.piece.block_positions():
                if self.board.get((x_pos, y_pos - 1, z_pos)) or \
                        x_pos == 0:
                    return False
            self.piece.pos[1] -= 1
            return True

        if move == FRONT:
            for x_pos, y_pos, z_pos in self.piece.block_positions():
                if self.board.get((x_pos, y_pos + 1, z_pos)) or \
                        x_pos == BOARD_WIDTH_DEPTH - 1:
                    return False
            self.piece.pos[1] += 1
            return True

        if move == HARD_DROP:
            # If the move is a hard drop,
            while not self.landed():
                self.move_piece_down()
            return True
            # We move the piece down until it lands.

        elif move == SOFT_DROP and not self.landed():
            # If the move is a soft drop, and we haven't landed,
            self.move_piece_down()
            return True
            # We move down once.

    def set_down(self):
        """
        Makes piece 'inbeded' in board.
        AKA: "puts" the cubes of the piece
        in the 'self.board' dictionary.
        """
        for square_pos in self.piece.block_positions():
            self.board[square_pos] = self.piece.color
    
    def rotate(self):
        pass

    def try_rotate(self, clockwise=True):
        """Rotates 'self.piece'. If the piece overlaps the outside of the board
        or a square in the board, the rotation is cancelled."""
        self.rotate(clockwise)

        if any(
            pos in self.board
            or pos[0] not in range(BOARD_WIDTH_DEPTH)
            or pos[1] not in range(BOARD_WIDTH_DEPTH)
            or pos[2] not in range(FLOORS)
            for pos in self.piece.block_positions()
        ):
            self.rotate(not clockwise)

    def landed(self):
        """
        Checks if 'self's current piece landed.
        A piece has landed if the floor or
        another square is EXACTLY one square below
        one of the piece's squares.
        """
        for block_pos in reversed(self.piece.block_positions()):
            # 'self.piece.block_positions' returns all of the squares
            # in order: up->down, left->right.
            # We want to scan down->up.
            if self.board.get((block_pos[0], block_pos[1], block_pos[2] + 1)) or \
                    block_pos[1] ==  - 1:
                # If there's a block or the floor underneath it...
                # Return True.
                return True
        return False

    def landing_handler(self):
        """If a piece landed, marks it at the previous piece,
        makes it part of the board, and spawns a new one."""
        if self.landed():
            self.set_down()
            self.clear_lines(self.piece)
            self.init_random_piece()

    def clear_lines(self, previous_piece: Piece3D):
        # time: O(n), where n is: height of piece
        # space: O(n), where n is: height of piece
        deleted_floors = set()

        PREVIOUS_PIECE_HEIGHT = previous_piece.blocks.shape[2]
        for z_pos in range(previous_piece.pos, previous_piece.pos + PREVIOUS_PIECE_HEIGHT):
            # look at each floor in the dropped piece

            if all(
                (x_pos, y_pos, z_pos) in self.board
                for y_pos in range(BOARD_WIDTH_DEPTH)
                for x_pos in range(BOARD_WIDTH_DEPTH)
            ):
                # If the whole floor in the board is filled
                for x_pos in range(BOARD_WIDTH_DEPTH):
                    for y_pos in range(BOARD_WIDTH_DEPTH):
                        self.board.pop((x_pos, y_pos, z_pos))
                # remove that floor
                deleted_floors.add(z_pos)
                # keep track of that floor

        landing_floor = 0
        for floor in deleted_floors:
            if floor > landing_floor:
                landing_floor = floor
        # lowest deleted floor is where all the floors with gunk in them will 'land' on.

        gunk_floor = landing_floor - 1
        while gunk_floor > -1:
            if not (gunk_floor in deleted_floors):
                # if floor has gunk in it
                for x_pos in range(BOARD_WIDTH_DEPTH):
                    if (x_pos, gunk_floor) in self.board:
                        self.board[(x_pos, landing_floor)] = self.board.pop((x_pos, gunk_floor))
                # move that floor down to the landing floor

                landing_floor -= 1
            gunk_floor -= 1

        self.score_manager.score(len(deleted_floors))

    def play(self):
        self.landing_handler()
        self.move_piece_down()