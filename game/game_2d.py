"""
Module with all of the 2D piece's data (blocks, starting position, color),
the Piece2D class, meant to hold:
    the pieces' data,
    rotate the piece and move the piece,
and the Game2D class, which contains:
    the 2D game's score,
    the 2D game's board,
    the 2D game's current and next pieces,
    and the amount of lines the player cleared during the previous "game step"
        (Look in 'Game2D.__init__').
"""
import random
from game.score import Score

START_POS = [3, 0]

I = (["    ",
      "####",
      "    ",
      "    "],

     ["  # ",
      "  # ",
      "  # ",
      "  # "],

     ["    ",
      "    ",
      "####",
      "    "],

     [" #  ",
      " #  ",
      " #  ",
      " #  "],

     START_POS,
     (0, 255, 255))

J = (["#  ",
      "###",
      "   "],

     [" ##",
      " # ",
      " # "],

     ["   ",
      "###",
      "  #"],

     [" # ",
      " # ",
      "## "],

     START_POS,
     (0, 0, 255))

L = (["  #",
      "###",
      "   "],

     [" # ",
      " # ",
      " ##"],

     ["   ",
      "###",
      "#  "],

     ["## ",
      " # ",
      " # "],

     START_POS,
     (255, 128, 0))

O = (["##",
      "##"],

     [4, 0],
     (255, 255, 0))

S = ([" ##",
      "## ",
      "   "],

     [" # ",
      " ##",
      "  #"],

     ["   ",
      " ##",
      "## "],

     ["#  ",
      "## ",
      " # "],

     START_POS,
     (0, 255, 0))

T = ([" # ",
      "###",
      "   "],

     [" # ",
      " ##",
      " # "],

     ["   ",
      "###",
      " # "],

     [" # ",
      "## ",
      " # "],

     START_POS,
     (128, 0, 255))

Z = (["## ",
      " ##",
      "   "],

     ["  #",
      " ##",
      " # "],

     ["   ",
      "## ",
      " ##"],

     [" # ",
      "## ",
      "#  "],

     START_POS,
     (255, 0, 0))
# Pieces data. Line-by-line data of piece's squares. Start positions and
# colors.

ROWS = 20
COLUMNS = 10


class Piece2D:
    """
    2D piece class with all of its rotation configurations,
    position in the board (at the top left of the piece's matrix),
    and its color.

    The rotation configurations must be matrices of list[str],
    made with # characters representing blocks, and " " characters
    representing space.
    """

    def __init__(self, piece: tuple):
        """
        'piece' should be I, J, L, O, S, T or Z.

        The rotation configurations must be matrices of list[str],
        made with # characters representing blocks, and " " characters
        representing space.
        """
        piece = list(piece)
        self.pos = list(piece.pop(-2))
        self.color = piece.pop(-1)
        self.all_rotations = piece
        self.rotation = 0

    @property
    def piece(self):
        """
        The current rotation configuration of 'self'.
        """
        return self.all_rotations[self.rotation]

    @property
    def piece_width(self):
        return len(self.piece[0])

    @property
    def piece_height(self):
        return len(self.piece)

    def relative_square_positions(self):
        """
        Returns the list of the positions of the squares
        in 'self.piece', IF 'self' WHERE IN THE TOP LEFT
        OF THE BOARD (aka, the "relative position")

        THE POSITIONS ARE RETURNED (x, y), NOT (y, x)
        """
        positions = []

        for ri, row in enumerate(self.piece):
            for ci, square in enumerate(row):

                if square == "#":
                    position = (ci, ri)
                    # They're "backwards" because the ci is the x position,
                    # and ri is the y position, and that's the order
                    # of a coordinate here, and in the window display
                    positions.append(position)
        return positions

    def square_positions(self):
        """
        Returns the list of the OBJECTIVE position all the squares of
        'self', the tetromino.

        THE POSITIONS ARE RETURNED (x, y), NOT (y, x)
        """
        positions = []

        for ri, row in enumerate(self.piece):
            for ci, square in enumerate(row):

                if square == "#":
                    position = (self.pos[0] + ci, self.pos[1] + ri)
                    positions.append(position)
        return positions


class Game2D:
    def __init__(self):
        self.pieces = [I, J, L, O, S, T, Z]

        self.piece = Piece2D(random.choice(self.pieces))
        self.next_piece = Piece2D(random.choice(self.pieces))

        self.score_manager = Score()

        self.board = {}
        # {pos: color}

        self.amount_of_levels_cleared: int = 0
        """
        Amount of levels (lines/floors, IN THIS CASE, LINES)
        the player cleared when the last piece landed.

        Set by 'self.clear_lines', which is called RIGHT AFTER a piece lands,
        in the same game step/frame.
        """

    def init_random_piece(self):
        self.piece = self.next_piece
        self.next_piece = Piece2D(random.choice(self.pieces))

    def move_piece_down(self):
        self.piece.pos[1] += 1

    def try_move(self, move):
        """Tries to move piece down, and returns
        weather or not it was successfully moved.

        A piece can be successfully moved if it's
        next position (SHOULD always be one over...)
        doesn't overlap any existing blocks in the board.

        Moves can be: LEFT, RIGHT, SOFT_DROP or HARD_DROP.
        """

        if move == "l":
            for x_pos, y_pos in self.piece.square_positions():
                if self.board.get((x_pos - 1, y_pos)) or \
                        x_pos == 0:
                    return False
            self.piece.pos[0] -= 1
            return True

        if move == "r":
            for x_pos, y_pos in self.piece.square_positions():
                if self.board.get((x_pos + 1, y_pos)) or \
                        x_pos == COLUMNS - 1:
                    return False
            self.piece.pos[0] += 1
            return True

        if move == "h":
            # If the move is a hard drop,
            while not self.landed():
                self.move_piece_down()
            return True
            # We move the piece down until it lands.

        elif move == "s" and not self.landed():
            # If the move is a soft drop, and we haven't landed,
            self.move_piece_down()
            return True
            # We move down once.

    def set_down(self):
        """
        Makes piece 'inbeded' in board.
        AKA: "puts" the squares of the piece
        in the 'self.board' dictionary.
        """
        for square_pos in self.piece.square_positions():
            self.board[square_pos] = self.piece.color

    def try_move_up(self):
        """
        Moves 'self'ss current piece up unless a square above it blocks it.
        Returns weather or not it was able to move up.
        """
        for x_pos, y_pos in self.piece.square_positions():
            if self.board.get((x_pos, y_pos - 1)):
                return False

        self.piece.pos[1] -= 1
        return True

    def rotate(self, clockwise=True):
        self.piece.rotation += 1 if clockwise else -1
        self.piece.rotation = abs(
            self.piece.rotation % len(
                self.piece.all_rotations))
        # Loops trough rotations in self.complete piece.

        # Uses mod operator to loop through piece rotations,
        # absolutes value in case they rotated counter-clockwise

    def try_rotate(self, clockwise=True) -> bool:
        """
        Rotates 'self.piece'. If the piece overlaps the outside of the board
        or a square in the board, the rotation is cancelled.

        Returns True if rotation succeeded, and False if the rotation
        needed to be cancelled.
        """
        self.rotate(clockwise)

        if any(
            pos in self.board
            or pos[0] not in range(COLUMNS)
            or pos[1] not in range(ROWS)
            for pos in self.piece.square_positions()
        ):
            self.rotate(not clockwise)

            return False
        return True

    def landed(self):
        """
        Checks if 'self's current piece landed.
        A piece has landed if the floor or
        another square is EXACTLY one square below
        one of the piece's squares.
        """
        for square_pos in reversed(self.piece.square_positions()):
            # 'self.piece.square_positions' returns all of the squares
            # in order: up->down, left->right.
            # We want to scan down->up.
            if self.board.get((square_pos[0], square_pos[1] + 1)) or \
                    square_pos[1] == ROWS - 1:
                # If there's a block or the wall underneath it...
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

    def clear_lines(self, previous_piece: Piece2D) -> int:
        """
        Finds every row in 'previous_piece', ASSUMING THAT
        'previous_piece' IS THE PIECE THAT JUST LANDED,
        and clears all of the lines it completes.

        Stores the amount of lines the player just cleared
        in 'self.amount_of_lines_cleared'.
        """
        # time: O(n), where n is: height of piece
        # space: O(n), where n is: height of piece
        deleted_rows = set()

        for y_pos, row in zip(
                range(len(previous_piece.piece), 0, -1), previous_piece.piece):
            # look at each row in the dropped piece
            square_y_pos = self.piece.pos[1] + len(self.piece.piece) - y_pos

            for x_pos in range(COLUMNS):
                if not ((x_pos, square_y_pos) in self.board):
                    break
            else:
                # If the whole row in the board is filled
                for x_pos in range(COLUMNS):
                    self.board.pop((x_pos, square_y_pos))
                # remove that row
                deleted_rows.add(square_y_pos)
                # keep track of that row

        landing_row = 0
        for row in deleted_rows:
            if row > landing_row:
                landing_row = row
        # lowest deleted row is where all the rows with gunk in them will
        # 'land' on.

        gunk_row = landing_row - 1
        while gunk_row > -1:
            if not (gunk_row in deleted_rows):
                # if row has gunk in it
                for x_pos in range(COLUMNS):
                    if (x_pos, gunk_row) in self.board:
                        self.board[(x_pos, landing_row)] = self.board.pop(
                            (x_pos, gunk_row))
                # move that row down to the landing row

                landing_row -= 1
            gunk_row -= 1

        self.amount_of_levels_cleared = len(deleted_rows)
        self.score_manager.score(self.amount_of_levels_cleared)

    def play(self):
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
            self.clear_lines(self.piece)
            self.init_random_piece()

            if any(
                block in self.board
                for block in self.piece.square_positions()
            ):
                return False
        else:
            self.move_piece_down()

        return True
