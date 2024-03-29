"""
Module with all of the 3D game's objects:

3D piece's data (<numpy cube matrix>, <color>)
the Piece3D class,
    meant to hold the pieces' data,
    rotate the piece, and move the piece,
and the Game3D class,
    which contains the 3D game's score,
    the 3D game's board,
    the 3D game's current and next pieces,
    and the amount of lines the player cleared during the previous
        "game step" (Look in 'Game3D.__init__').

The AXII INDEXES IN 'Game3D' and 'Piece3D' ARE DEFINED AS:
0: x: left->right
1: y: front->back
2: z: top->bottom
"""
from numpy import zeros, ndarray, rot90
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

FLOOR_WIDTH = 4
FLOORS = 20

X_AXIS = 0
Y_AXIS = 1
Z_AXIS = 2
AXII = [X_AXIS, Y_AXIS, Z_AXIS]


class Piece3D:
    """
    'self.blocks': a numpy 3D ndarray cube with 1's representing a block
    and 0's representing empty space

    The 'self.blocks' coordinate system works like this:
    self.blocks[
        relative_x_pos (left->right),
        relative_y_pos (front->back),
        relative_z_pos (top->bottom)
    ]

    'self.color': pygame color for screen display (aka: tuple[int, int, int])
    'self.pos': the position of the left-front-top corner
        ...of the 'self.blocks' matrix
    in the Game3D board. (scroll down)
    """

    def __init__(self, blocks: ndarray, color: tuple[int, int, int]) -> None:
        """
        Copies the parameters,
        BUT CHECKS THAT 'blocks' IS A 3D ARRAY,
        AND THROWS AN ERROR IF IT ISNT.
        """
        self.pos = [
            FLOOR_WIDTH //
            2 -
            len(blocks) //
            2,
            FLOOR_WIDTH //
            2 -
            len(blocks) //
            2,
            0]
        """top-left-front"""

        if len(blocks.shape) != 3:
            raise TypeError(f"'blocks' argument isn't a 3D numpy matrix!")

        self.blocks = blocks
        self.color = color

    def __str__(self):
        return "Piece(" \
            + "pos={self.pos}, blocks={self.blocks}, color={self.color=})"

    def rotate(self, axis: int, clockwise: bool):
        """
        Rotates self's blocks AROUND 'axis'
        however 'clockwise' specifies,

        ASSUMING 'self.blocks' is a cube.
        (Read this class' docstring)
        """
        rotation_axii = [X_AXIS, Y_AXIS, Z_AXIS]

        if axis not in AXII:
            raise ValueError(
                "Rotation axis 'axis'"
                + "can only be 'X_AXIS, 'Y_AXIS' or 'Z_AXIS'.\n"
                + f"Got: {axis}"
            )

        rotation_axii.remove(axis)

        if axis == Z_AXIS or axis == X_AXIS:
            clockwise = not clockwise
        # numpy matrix rotation is flipped in the Y axis,
        # according to our description of the piece,
        # so we must account for it, by flipping the Y axis'
        # rotation's direction here.

        self.blocks = rot90(
            self.blocks,
            1 if clockwise else 3,
            tuple(rotation_axii))

    def block_positions(self):
        """
        Returns all of the blocks' positions
        relative to the board.
        (aka: 'self.pos' + block_pos, as 3D vectors)
        """
        positions = []

        for x_pos, vertical_slice in enumerate(self.blocks):
            for y_pos, column in enumerate(vertical_slice):
                for z_pos, block in enumerate(column):
                    if block:
                        positions.append((
                            x_pos + self.pos[0],
                            y_pos + self.pos[1],
                            z_pos + self.pos[2]
                        ))
        return positions

    def relative_block_positions(self):
        """
        Returns all of the block's positions relative
        to the PIECE position, AKA the top-left-front position
        """
        positions = []

        for x_pos, vertical_slice in enumerate(self.blocks):
            for y_pos, column in enumerate(vertical_slice):
                for z_pos, block in enumerate(column):
                    if block:
                        positions.append((x_pos, y_pos, z_pos))
        return positions


class Game3D:
    """
    3D current and next pieces,
    a ScoreManager instance, and a board dictionary
    that functions in this format: {3d_pos: color}

    The 3D current and next pieces are NOT PART OF THE BOARD,
    and are placed IN the board when they land.

    The 'self.score_manager' instance is used exactly as 2D:
    BUT using FLOORS instead of LINES.

    The 'self.board' has tuple[int, int, int] as both the coordinates
    and the colors (of "garbage" left by the other pieces)

    THE AXII IN THIS BOARD ARE DEFINED AS THE FOLLOWING,
    AND 'self.try_move' WILL MOVE THE PIECES ACCORDING TO
    THIS 3D PROJECTION METHOD (used in 'main.py'):

    x axis: LEFT to RIGHT (0 -> FLOOR_WIDTH)
    y axis: FRONT to BACK (0 -> FLOOR_WIDTH)
    z axis: UP to DOWN (0 -> FLOORS)
    """

    def __init__(self):
        self.piece = Piece3D(*random.choice(PIECES_3D))
        self.next_piece = Piece3D(*random.choice(PIECES_3D))

        self.piece.rotate(Z_AXIS, True)
        self.piece.rotate(Y_AXIS, True)
        self.next_piece.rotate(Z_AXIS, True)
        self.next_piece.rotate(Y_AXIS, True)
        # To make pieces "face the player",
        # perhaps in a more familiar way.

        self.score_manager = Score()

        self.board = {}
        # {3D_pos: color}

        self.amount_of_levels_cleared: int = 0
        """
        Amount of levels (lines/floors, IN THIS CASE, FLOORS)
        the player cleared when the last piece landed.

        Set by 'self.clear_floors', which is called RIGHT AFTER a piece lands,
        in the same game step/frame.
        """

    def _init_random_piece(self) -> None:
        """
        Makes 'self.piece' to be 'self.next_piece'
        and initializes a random new 'self.next_piece',

        with the UNPACKED data in 'PIECES_3D'.
        (higher up in the file)
        """
        self.piece = self.next_piece
        self.next_piece = Piece3D(*random.choice(PIECES_3D))

        self.next_piece.rotate(Z_AXIS, True)
        self.next_piece.rotate(Y_AXIS, True)
        # To make pieces "face the player",
        # perhaps in a more familiar way.

    def _move_piece_down(self) -> None:
        """
        Moves 'self.piece' one floor down
        AKA adds one to its z-pos.

        If 'self.piece' overlaps any block in self.board,
        this method raises ValueError.
        """
        self.piece.pos[2] += 1

        if any(
            block in self.board
            for block in self.piece.block_positions()
        ):
            raise ValueError(
                "Moved piece down,"
                + f"overlapping board block! {self.board=} {self.piece=}"
            )

    def try_move(self, move: str) -> bool:
        """
        Tries to move piece in 'move' direction.
        The direction options are defined in
        'game.move_data.py', in this folder.

        If the piece were to overlap another cube, or have any of its
        cubes outside the position ranges of the board,
        THE MOVE FAILS.

        OTHERWISE, THE MOVE SUCCEEDS.

        AND THE AXII DIRECTION ARE DEFINED IN THIS CLASS'
        DOCSTRING!
        """
        # SUGGESTION: PLEASE MANAGE YOUR INDEXES, POSITIONS AND MOVES BETTER!
        # I HAD TO SWAP TONS OF VALUES AROUND TO GET THE PIECES
        # TO BEHAVE IN THE CORRECT POSITIONS!

        if move not in MOVES_3D:
            raise ValueError(
                "Invalid 3D Game move!"
                + f"Expected: {' or '.join(MOVES_3D)}. Got: {move}"
            )

        # All these paths return True after they finish,
        # or fail and return False RIGHT THERE.
        if move == LEFT:
            for x_pos, y_pos, z_pos in self.piece.block_positions():
                if self.board.get((x_pos - 1, y_pos, z_pos)) or \
                        x_pos == 0:
                    return False
            self.piece.pos[X_AXIS] -= 1

        elif move == RIGHT:
            for x_pos, y_pos, z_pos in self.piece.block_positions():
                if self.board.get((x_pos + 1, y_pos, z_pos)) or \
                        x_pos == FLOOR_WIDTH - 1:
                    return False
            self.piece.pos[X_AXIS] += 1

        elif move == BACK:
            for x_pos, y_pos, z_pos in self.piece.block_positions():
                if self.board.get((x_pos, y_pos + 1, z_pos)) or \
                        y_pos == FLOOR_WIDTH - 1:
                    return False
            self.piece.pos[Y_AXIS] += 1

        elif move == FRONT:
            for x_pos, y_pos, z_pos in self.piece.block_positions():
                if self.board.get((x_pos, y_pos - 1, z_pos)) or \
                        y_pos == 0:
                    return False
            self.piece.pos[Y_AXIS] -= 1

        elif move == HARD_DROP:
            while not self.landed():
                self._move_piece_down()
            # move the piece down until it lands.

        elif move == SOFT_DROP:
            if self.landed():
                return False
            # can't move the piece down if it has already landed

            self._move_piece_down()

        return True

    def set_down(self) -> None:
        """
        Makes piece 'inbeded' in board.
        AKA: "puts" the cubes of the piece
        in the 'self.board' dictionary.
        """
        for cube_pos in self.piece.block_positions():
            self.board[cube_pos] = self.piece.color

    def try_rotate(self, axis: int, clockwise: bool) -> bool:
        """
        Rotates 'self.piece' AROUND the 'axis'
        DEFINED AT THE TOP OF THIS CLASS.

        If the piece can't rotate because it goes outside of the 3D board,
        or a block is already in a position
        where the piece's block will end up in,
        this method CANCELS THE ROTATION.

        Returns weather or not the rotation succeeded.
        """
        if axis not in (X_AXIS, Y_AXIS, Z_AXIS):
            raise ValueError(
                "Invalid rotation axis! "
                + f"Expected: X_AXIS, Y_AXIS or Z_AXIS. Got: {axis}"
            )
        self.piece.rotate(axis, clockwise)
        # rotate

        if any(
            piece_block_pos in self.board
            or piece_block_pos[0] not in range(FLOOR_WIDTH)
            or piece_block_pos[1] not in range(FLOOR_WIDTH)
            or piece_block_pos[2] not in range(FLOORS)
            for piece_block_pos in self.piece.block_positions()
        ):
            # if any block in self.piece.block_positions
            # is aleady occupied by self.board,
            # or is outside the board,
            # undo
            self.piece.rotate(axis, not clockwise)
            return False
        return True

    def landed(self) -> bool:
        """
        Checks if 'self's current piece landed.
        A piece has landed if the floor or
        another square is EXACTLY one square below
        one of the piece's squares.
        """
        for block_x_pos, block_y_pos, block_z_pos in reversed(
                self.piece.block_positions()):
            # 'self.piece.block_positions' returns all of the squares
            # in order: up->down, left->right.
            # We want to scan down->up.
            if self.board.get((block_x_pos, block_y_pos, block_z_pos + 1)) or \
                    block_z_pos == FLOORS - 1:
                # If there's a block or the floor underneath it...
                # Return True.
                return True
        return False

    def _clear_floors(self, previous_piece: Piece3D) -> None:
        # time: O(n), where n is: height of piece
        # space: O(n), where n is: height of piece
        deleted_floors = set()

        # Look at each floor 'previous_piece' landed in
        # (assuming it's 'self.piece', that just landed)
        # and add the floor index to 'deleted_floors' if the floor
        # was completed
        PREVIOUS_PIECE_HEIGHT = previous_piece.blocks.shape[2]
        PREVIOUS_PIECE_Z_POS = previous_piece.pos[2]
        for z_pos in range(
                PREVIOUS_PIECE_Z_POS,
                PREVIOUS_PIECE_Z_POS +
                PREVIOUS_PIECE_HEIGHT):
            # look at each floor in the dropped piece

            if all(
                (x_pos, y_pos, z_pos) in self.board
                for y_pos in range(FLOOR_WIDTH)
                for x_pos in range(FLOOR_WIDTH)
            ):
                # If the whole floor in the board is filled
                for x_pos in range(FLOOR_WIDTH):
                    for y_pos in range(FLOOR_WIDTH):
                        self.board.pop((x_pos, y_pos, z_pos))
                # remove that floor
                deleted_floors.add(z_pos)
                # keep track of that floor

        if not deleted_floors:
            return
        # no cleared floors, so no "landing" of floors either.

        landing_floor = max(deleted_floors)
        # lowest deleted floor is where all the floors with gunk in them will
        # 'land' on.

        # print(f"{deleted_floors=} {landing_floor=}")
        # make board's rows higher than the cleared rows "land"
        # in that space
        gunk_floor = landing_floor - 1
        for gunk_floor in range(landing_floor, -1, -1):

            if gunk_floor not in deleted_floors:
                # if floor has gunk in it
                for x_pos in range(FLOOR_WIDTH):
                    for y_pos in range(FLOOR_WIDTH):
                        if (x_pos, y_pos, gunk_floor) in self.board:
                            self.board[(x_pos, y_pos, landing_floor)] = \
                                self.board.pop((x_pos, y_pos, gunk_floor))
                # move that floor down to the landing floor

                landing_floor -= 1

        self.amount_of_levels_cleared = len(deleted_floors)
        self.score_manager.score(self.amount_of_levels_cleared)

    def play(self) -> bool:
        """
        Plays Tetris for one "step" (where the piece goes one down),
        and returns True if the game can continue,
        and False it the game is over.

        This is the "step":
        If the current piece has landed,
        we set it down using 'self.set_down',
        clear any floors the piece completed with 'self.clear_floors'
        and makes a new piece.

        If the new piece spawns where it immediately lands,
        the game is over.

        If the piece hasn't landed, or if the game isn't over,
        we just move the piece one down using
        'self.move_piece_down'.
        """
        if self.landed():
            self.set_down()
            self._clear_floors(self.piece)
            self._init_random_piece()

            if any(
                block in self.board
                for block in self.piece.block_positions()
            ):
                return False
        else:
            self._move_piece_down()

        return True
