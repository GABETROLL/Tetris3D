"""
Module with all of the 2D game's objects:

2D piece's data (<numpy 2D ndarray>, <color>)
the Piece2D class, meant to hold the pieces' data, rotate the piece and move the piece,
and the Game2D class, which contains the 2D game's score, the 2D game's board,
the 2D game's current and next pieces, and the amount of lines cleared the previous
"game step" (Look in 'Game2D.__init__').

The AXII INDEXES IN 'Game2D' and 'Piece2D' ARE DEFINED AS:
0: x: left->right
1: y: top-> bottom
"""
from numpy import ndarray, rot90, matrix
import random
from game.score import Score
from game.move_data import *

I_2D = (
    matrix(
        [
            [0, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 1, 0, 0]
        ]
    ).A,
    (0, 255, 255)
)

L_2D = (
    matrix(
        [
            [0, 1, 0],
            [0, 1, 0],
            [1, 1, 0]
        ]
    ).A,
    (255, 128, 0)
)

J_2D = (
    matrix(
        [
            [1, 1, 0],
            [0, 1, 0],
            [0, 1, 0]
        ]
    ).A,
    (0, 0, 255)
)

O_2D = (
    matrix(
        [
            [1, 1],
            [1, 1]
        ]
    ).A,
    (255, 255, 0)
)

S_2D = (
    matrix(
        [
            [0, 1, 0],
            [1, 1, 0],
            [1, 0, 0]
        ]
    ).A,
    (0, 255, 0)
)

T_2D = (
    matrix(
        [
            [0, 1, 0],
            [1, 1, 0],
            [0, 1, 0]
        ]
    ).A,
    (128, 0, 255)
)

Z_2D = (
    matrix(
        [
            [1, 0, 0],
            [1, 1, 0],
            [0, 1, 0]
        ]
    ).A,
    (255, 0, 0)
)

PIECES_2D: list[ndarray, tuple[int, int, int]] = [I_2D, L_2D, J_2D, O_2D, S_2D, T_2D, Z_2D]
"""
All of the classic 2D Tetrominos:

A list of tuples of a numpy.ndarray of 1's and 0's

(the 1's representing the piece's blocks,
and the 0's representing empty space)

and their colors (a tuple of 3 0 <= ints <= 255 )
"""

COLUMNS = 10
ROWS = 20

X_AXIS = 0
Y_AXIS = 1
AXII = [X_AXIS, Y_AXIS]


class Piece2D:
    """
    'initial_rotation': a numpy 2D ndarray with 1's representing a block
    and 0's representing empty space. This should be how the piece spawns,
    when the player hasn't rotated it yet.

    The 'initial_rotation' coordinate system works like this:
    initial_rotation[relative_x_pos (left->right), relative_y_pos (top->bottom)]

    'color': pygame color for screen display (aka: tuple[int, int, int])

    'pos': the position of the left-front-top corner of the 'initial_rotation' matrix
    in the Game2D board. (scroll down)
    """
    def __init__(self, initial_rotation: ndarray, color: tuple[int, int, int]) -> None:
        """
        Copies the parameters,
        BUT CHECKS THAT 'initial_rotation' IS A 2D 'numpy.ndarray',
        AND THROWS AN ERROR IF IT ISNT.
        """

        self.pos = [((COLUMNS - 1) >> 1) - (len(initial_rotation) >> 1), 0]
        """left-top"""

        if not isinstance(initial_rotation, ndarray) or len(initial_rotation.shape) != 2:
            raise TypeError(f"'initial_rotation' argument isn't a 2D 'numpy.ndarray'!")

        self.initial_rotation: ndarray = initial_rotation
        self.rotation: int = 0

        self.color: tuple[int, int, int] = color

    def __str__(self) -> str:
        return f"Piece(pos={self.pos}, initial_rotation={self.initial_rotation}, color={self.color=})"

    @property
    def blocks(self) -> ndarray:
        return rot90(self.initial_rotation, self.rotation)

    @property
    def piece_width(self) -> int:
        return self.blocks.shape[X_AXIS]

    @property
    def piece_height(self) -> int:
        return self.blocks.shape[Y_AXIS]

    def rotate(self, clockwise: bool) -> None:
        """
        Changes 'self.rotation' to represent the new rotation
        state of 'self'.

        The 4 rotation states are represented by:
            0, 1, 2, 3;
        where 0 is 'self.initial_rotation',
        1 is 'self.initial_rotation' rotated clockwise,
        2 is 'self.initial_rotation' rotated clockwise twice
        and 3 is 'self.initial_rotation' rotated clockwise 3 times.
        
        of 'self.initial_rotation' (clockwise): 
        """
        self.rotation += 1 if clockwise else -1
        self.rotation = abs(self.rotation % (POSSIBLE_ROTATIONS := 4))

    def square_positions(self) -> list[tuple[int, int]]:
        """
        Returns all of 'self's blocks' positions
        relative to the board.
        (aka: 'self.pos' + block_pos, as 2D vectors)
        """
        positions = []

        for x_pos, column in enumerate(self.blocks):
            for y_pos, block in enumerate(column):

                    if block:
                        positions.append(
                            (x_pos + self.pos[0], y_pos + self.pos[1])
                        )
        return positions

    def relative_square_positions(self) -> list[tuple[int, int]]:
        """
        Returns all of the block's positions relative
        to the PIECE position, AKA the top-left-front position
        """
        positions = []

        for x_pos, column in enumerate(self.blocks):
            for y_pos, block in enumerate(column):

                    if block:
                        positions.append(
                            (x_pos, y_pos)
                        )
        return positions


class Game2D:
    """
    2D current and next pieces,
    a ScoreManager instance, and a board dictionary
    that functions in this format: {2D_pos: color}

    The 2D current and next pieces are NOT PART OF THE BOARD,
    and are placed IN the board WHEN THEY LAND.

    The 'self.board' has tuple[int, int] as coordinate keys
    and tuple[int, int, int] as the colors
    (of "garbage" left by the other pieces)

    THE AXII IN THIS BOARD ARE DEFINED AS THE FOLLOWING:

    x axis: LEFT to RIGHT (0 -> COLUMNS)
    y axis: UP to DOWN (0 -> ROWS)
    """
    def __init__(self):
        self.piece = Piece2D(*random.choice(PIECES_2D))
        self.next_piece = Piece2D(*random.choice(PIECES_2D))

        self.score_manager = Score()

        self.board = {}
        # {2D_pos: color}

        self.amount_of_levels_cleared: int = 0
        """
        Amount of levels (lines/floors, IN THIS CASE, LINES) the player cleared when the last piece
        landed

        Set by 'self.clear_lines', which is called RIGHT AFTER a piece lands,
        in the same game step/frame.
        """

    def _init_random_piece(self) -> None:
        """
        Makes 'self.piece' to be 'self.next_piece'
        and initializes a random new 'self.next_piece',

        with the UNPACKED data in 'PIECES_2D'.
        (higher up in the file)
        """
        self.piece = self.next_piece
        self.next_piece = Piece2D(*random.choice(PIECES_2D))

    def _move_piece_down(self) -> None:
        """
        Moves 'self.piece' one row down
        (AKA: adds 1 to 'self.piece.pos[Y_AXIS]'
            ('Y_AXIS' is 1, ldefined above in this file)
        )

        If 'self.piece' overlaps any block in self.board,
        this method raises ValueError.
        """
        self.piece.pos[Y_AXIS] += 1

        if any(
            block in self.board
            for block in self.piece.square_positions()
        ):
            raise ValueError(f"Moved piece down, overlapping board block! {self.board=} {self.piece=}")

    def try_move(self, move: str) -> bool:
        """
        Tries to move piece in 'move' direction.
        The direction options are defined in
        'game.move_data.py', in this folder.

        If the piece were to overlap another square, or have any of its
        squares outside the position ranges of the board,
        THE MOVE FAILS.

        OTHERWISE, THE MOVE SUCCEEDS.

        AND THE AXII DIRECTION ARE DEFINED IN THIS CLASS'
        DOCSTRING!
        """
        # SUGGESTION: PLEASE MANAGE YOUR INDEXES, POSITIONS AND MOVES BETTER!
        # I HAD TO SWAP TONS OF VALUES AROUND TO GET THE PIECES
        # TO BEHAVE IN THE CORRECT POSITIONS!

        if move not in MOVES_2D:
            raise ValueError(
                f"Invalid 2D Game move! Expected: {' or '.join(MOVES_2D)}. Got: {move}"
            )

        # All these paths jump to the end of this method after they finish,
        # and return True,
        # or fail and return False RIGHT THERE.
        if move == LEFT:
            for x_pos, y_pos in self.piece.square_positions():
                if self.board.get((x_pos - 1, y_pos)) or \
                        x_pos == 0:
                    return False
            self.piece.pos[X_AXIS] -= 1

        elif move == RIGHT:
            for x_pos, y_pos in self.piece.square_positions():
                if self.board.get((x_pos + 1, y_pos)) or \
                        x_pos == COLUMNS - 1:
                    return False
            self.piece.pos[X_AXIS] += 1

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
        AKA: "puts" the squares of the piece
        in the 'self.board' dictionary.
        """
        for square_pos in self.piece.square_positions():
            self.board[square_pos] = self.piece.color

    def try_rotate(self, clockwise: bool = True) -> bool:
        """
        Rotates 'self.piece' in the direction 'clockwise' specifies
        (True if clockwise, False if counter-clockwise).

        If the piece can't rotate because it goes outside of the 2D board,
        or any block  of the piece overlaps a block in the 2D board,
        this method CANCELS THE ROTATION.

        Returns weather or not the rotation succeeded.
        """

        self.piece.rotate(clockwise)
        # rotate

        if any(
            piece_block_pos in self.board
            or piece_block_pos[X_AXIS] not in range(COLUMNS)
            or piece_block_pos[Y_AXIS] not in range(ROWS)
            for piece_block_pos in self.piece.square_positions()
        ):
            # if any block in self.piece.block_positions
            # is aleady occupied by self.board,
            # or is outside the board,
            # undo
            self.piece.rotate(not clockwise)
            return False
        return True

    def landed(self) -> bool:
        """
        Checks if 'self's current piece landed.
        A piece has landed if the floor or
        another square is EXACTLY one square below
        one of the piece's squares.
        """
        for block_x_pos, block_y_pos in reversed(self.piece.square_positions()):
            # 'self.piece.block_positions' returns all of the squares
            # in order: up->down, left->right.
            # We want to scan down->up.
            if self.board.get((block_x_pos, block_y_pos + 1)) or \
                    block_y_pos == ROWS - 1:
                # If there's a block or the floor underneath it...
                # Return True.
                return True
        return False

    def _clear_lines(self, previous_piece: Piece2D) -> None:
        # time: O(n), where n is: height of piece
        # space: O(n), where n is: height of piece
        cleared_lines = set()

        # Look at each line 'previous_piece' landed in
        # (assuming it's 'self.piece', that just landed)
        # and add the line index to 'deleted_lines' if the line
        # was completed
        PREVIOUS_PIECE_HEIGHT = previous_piece.blocks.shape[Y_AXIS]
        PREVIOUS_PIECE_Y_POS = previous_piece.pos[Y_AXIS]

        for y_pos in range(PREVIOUS_PIECE_Y_POS, PREVIOUS_PIECE_Y_POS + PREVIOUS_PIECE_HEIGHT):
            # look at each line in the dropped piece

            if all(
                (x_pos, y_pos) in self.board
                for x_pos in range(COLUMNS)
            ):
                # If the whole line in the board is filled
                for x_pos in range(COLUMNS):
                    self.board.pop((x_pos, y_pos))
                # remove that line
                cleared_lines.add(y_pos)
                # keep track of that line

        if not cleared_lines:
            return
        # no cleared lines, so no "landing" of lines either.

        landing_line = max(cleared_lines)
        # lowest deleted line is where all the lines with gunk in them will 'land' on.

        # print(f"{deleted_lines=} {landing_line=}")
        # make board's rows higher than the cleared rows "land"
        # in that space
        gunk_line = landing_line - 1
        for gunk_line in range(landing_line, -1, -1):

            if gunk_line not in cleared_lines:
                # if line has gunk in it
                for x_pos in range(COLUMNS):
                    if (x_pos, gunk_line) in self.board:
                        self.board[(x_pos, landing_line)] = self.board.pop((x_pos, gunk_line))
                # move that line down to the landing line

                landing_line -= 1

        self.amount_of_levels_cleared = len(cleared_lines)
        self.score_manager.score(self.amount_of_levels_cleared)

    def play(self) -> bool:
        """
        Plays Tetris for one "step" (where the piece goes one down),
        and returns True if the game can continue,
        and False it the game is over.

        This is the "step":
        If the current piece has landed,
        we set it down using 'self.set_down',
        clear any lines the piece completed with 'self.clear_lines'
        and makes a new piece.
        
        If the new piece spawns where it immediately lands,
        the game is over.

        If the piece hasn't landed, or if the game isn't over,
        we just move the piece one down using
        'self.move_piece_down'.
        """
        if self.landed():
            self.set_down()
            self._clear_lines(self.piece)
            self._init_random_piece()

            if any(
                block in self.board
                for block in self.piece.square_positions()
            ):
                return False
        else:
            self._move_piece_down()

        return True
