import random

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


class Board:
    def __init__(self):
        self.pieces = [I, J, L, O, S, T, Z]
        self.init_random_piece()

        self.board = {}
        # {pos: color}

    def init_random_piece(self):
        self.piece = Piece(random.choice(self.pieces))

    def move_piece_down(self):
        self.piece.pos[1] += 1

    def try_move(self, move):
        """Tries to move piece down.

        Moves can be: LEFT, RIGHT, SOFT_DROP or HARD_DROP."""

        if move == "l":
            will_move = True

            for ri, row in enumerate(self.piece.piece):
                for ci, square in enumerate(row):

                    if square == "#":
                        xpos, ypos = (self.piece.pos[0] + ci, self.piece.pos[1] + ri)

                        if self.board.get((xpos - 1, ypos)) or \
                                xpos == 0:
                            will_move = False

            if will_move:
                self.piece.pos[0] -= 1

            return will_move

        elif move == "r":
            will_move = True

            for ri, row in enumerate(self.piece.piece):
                for ci, square in enumerate(row):

                    if square == "#":
                        xpos, ypos = (self.piece.pos[0] + ci, self.piece.pos[1] + ri)

                        if self.board.get((xpos + 1, ypos)) or\
                                xpos == COLUMNS - 1:
                            will_move = False

            if will_move:
                self.piece.pos[0] += 1

            return will_move
        # If the piece has a square or the wall left or right of one of its squares,
        # We can't move there.

        elif move == "h":
            # If the move is a hard drop,
            while not self.landed():
                self.move_piece_down()
            return True
            # We move the piece down until it lands.

        elif move == "s" and not self.landed():
            # Id the move is a soft drop and we haven't landed,
            self.move_piece_down()
            return True
            # We move down once.

    def set_down(self):
        """Makes piece inbeded in board."""

        for ri, row in zip(range(self.piece.pos[1], self.piece.pos[1] + len(self.piece.piece)), self.piece.piece):
            for ci, square in zip(range(self.piece.pos[0], self.piece.pos[0] + len(row)), row):
                # We iterate over both the positions of the squares in the piece
                # Based on it's position and each square,
                # row by row, column by column,

                if square == "#":
                    self.board[(ci, ri)] = self.piece.color
                    # And append the squares to the board.

    def try_move_up(self):
        """Moves up unless a square above it blocks it."""
        for ri, row in enumerate(self.piece.piece):
            for ci, square in enumerate(row):
                xpos, ypos = (self.piece.pos[0] + ci, self.piece.pos[1] + ri)

                if square == "#" and self.board.get((xpos, ypos - 1)):
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

        for ri, row in enumerate(self.piece.piece):
            for ci, square in enumerate(row):
                # Look at each square
                if square == "#":
                    xpos, ypos = (self.piece.pos[0] + ci, self.piece.pos[1] + ri)

                    if xpos > COLUMNS - 1:
                        if not self.try_move("l"):
                            self.rotate(not clockwise)

                    elif xpos < 0:
                        if not self.try_move("r"):
                            self.rotate(not clockwise)

                    if ypos > ROWS - 1:
                        if not self.try_move_up():
                            self.rotate(not clockwise)

                    # If the square is outside the board, we try to push it back in.
                    # If we can't, we cancel the rotation.

    def landed(self):
        """Checks if the piece landed."""
        for ypos, row in zip(range(len(self.piece.piece), 0, -1), self.piece.piece):
            for xpos, square in enumerate(row):
                # Check every square in the piece from the bottom to top rows.

                if square == "#":
                    # If that square is full...
                    square_pos = (self.piece.pos[0] + xpos, self.piece.pos[1] + len(self.piece.piece) - ypos)
                    if self.board.get((square_pos[0], square_pos[1] + 1)) or\
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
            self.clear_handler(self.piece)
            self.init_random_piece()

    def clear_handler(self, previous_piece):
        # time: O(n), where n is: height of piece
        # space: O(n), where n is: height of piece
        deleted_rows = set()

        for ypos, row in zip(range(len(previous_piece.piece), 0, -1), previous_piece.piece):
            # look at each row in the dropped piece
            square_y_pos = self.piece.pos[1] + len(self.piece.piece) - ypos

            for xpos in range(COLUMNS):
                print(xpos)
                if not ((xpos, square_y_pos) in self.board):
                    print(f"{(xpos), square_y_pos} WAS NOT FULL!")
                    print(self.board)
                    break
            else:
                print(f"{square_y_pos} WAS FULL!!")
                # If the whole row in the board is filled
                for xpos in range(COLUMNS):
                    self.board.pop((xpos, square_y_pos))
                # remove that row
                deleted_rows.add(square_y_pos)
                # keep track of that row
        print(deleted_rows)

        landing_row = 0
        for row in deleted_rows:
            if row > landing_row:
                landing_row = row
        # lowest deleted row is where all of the rows with gunk in them will 'land' on.

        gunk_row = landing_row - 1
        while gunk_row > -1:
            if not (gunk_row in deleted_rows):
                # if row has gunk in it
                for xpos in range(COLUMNS):
                    if (xpos, gunk_row) in self.board:
                        self.board[(xpos, landing_row)] = self.board.pop((xpos, gunk_row))
                # move that row down to the landing row

                landing_row -= 1
            gunk_row -= 1

    def play(self):
        self.landing_handler()
        self.move_piece_down()
