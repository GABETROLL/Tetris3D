import random
from dataclasses import dataclass

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
      "####",
      "    ",
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
# Pieces data. Line-by-line data of piece's squares. Start positions and colors.

ROWS = 20
COLUMNS = 10

LEFT = "l"
RIGHT = "r"
HARD_DROP = "h"
SOFT_DROP = "s"


class Piece:
    """piece player can currently control. (piece data, pos)
    Must be one of these:

    I, J, L, O, S, T or Z.
    """
    def __init__(self, piece: tuple):
        piece = list(piece)
        self.pos = list(piece.pop(-2))
        self.color = piece.pop(-1)
        self.all_rotations = piece
        self.rotation = 0

    @property
    def piece(self):
        return self.all_rotations[self.rotation]

    def square_positions(self):
        """
        Returns the list of the OBJECTIVE position all the squares of
        'self', the tetromino.
        """
        positions = []

        for ri, row in enumerate(self.piece):
            for ci, square in enumerate(row):

                if square == "#":
                    position = (self.pos[0] + ci, self.pos[1] + ri)
                    positions.append(position)
        return positions


@dataclass
class Score:
    points: int = 0
    lines: int = 0
    level: int = 0
    transitioned: bool = False

    def score(self, cleared_lines: int):
        """Adds points for each line cleared and goes up levels."""
        score_per_line = 0, 40, 100, 300, 1200
        transitions = {level: (level + 1) * 10 for level in range(8 + 1)} | \
                      {level: 100 for level in range(9, 15 + 1)} | \
                      {level: (level + 50) * 10 for level in range(16, 24 + 1)} | \
                      {level: 200 for level in range(25, 28 + 1)}

        self.points += (self.level + 1) * score_per_line[cleared_lines]
        next_lines = self.lines + cleared_lines

        if self.transitioned and 0 in (n % 10 for n in range(self.lines + 1, next_lines + 1)) and cleared_lines:
            # If we passed or are in a multiple of 10 after transition...
            # print(n % 10 for n in range(self.lines, next_lines))
            # print("HI")
            self.level += 1

        elif self.lines < transitions[self.level] <= next_lines:
            # If we passed or are in a transition point...
            self.level += 1
            self.transitioned = True
            # NES Tetris rules. :)

        self.lines = next_lines


class Board:
    def __init__(self):
        self.pieces = [I, J, L, O, S, T, Z]
        self.init_random_piece()

        self.score_manager = Score()

        self.board = {}
        # {pos: color}

    def init_random_piece(self):
        self.piece = Piece(random.choice(self.pieces))

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
        self.piece.rotation = abs(self.piece.rotation % len(self.piece.all_rotations))
        # Loops trough rotations in self.complete piece.

        # Uses mod operator to loop through piece rotations,
        # absolutes value in case they rotated counter-clockwise

    def try_rotate(self, clockwise=True):
        """Tries to rotate. If the piece is inside a wall, it tries pushing it out.
        If it can't move there, it cancels the rotation."""
        self.rotate(clockwise)

        for x_pos, y_pos in self.piece.square_positions():
            if x_pos > COLUMNS - 1:
                if not self.try_move("l"):
                    self.rotate(not clockwise)

            elif x_pos < 0:
                if not self.try_move("r"):
                    self.rotate(not clockwise)

            if y_pos > ROWS - 1:
                if not self.try_move_up():
                    self.rotate(not clockwise)

            if (x_pos, y_pos) in self.board:
                self.rotate(not clockwise)
            # If the square is outside the board, we try to push it back in.
            # If we can't, we cancel the rotation.

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

    def clear_lines(self, previous_piece: Piece):
        # time: O(n), where n is: height of piece
        # space: O(n), where n is: height of piece
        deleted_rows = set()

        for y_pos, row in zip(range(len(previous_piece.piece), 0, -1), previous_piece.piece):
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
        # lowest deleted row is where all the rows with gunk in them will 'land' on.

        gunk_row = landing_row - 1
        while gunk_row > -1:
            if not (gunk_row in deleted_rows):
                # if row has gunk in it
                for x_pos in range(COLUMNS):
                    if (x_pos, gunk_row) in self.board:
                        self.board[(x_pos, landing_row)] = self.board.pop((x_pos, gunk_row))
                # move that row down to the landing row

                landing_row -= 1
            gunk_row -= 1

        self.score_manager.score(len(deleted_rows))

    def play(self):
        self.landing_handler()
        self.move_piece_down()
